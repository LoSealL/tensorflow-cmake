# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
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
"""AST manipulation utilities."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import ast

import collections
import gast

from tensorflow.contrib.autograph.pyct import anno
from tensorflow.contrib.autograph.pyct import parser


class CleanCopier(object):
  """NodeTransformer-like visitor that copies an AST."""

  def __init__(self, preserve_annos):
    super(CleanCopier, self).__init__()
    self.preserve_annos = preserve_annos

  def copy(self, node):
    """Returns a deep copy of node (excluding some fields, see copy_clean)."""

    if isinstance(node, list):
      return [self.copy(n) for n in node]
    elif isinstance(node, tuple):
      return tuple(self.copy(n) for n in node)
    elif not isinstance(node, (gast.AST, ast.AST)):
      # Assuming everything that's not an AST, list or tuple is a value type
      # and may simply be assigned.
      return node

    assert isinstance(node, (gast.AST, ast.AST))

    new_fields = {}
    for f in node._fields:
      if not f.startswith('__') and hasattr(node, f):
        new_fields[f] = self.copy(getattr(node, f))
    new_node = type(node)(**new_fields)

    if self.preserve_annos:
      for k in self.preserve_annos:
        anno.copyanno(node, new_node, k)
    return new_node


def copy_clean(node, preserve_annos=None):
  """Creates a deep copy of an AST.

  The copy will not include fields that are prefixed by '__', with the
  exception of user-specified annotations.

  Args:
    node: ast.AST
    preserve_annos: Optional[Set[Hashable]], annotation keys to include in the
        copy
  Returns:
    ast.AST
  """
  return CleanCopier(preserve_annos).copy(node)


class SymbolRenamer(gast.NodeTransformer):
  """Transformer that can rename symbols to a simple names."""

  def __init__(self, name_map):
    self.name_map = name_map

  def _process(self, node):
    qn = anno.getanno(node, anno.Basic.QN)
    if qn in self.name_map:
      new_node = gast.Name(str(self.name_map[qn]), node.ctx, None)
      # All annotations get carried over.
      for k in anno.keys(node):
        anno.copyanno(node, new_node, k)
      return new_node
    return self.generic_visit(node)

  def visit_Name(self, node):
    return self._process(node)

  def visit_Attribute(self, node):
    if anno.hasanno(node, anno.Basic.QN):
      return self._process(node)
    # Attributes of dynamic objects will not have a QN.
    return self.generic_visit(node)


def rename_symbols(node, name_map):
  """Renames symbols in an AST. Requires qual_names annotations."""
  renamer = SymbolRenamer(name_map)
  if isinstance(node, list):
    return [renamer.visit(n) for n in node]
  elif isinstance(node, tuple):
    return tuple(renamer.visit(n) for n in node)
  return renamer.visit(node)


def keywords_to_dict(keywords):
  """Converts a list of ast.keyword objects to a dict."""
  keys = []
  values = []
  for kw in keywords:
    keys.append(gast.Str(kw.arg))
    values.append(kw.value)
  return gast.Dict(keys=keys, values=values)


class PatternMatcher(gast.NodeVisitor):
  """Matches a node against a pattern represented by a node."""

  def __init__(self, pattern):
    self.pattern = pattern
    self.pattern_stack = []
    self.matches = True

  def compare_and_visit(self, node, pattern):
    self.pattern_stack.append(self.pattern)
    self.pattern = pattern
    self.generic_visit(node)
    self.pattern = self.pattern_stack.pop()

  def no_match(self):
    self.matches = False
    return False

  def is_wildcard(self, p):
    if isinstance(p, (list, tuple)) and len(p) == 1:
      p, = p
    if isinstance(p, gast.Name) and p.id == '_':
      return True
    if p == '_':
      return True
    return False

  def generic_visit(self, node):
    if not self.matches:
      return

    pattern = self.pattern
    for f in node._fields:
      if f.startswith('__'):
        continue

      if not hasattr(node, f):
        if hasattr(pattern, f) and getattr(pattern, f):
          return self.no_match()
        else:
          continue
      if not hasattr(pattern, f):
        return self.no_match()

      v = getattr(node, f)
      p = getattr(pattern, f)

      if self.is_wildcard(p):
        continue
      if isinstance(v, (list, tuple)):
        if not isinstance(p, (list, tuple)) or len(v) != len(p):
          return self.no_match()
        for v_item, p_item in zip(v, p):
          self.compare_and_visit(v_item, p_item)
      elif isinstance(v, (gast.AST, ast.AST)):
        if not isinstance(v, type(p)) and not isinstance(p, type(v)):
          return self.no_match()
        self.compare_and_visit(v, p)
      else:
        # Assume everything else is a value type.
        if v != p:
          return self.no_match()

def matches(node, pattern):
  """Basic pattern matcher for AST.

  The pattern may contain wildcards represented by the symbol '_'. A node
  matches a pattern if for every node in the tree, either there is a node of
  the same type in pattern, or a Name node with id='_'.

  Args:
    node: ast.AST
    pattern: ast.AST
  Returns:
    bool
  """
  if isinstance(pattern, str):
    pattern = parser.parse_expression(pattern)
  matcher = PatternMatcher(pattern)
  matcher.visit(node)
  return matcher.matches


# TODO(mdan): Once we have error tracing, we may be able to just go to SSA.
def apply_to_single_assignments(targets, values, apply_fn):
  """Applies a function to each individual assignment.

  This function can process a possibly-unpacked (e.g. a, b = c, d) assignment.
  It tries to break down the unpacking if possible. In effect, it has the same
  effect as passing the assigned values in SSA form to apply_fn.

  Examples:

  The following will result in apply_fn(a, c), apply_fn(b, d):

      a, b = c, d

  The following will result in apply_fn(a, c[0]), apply_fn(b, c[1]):

      a, b = c

  The following will result in apply_fn(a, (b, c)):

      a = b, c

  It uses the visitor pattern to allow subclasses to process single
  assignments individually.

  Args:
    targets: Union[List[ast.AST, ...], Tuple[ast.AST, ...], ast.AST, should be
        used with the targets field of an ast.Assign node
    values: ast.AST
    apply_fn: Callable[[ast.AST, ast.AST], None], called with the
        respective nodes of each single assignment
  """
  if not isinstance(targets, (list, tuple)):
    targets = (targets,)
  for target in targets:
    if isinstance(target, (gast.Tuple, gast.List)):
      for i in range(len(target.elts)):
        target_el = target.elts[i]
        if isinstance(values, (gast.Tuple, gast.List)):
          value_el = values.elts[i]
        else:
          idx = parser.parse_expression(str(i))
          value_el = gast.Subscript(values, gast.Index(idx), ctx=gast.Load())
        apply_to_single_assignments(target_el, value_el, apply_fn)
    else:
      apply_fn(target, values)


def iter_fields(node):
  for field in sorted(node._fields):
    try:
      yield getattr(node, field)
    except AttributeError:
      pass


def iter_child_nodes(node):
  for field in iter_fields(node):
    if isinstance(field, gast.AST):
      yield field
    elif isinstance(field, list):
      for item in field:
        if isinstance(item, gast.AST):
          yield item


def parallel_walk(node_a, node_b):
  todo_a = collections.deque([node_a])
  todo_b = collections.deque([node_b])
  while todo_a and todo_b:
    node_a = todo_a.popleft()
    node_b = todo_b.popleft()
    todo_a.extend(iter_child_nodes(node_a))
    todo_b.extend(iter_child_nodes(node_b))
    yield node_a, node_b
