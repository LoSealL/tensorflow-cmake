"""Checkpointable data structures."""
# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import six

from tensorflow.python.ops import variables
from tensorflow.python.training.checkpointable import base
from tensorflow.python.training.checkpointable import layer_utils


class NoDependency(object):
  """Allows attribute assignment to `Checkpointable` objects with no dependency.

  Example usage:
  ```python
  obj = Checkpointable()
  obj.has_dependency = tf.Variable(0., name="dep")
  obj.no_dependency = NoDependency(tf.Variable(1., name="nodep"))
  assert obj.no_dependency.name == "nodep:0"
  ```

  `obj` in this example has a dependency on the variable "dep", and both
  attributes contain un-wrapped `Variable` objects.

  `NoDependency` also works with `tf.keras.Model`, but only for checkpoint
  dependencies: wrapping a `Layer` in `NoDependency` will assign the (unwrapped)
  `Layer` to the attribute without a checkpoint dependency, but the `Model` will
  still track the `Layer` (so it will appear in `Model.layers`, and its
  variables will appear in `Model.variables`).
  """

  def __init__(self, value):
    self.value = value


def _wrap_or_unwrap(value):
  """Wraps basic data structures, unwraps NoDependency objects."""
  if isinstance(value, NoDependency):
    return value.value
  if isinstance(value, base.CheckpointableBase):
    return value  # Skip conversion for already checkpointable objects.
  elif isinstance(value, list):
    return _ListWrapper(value)
  else:
    return value
  # TODO(allenl): Handle other common data structures. Tuples will require
  # special casing (tuple subclasses are not weak referenceable, so replacement
  # with a wrapper that subclasses tuple on attribute assignment works poorly,
  # and replacement with a wrapper that isn't a tuple is also problematic),
  # probably a tree traversal where the leaves are non-tuples(/namedtuples) to
  # come up with names. Dictionaries should look like lists.


def sticky_attribute_assignment(checkpointable, name, value):
  """Adds dependencies, generally called from __setattr__.

  This behavior is shared between Checkpointable and Model.

  Respects NoDependency indicators, but otherwise makes checkpointable objects
  out of common data structures and tracks objects by their attribute names.

  Args:
    checkpointable: The object to add dependencies to (generally the one having
      an attribute assigned).
    name: The attribute name being assigned.
    value: The value being assigned. Not necessarily a checkpointable object.

  Returns:
    The value which should be stored in the attribute (unwrapped from a
    NoDependency object if necessary).
  """
  if isinstance(value, NoDependency):
    add_dependency = False
  else:
    add_dependency = True
  value = _wrap_or_unwrap(value)
  if not add_dependency:
    return value
  if isinstance(value, base.CheckpointableBase):
    checkpointable._track_checkpointable(  # pylint: disable=protected-access
        value, name=name,
        # Allow the user to switch the Checkpointable which is tracked by this
        # name, since assigning a new variable to an attribute has
        # historically been fine (e.g. Adam did this).
        overwrite=True)
  return value


class CheckpointableDataStructure(base.CheckpointableBase):
  """Base class for data structures which contain checkpointable objects."""

  def __init__(self):
    # An append-only ordered set
    self._layers = []

    self.trainable = True
    self._extra_variables = []

  def _track_value(self, value, name):
    """Add a dependency on `value`."""
    value = sticky_attribute_assignment(
        checkpointable=self, value=value, name=name)
    if isinstance(value, variables.Variable):
      self._extra_variables.append(value)
    if not isinstance(value, base.CheckpointableBase):
      raise ValueError(
          ("Only checkpointable objects (such as Layers or Optimizers) may be "
           "stored in a List object. Got %s, which does not inherit from "
           "CheckpointableBase.") % (value,))
    if (isinstance(value, CheckpointableDataStructure)
        or layer_utils.is_layer(value)):
      # Check for object-identity rather than with __eq__ to avoid
      # de-duplicating empty container types. Automatically generated list
      # wrappers keep things like "[] == []" true, which means "[] in [[]]" is
      # also true. This becomes not true once one of the lists is mutated.
      if not any((layer is value for layer in self._layers)):
        self._layers.append(value)
        if hasattr(value, "_use_resource_variables"):
          # In subclassed models, legacy layers (tf.layers) must always use
          # resource variables.
          value._use_resource_variables = True  # pylint: disable=protected-access
    return value

  @property
  def layers(self):
    return layer_utils.filter_empty_layer_containers(self._layers)

  @property
  def trainable_weights(self):
    return layer_utils.gather_trainable_weights(
        trainable=self.trainable,
        sub_layers=self.layers,
        extra_variables=self._extra_variables)

  @property
  def non_trainable_weights(self):
    return layer_utils.gather_non_trainable_weights(
        trainable=self.trainable,
        sub_layers=self.layers,
        extra_variables=self._extra_variables)

  @property
  def weights(self):
    return self.trainable_weights + self.non_trainable_weights

  @property
  def trainable_variables(self):
    return self.trainable_weights

  @property
  def non_trainable_variables(self):
    return self.non_trainable_weights

  @property
  def variables(self):
    return self.weights

  @property
  def updates(self):
    """Aggregate updates from any `Layer` instances."""
    # Updates and conditional losses are forwarded as-is rather than being
    # filtered based on inputs, since this is just a container and won't ever
    # have any inputs.
    aggregated = []
    for layer in self.layers:
      aggregated += layer.updates
    return aggregated

  @property
  def losses(self):
    """Aggregate losses from any `Layer` instances."""
    aggregated = []
    for layer in self.layers:
      aggregated += layer.losses
    return aggregated

  def __hash__(self):
    # Support object-identity hashing, so these structures can be used as keys
    # in sets/dicts.
    return id(self)

  def __eq__(self, other):
    # Similar to Tensors, checkpointable data structures use object-identity
    # equality to support set/dict membership.
    return self is other


class List(CheckpointableDataStructure, collections.Sequence):
  """An append-only sequence type which is checkpointable.

  Maintains checkpoint dependencies on its contents (which must also be
  checkpointable), and forwards any `Layer` metadata such as updates and losses.

  Note that `List` is purely a container. It lets a `tf.keras.Model` or
  other checkpointable object know about its contents, but does not call any
  `Layer` instances which are added to it. To indicate a sequence of `Layer`
  instances which should be called sequentially, use `tf.keras.Sequential`.

  Example usage:
  ```python
  class HasList(tf.keras.Model):

    def __init__(self):
      super(HasList, self).__init__()
      self.layer_list = tf.contrib.checkpoint.List([layers.Dense(3)])
      self.layer_list.append(layers.Dense(4))

    def call(self, x):
      aggregation = 0.
      for l in self.layer_list:
        x = l(x)
        aggregation += tf.reduce_sum(x)
      return aggregation
  ```

  This kind of wrapping is necessary because `Checkpointable` objects do not
  (yet) deeply inspect regular Python data structures, so for example assigning
  a regular list (`self.layer_list = [layers.Dense(3)]`) does not create a
  checkpoint dependency and does not add the `Layer` instance's weights to its
  parent `Model`.
  """

  def __init__(self, *args, **kwargs):
    """Construct a new sequence. Arguments are passed to `list()`."""
    super(List, self).__init__()
    self._storage = self._make_storage(*args, **kwargs)
    for index, element in enumerate(self._storage):
      self._storage[index] = self._track_value(
          element, name=self._name_element(index))

  def _make_storage(self, *args, **kwargs):
    """Determines the backing storage (overridden in subclasses)."""
    return list(*args, **kwargs)

  def _name_element(self, index):
    return "%d" % (index,)

  def append(self, value):
    """Add a new checkpointable value."""
    value = self._track_value(value, self._name_element(len(self._storage)))
    self._storage.append(value)

  def extend(self, values):
    """Add a sequence of checkpointable values."""
    for value in values:
      self._storage.append(self._track_value(
          value, name=self._name_element(len(self._storage))))

  def __iadd__(self, values):
    self.extend(values)
    return self

  def __add__(self, other):
    if isinstance(other, List):
      return self.__class__(self._storage + other._storage)  # pylint: disable=protected-access
    else:
      return self.__class__(self._storage + other)

  def __radd__(self, other):
    return self + other

  def __getitem__(self, key):
    return self._storage[key]

  def __len__(self):
    return len(self._storage)

  def __repr__(self):
    return "List(%s)" % (repr(self._storage),)


class _ListWrapper(List, collections.MutableSequence,
                   # Shadowed, but there for isinstance checks.
                   list):
  """Wraps the built-in `list` to support restore-on-create for variables.

  Unlike `List`, this sequence type is mutable in the same ways built-in lists
  are. Instead of throwing an error immediately like `List`, it records
  problematic mutations (e.g. assigning a new element to a position already
  occupied, meaning both elements get the same names at different times) and
  refuses to save.

  On assignment to an attribute of a Model or Checkpointable object, Python
  lists are replaced with _ListWrapper. Wrapping a list in a
  `tf.contrib.checkpoint.NoDependency` object prevents this.
  """

  def __init__(self, wrapped_list):
    """Construct a new list wrapper.

    Args:
      wrapped_list: The initial value of the data structure. A shallow copy may
        be maintained for error checking. `wrapped_list` itself should not be
        modified directly after constructing the `_ListWrapper`, and if changes
        are detected the `_ListWrapper` will throw an exception on save.
    """
    # Monotonic flags which indicate this object would not be restored properly,
    # and therefore should throw an error on save to avoid giving the impression
    # that restoring it will work.
    self._non_append_mutation = False
    self._external_modification = False
    super(_ListWrapper, self).__init__(wrapped_list)
    self._last_wrapped_list_snapshot = list(self._storage)

  def _make_storage(self, wrapped_list):
    """Use the user's original list for storage."""
    return wrapped_list

  def _check_external_modification(self):
    """Checks for any changes to the wrapped list not through the wrapper."""
    if self._external_modification or self._non_append_mutation:
      return
    if self._storage != self._last_wrapped_list_snapshot:
      self._external_modification = True
      self._last_wrapped_list_snapshot = None

  def _update_snapshot(self):
    """Acknowledges tracked changes to the wrapped list."""
    if self._external_modification or self._non_append_mutation:
      return
    self._last_wrapped_list_snapshot = list(self._storage)

  @property
  def _checkpoint_dependencies(self):
    self._check_external_modification()
    if self._non_append_mutation:
      raise ValueError(
          ("Unable to save the object %s (a list wrapper constructed to track "
           "checkpointable TensorFlow objects). A list element was replaced "
           "(__setitem__), deleted, or inserted. In order to support "
           "restoration on object creation, tracking is exclusively for "
           "append-only data structures.\n\nIf you don't need this list "
           "checkpointed, wrap it in a tf.contrib.checkpoint.NoDependency "
           "object; it will be automatically un-wrapped and subsequently "
           "ignored." % (self,)))
    if self._external_modification:
      raise ValueError(
          ("Unable to save the object %s (a list wrapper constructed to track "
           "checkpointable TensorFlow objects). The wrapped list was modified "
           "outside the wrapper (its final value was %s, its value when a "
           "checkpoint dependency was added was %s), which breaks restoration "
           "on object creation.\n\nIf you don't need this list checkpointed, "
           "wrap it in a tf.contrib.checkpoint.NoDependency object; it will be "
           "automatically un-wrapped and subsequently ignored." % (
               self, self._storage, self._last_wrapped_list_snapshot)))
    return super(_ListWrapper, self)._checkpoint_dependencies

  def __delitem__(self, key):
    self._non_append_mutation = True
    del self._storage[key]

  def __setitem__(self, key, value):
    self._non_append_mutation = True
    self._storage[key] = value

  def append(self, value):
    """Add a new checkpointable value."""
    self._check_external_modification()
    super(_ListWrapper, self).append(value)
    self._update_snapshot()

  def extend(self, values):
    """Add a sequence of checkpointable values."""
    self._check_external_modification()
    super(_ListWrapper, self).extend(values)
    self._update_snapshot()

  def __eq__(self, other):
    return self._storage == getattr(other, "_storage", other)

  def __ne__(self, other):
    return self._storage != getattr(other, "_storage", other)

  def __lt__(self, other):
    return self._storage < getattr(other, "_storage", other)

  def __le__(self, other):
    return self._storage <= getattr(other, "_storage", other)

  def __gt__(self, other):
    return self._storage > getattr(other, "_storage", other)

  def __ge__(self, other):
    return self._storage >= getattr(other, "_storage", other)

  def __hash__(self):
    # List wrappers need to compare like regular lists, and so like regular
    # lists they don't belong in hash tables.
    raise TypeError("unhashable type: 'ListWrapper'")

  def insert(self, index, obj):
    self._non_append_mutation = True
    self._storage.insert(index, obj)

  def _track_value(self, value, name):
    """Allows storage of non-checkpointable objects."""
    try:
      value = super(_ListWrapper, self)._track_value(value=value, name=name)
    except ValueError:
      # Even if this value isn't checkpointable, we need to make sure
      # NoDependency objects get unwrapped.
      value = sticky_attribute_assignment(
          checkpointable=self, value=value, name=name)
    return value

  def __repr__(self):
    return "ListWrapper(%s)" % (repr(self._storage),)


class Mapping(CheckpointableDataStructure, collections.Mapping):
  """An append-only checkpointable mapping data structure with string keys.

  Maintains checkpoint dependencies on its contents (which must also be
  checkpointable), named based on its keys.

  Note that once a key has been added, it may not be deleted or replaced. If
  names may not be unique, see `tf.contrib.checkpoint.UniqueNameTracker`.
  """

  def __init__(self, *args, **kwargs):
    """Construct a new sequence. Arguments are passed to `dict()`."""
    super(Mapping, self).__init__()
    self._storage = dict(*args, **kwargs)
    self._storage.update(
        {key: self._track_value(
            value, name=self._name_element(key))
         for key, value in self._storage.items()})

  def _name_element(self, key):
    if not isinstance(key, six.string_types):
      raise TypeError(
          "Mapping accepts only string keys, but got a key %s."
          % repr(key))
    return str(key)

  def __setitem__(self, key, value):
    name = self._name_element(key)
    value = self._track_value(value, name=name)
    current_value = self._storage.setdefault(key, value)
    if current_value is not value:
      raise ValueError(
          ("Mappings are an append-only data structure. Tried to overwrite the "
           "key '%s' with value %s, but it already contains %s")
          % (key, value, current_value))

  def update(self, *args, **kwargs):
    for key, value in dict(*args, **kwargs).items():
      self[key] = value

  def __getitem__(self, key):
    return self._storage[key]

  def __len__(self):
    return len(self._storage)

  def __repr__(self):
    return "Mapping(%s)" % (repr(self._storage),)

  def __iter__(self):
    return iter(self._storage)
