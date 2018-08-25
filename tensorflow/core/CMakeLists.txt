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

########################################################
# tf_protos_cc library
########################################################

file(GLOB_RECURSE tf_protos_cc_srcs RELATIVE ${tensorflow_SOURCE_DIR}
    "${tensorflow_SOURCE_DIR}/tensorflow/core/*.proto"
    "${tensorflow_SOURCE_DIR}/tensorflow/compiler/xla/*.proto"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/proto/*.proto"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tpu/proto/*.proto"
)

RELATIVE_PROTOBUF_GENERATE_CPP(PROTO_SRCS PROTO_HDRS
    ${tensorflow_SOURCE_DIR} ${tf_protos_cc_srcs}
)


set(PROTO_TEXT_EXE "proto_text")
set(tf_proto_text_srcs
    "tensorflow/core/example/example.proto"
    "tensorflow/core/example/feature.proto"
    "tensorflow/core/framework/allocation_description.proto"
    "tensorflow/core/framework/attr_value.proto"
    "tensorflow/core/framework/cost_graph.proto"
    "tensorflow/core/framework/device_attributes.proto"
    "tensorflow/core/framework/function.proto"
    "tensorflow/core/framework/graph.proto"
    "tensorflow/core/framework/graph_transfer_info.proto"
    "tensorflow/core/framework/kernel_def.proto"
    "tensorflow/core/framework/log_memory.proto"
    "tensorflow/core/framework/node_def.proto"
    "tensorflow/core/framework/op_def.proto"
    "tensorflow/core/framework/remote_fused_graph_execute_info.proto"
    "tensorflow/core/framework/resource_handle.proto"
    "tensorflow/core/framework/step_stats.proto"
    "tensorflow/core/framework/summary.proto"
    "tensorflow/core/framework/tensor.proto"
    "tensorflow/core/framework/tensor_description.proto"
    "tensorflow/core/framework/tensor_shape.proto"
    "tensorflow/core/framework/tensor_slice.proto"
    "tensorflow/core/framework/types.proto"
    "tensorflow/core/framework/versions.proto"
    "tensorflow/core/lib/core/error_codes.proto"
    "tensorflow/core/protobuf/cluster.proto"
    "tensorflow/core/protobuf/config.proto"
    "tensorflow/core/protobuf/debug.proto"
    "tensorflow/core/protobuf/device_properties.proto"
    "tensorflow/core/protobuf/rewriter_config.proto"
    "tensorflow/core/protobuf/tensor_bundle.proto"
    "tensorflow/core/protobuf/saver.proto"
    "tensorflow/core/util/memmapped_file_system.proto"
    "tensorflow/core/util/saved_tensor_slice.proto"
)
RELATIVE_PROTOBUF_TEXT_GENERATE_CPP(PROTO_TEXT_SRCS PROTO_TEXT_HDRS
    ${tensorflow_SOURCE_DIR} ${tf_proto_text_srcs}
)

if(WIN32)
  add_library(tf_protos_cc ${PROTO_SRCS} ${PROTO_HDRS})
else()
  file(GLOB_RECURSE tf_protos_grpc_cc_srcs RELATIVE ${tensorflow_SOURCE_DIR}
      "${tensorflow_SOURCE_DIR}/tensorflow/core/debug/*.proto"
  )
  RELATIVE_PROTOBUF_GENERATE_GRPC_CPP(PROTO_GRPC_SRCS PROTO_GRPC_HDRS
      ${tensorflow_SOURCE_DIR} ${tf_protos_grpc_cc_srcs}
  )
  add_library(tf_protos_cc ${PROTO_GRPC_SRCS} ${PROTO_GRPC_HDRS} ${PROTO_SRCS} ${PROTO_HDRS})
endif()

########################################################
# tf_core_lib library
########################################################
file(GLOB_RECURSE tf_core_lib_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/lib/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/lib/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/public/*.h"
)

file(GLOB tf_core_platform_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/default/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/default/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/resource_handle.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/resource_handle.cc")
if (NOT tensorflow_ENABLE_GPU)
  file(GLOB tf_core_platform_gpu_srcs
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/cuda_libdevice_path.*"
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/default/cuda_libdevice_path.*")
  list(REMOVE_ITEM tf_core_platform_srcs ${tf_core_platform_gpu_srcs})
else()
  file(GLOB tf_core_platform_srcs_exclude
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/default/device_tracer.cc")
  list(REMOVE_ITEM tf_core_platform_srcs ${tf_core_platform_srcs_exclude})
endif()

list(APPEND tf_core_lib_srcs ${tf_core_platform_srcs})

if(UNIX)
  file(GLOB tf_core_platform_posix_srcs
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/posix/*.h"
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/posix/*.cc"
  )
  list(APPEND tf_core_lib_srcs ${tf_core_platform_posix_srcs})
endif(UNIX)

if(WIN32)
  file(GLOB tf_core_platform_windows_srcs
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/windows/*.h"
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/windows/*.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/posix/error.h"
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/posix/error.cc"
  )
  list(APPEND tf_core_lib_srcs ${tf_core_platform_windows_srcs})
endif(WIN32)

if (tensorflow_ENABLE_HDFS_SUPPORT)
  list(APPEND tf_core_platform_hdfs_srcs
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/hadoop/hadoop_file_system.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/hadoop/hadoop_file_system.h"
  )
  list(APPEND tf_core_lib_srcs ${tf_core_platform_hdfs_srcs})
endif()

file(GLOB_RECURSE tf_core_lib_test_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/lib/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/lib/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/public/*test*.h"
)
list(REMOVE_ITEM tf_core_lib_srcs ${tf_core_lib_test_srcs})

add_library(tf_core_lib OBJECT ${tf_core_lib_srcs})
add_dependencies(tf_core_lib ${tensorflow_EXTERNAL_DEPENDENCIES} tf_protos_cc)

# [TODO: why necessary?] Tricky setup to force always rebuilding
# force_rebuild always runs forcing ${VERSION_INFO_CC} target to run
# ${VERSION_INFO_CC} would cache, but it depends on a phony never produced
# target.
set(VERSION_INFO_CC ${tensorflow_SOURCE_DIR}/tensorflow/core/util/version_info.cc)
add_custom_target(force_rebuild_target ALL DEPENDS ${VERSION_INFO_CC})
# add_custom_command(OUTPUT __force_rebuild COMMAND ${CMAKE_COMMAND} -E echo)
add_custom_command(OUTPUT
    ${VERSION_INFO_CC}
    COMMAND ${PYTHON_EXECUTABLE} ${tensorflow_SOURCE_DIR}/tensorflow/tools/git/gen_git_source.py
    ARGS --raw_generate ${VERSION_INFO_CC} --source_dir ${tensorflow_SOURCE_DIR} --git_tag_override=${GIT_TAG_OVERRIDE}
    # DEPENDS __force_rebuild
)
set(tf_version_srcs ${tensorflow_SOURCE_DIR}/tensorflow/core/util/version_info.cc)

########################################################
# tf_core_framework library
########################################################
file(GLOB_RECURSE tf_core_framework_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/edgeset.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/edgeset.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph_def_builder.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph_def_builder.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/node_builder.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/node_builder.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/tensor_id.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/tensor_id.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/while_context.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/while_context.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/util/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/util/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/session.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/session_factory.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/session_options.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensorboard/db/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensorboard/db/*.h"
    "${tensorflow_SOURCE_DIR}/public/*.h"
)

file(GLOB_RECURSE tf_core_framework_exclude_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/*testutil.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/*testutil.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/*main.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/framework/resource_handle.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/util/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/util/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/util/*main.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensorboard/db/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensorboard/db/loader.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensorboard/db/vacuum.cc"
)

# TODO(jart): Why doesn't this work?
# set_source_files_properties(
#     ${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensorboard/db/snapfn.cc
#     PROPERTIES COMPILE_FLAGS -DSQLITE_OMIT_LOAD_EXTENSION)

list(REMOVE_ITEM tf_core_framework_srcs ${tf_core_framework_exclude_srcs})

add_library(tf_core_framework OBJECT
    ${tf_core_framework_srcs}
    ${tf_version_srcs}
    ${PROTO_TEXT_HDRS}
    ${PROTO_TEXT_SRCS}
)
add_dependencies(tf_core_framework tf_core_lib proto_text)

########################################################
# tf_core_cpu library
########################################################
file(GLOB_RECURSE tf_core_cpu_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/cc/saved_model/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/cc/saved_model/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/debug/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/debug/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/distributed_runtime/server_lib.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/distributed_runtime/server_lib.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/*/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/*/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/public/*.h"
)

file(GLOB_RECURSE tf_core_cpu_exclude_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/cc/saved_model/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/cc/saved_model/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/*main.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/gpu/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/gpu_device_factory.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/direct_session.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/direct_session.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/session.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/session_factory.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/session_options.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/edgeset.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/edgeset.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph_def_builder.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/graph_def_builder.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/node_builder.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/node_builder.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/tensor_id.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/tensor_id.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/while_context.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/graph/while_context.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/clusters/single_machine.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/clusters/single_machine.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/inputs/trivial_test_graph_input_yielder.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/inputs/trivial_test_graph_input_yielder.cc"
)
file(GLOB_RECURSE tf_core_cpu_whitelisted_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/gpu/gpu_id.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/gpu/gpu_id.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/gpu/gpu_id_manager.cc"
)
list(REMOVE_ITEM tf_core_cpu_exclude_srcs ${tf_core_cpu_whitelisted_srcs})
list(REMOVE_ITEM tf_core_cpu_srcs ${tf_core_cpu_exclude_srcs})

if (tensorflow_ENABLE_GPU)
  file(GLOB_RECURSE tf_core_gpu_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/gpu/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/default/gpu/cupti_wrapper.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/default/device_tracer.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/gpu_device_factory.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/devices.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/devices.cc"
  )
  file(GLOB_RECURSE tf_core_gpu_exclude_srcs
     "${tensorflow_SOURCE_DIR}/tensorflow/core/*test*.cc"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/*test*.cc"
  )
  list(REMOVE_ITEM tf_core_gpu_srcs ${tf_core_gpu_exclude_srcs})
  list(REMOVE_ITEM tf_core_gpu_srcs ${tf_core_cpu_whitelisted_srcs})
  list(APPEND tf_core_cpu_srcs ${tf_core_gpu_srcs})
endif()

add_library(tf_core_cpu OBJECT ${tf_core_cpu_srcs})
add_dependencies(tf_core_cpu tf_core_framework)

########################################################
# tf_core_direct_session library
########################################################
file(GLOB tf_core_direct_session_srcs
   "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/direct_session.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/common_runtime/direct_session.h"
)

file(GLOB_RECURSE tf_core_direct_session_test_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/debug/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/debug/*test*.cc"
)

list(REMOVE_ITEM tf_core_direct_session_srcs ${tf_core_direct_session_test_srcs})

add_library(tf_core_direct_session OBJECT ${tf_core_direct_session_srcs})

add_dependencies(tf_core_direct_session tf_core_cpu)

########################################################
# tf_core_ops
########################################################

foreach(tf_op_lib_name ${tf_op_lib_names})
    ########################################################
    # tf_${tf_op_lib_name} library
    ########################################################
    file(GLOB tf_${tf_op_lib_name}_srcs
        "${tensorflow_SOURCE_DIR}/tensorflow/core/ops/${tf_op_lib_name}.cc"
    )
    
    add_library(tf_${tf_op_lib_name} OBJECT ${tf_${tf_op_lib_name}_srcs})
    
    add_dependencies(tf_${tf_op_lib_name} tf_core_framework)
    set_target_properties(tf_${tf_op_lib_name} PROPERTIES FOLDER "core/op_libs")
endforeach()

function(GENERATE_CONTRIB_OP_LIBRARY op_lib_name cc_srcs)
    add_library(tf_contrib_${op_lib_name}_ops OBJECT ${cc_srcs})
    add_dependencies(tf_contrib_${op_lib_name}_ops tf_core_framework)
    set_target_properties(tf_contrib_${op_lib_name}_ops PROPERTIES FOLDER "core/op_libs_contrib")
endfunction()

file(GLOB_RECURSE tensor_forest_hybrid_srcs
     "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/*.cc"
)

file(GLOB_RECURSE tpu_ops_srcs
     "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tpu/ops/*.cc"
)

GENERATE_CONTRIB_OP_LIBRARY(boosted_trees_model "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/model_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(boosted_trees_split_handler "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/split_handler_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(boosted_trees_training "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/training_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(boosted_trees_prediction "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/prediction_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(boosted_trees_quantiles "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/quantile_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(boosted_trees_stats_accumulator "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/stats_accumulator_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(coder "${tensorflow_SOURCE_DIR}/tensorflow/contrib/coder/ops/coder_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(data_dataset "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/ops/dataset_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(factorization_clustering "${tensorflow_SOURCE_DIR}/tensorflow/contrib/factorization/ops/clustering_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(factorization_factorization "${tensorflow_SOURCE_DIR}/tensorflow/contrib/factorization/ops/factorization_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(framework_variable "${tensorflow_SOURCE_DIR}/tensorflow/contrib/framework/ops/variable_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(input_pipeline "${tensorflow_SOURCE_DIR}/tensorflow/contrib/input_pipeline/ops/input_pipeline_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(image "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/ops/image_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(image_distort_image "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/ops/distort_image_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(image_sirds "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/ops/single_image_random_dot_stereograms_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(layers_sparse_feature_cross "${tensorflow_SOURCE_DIR}/tensorflow/contrib/layers/ops/sparse_feature_cross_op.cc")
GENERATE_CONTRIB_OP_LIBRARY(memory_stats "${tensorflow_SOURCE_DIR}/tensorflow/contrib/memory_stats/ops/memory_stats_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(nccl "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/ops/nccl_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(periodic_resample "${tensorflow_SOURCE_DIR}/tensorflow/contrib/periodic_resample/ops/array_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(nearest_neighbor "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nearest_neighbor/ops/nearest_neighbor_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(resampler "${tensorflow_SOURCE_DIR}/tensorflow/contrib/resampler/ops/resampler_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(rnn_gru "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/ops/gru_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(rnn_lstm "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/ops/lstm_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(seq2seq_beam_search "${tensorflow_SOURCE_DIR}/tensorflow/contrib/seq2seq/ops/beam_search_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(tensor_forest "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/ops/tensor_forest_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(tensor_forest_hybrid "${tensor_forest_hybrid_srcs}")
GENERATE_CONTRIB_OP_LIBRARY(tensor_forest_model "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/ops/model_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(tensor_forest_stats "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/ops/stats_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(text_skip_gram "${tensorflow_SOURCE_DIR}/tensorflow/contrib/text/ops/skip_gram_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(tpu "${tpu_ops_srcs}")
GENERATE_CONTRIB_OP_LIBRARY(bigquery_reader "${tensorflow_SOURCE_DIR}/tensorflow/contrib/cloud/ops/bigquery_reader_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(gcs_config "${tensorflow_SOURCE_DIR}/tensorflow/contrib/cloud/ops/gcs_config_ops.cc")
GENERATE_CONTRIB_OP_LIBRARY(reduce_slice_ops "${tensorflow_SOURCE_DIR}/tensorflow/contrib/reduce_slice_ops/ops/reduce_slice_ops.cc")

########################################################
# tf_user_ops library
########################################################
file(GLOB_RECURSE tf_user_ops_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/user_ops/*.cc"
)

add_library(tf_user_ops OBJECT ${tf_user_ops_srcs})

add_dependencies(tf_user_ops tf_core_framework)

########################################################
# tf_core_ops library
########################################################
file(GLOB_RECURSE tf_core_ops_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/ops/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/ops/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/user_ops/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/user_ops/*.cc"
)

file(GLOB_RECURSE tf_core_ops_exclude_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/ops/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/ops/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/ops/*main.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/user_ops/*test*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/user_ops/*test*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/user_ops/*main.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/user_ops/*.cu.cc"
)

list(REMOVE_ITEM tf_core_ops_srcs ${tf_core_ops_exclude_srcs})

add_library(tf_core_ops OBJECT ${tf_core_ops_srcs})

add_dependencies(tf_core_ops tf_core_cpu)

########################################################
# tf_debug_ops library
########################################################

file(GLOB tf_debug_ops_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/ops/debug_ops.cc"
)

add_library(tf_debug_ops OBJECT ${tf_debug_ops_srcs})

add_dependencies(tf_debug_ops tf_core_framework)

########################################################
# tf_core_kernels library
########################################################

if(tensorflow_BUILD_ALL_KERNELS)
  file(GLOB_RECURSE tf_core_kernels_srcs
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*.cc"
  )
else(tensorflow_BUILD_ALL_KERNELS)
  # Build a minimal subset of kernels to be able to run a test program.
  set(tf_core_kernels_srcs
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/bounds_check.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/constant_op.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/constant_op.cc"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/fill_functor.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/fill_functor.cc"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/matmul_op.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/matmul_op.cc"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/no_op.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/no_op.cc"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/ops_util.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/ops_util.cc"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/sendrecv_ops.h"
     "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/sendrecv_ops.cc"
  )
endif(tensorflow_BUILD_ALL_KERNELS)

if(tensorflow_BUILD_CONTRIB_KERNELS)
  set(tf_contrib_kernels_srcs
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/kernels/model_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/kernels/prediction_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/kernels/quantile_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/kernels/split_handler_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/kernels/stats_accumulator_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/kernels/training_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/utils/batch_features.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/utils/dropout_utils.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/utils/examples_iterable.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/utils/parallel_for.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/utils/sparse_column_iterable.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/utils/tensor_utils.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/learner/common/partitioners/example_partitioner.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/models/multiple_additive_trees.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/lib/trees/decision_tree.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/model_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/prediction_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/quantile_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/split_handler_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/stats_accumulator_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/boosted_trees/ops/training_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/coder/kernels/pmf_to_cdf_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/coder/kernels/range_coder.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/coder/kernels/range_coder_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/coder/kernels/range_coder_ops_util.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/coder/ops/coder_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/kernels/csv_dataset_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/kernels/directed_interleave_dataset_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/kernels/ignore_errors_dataset_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/kernels/prefetching_kernels.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/kernels/threadpool_dataset_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/kernels/unique_dataset_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/data/ops/dataset_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/factorization/kernels/clustering_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/factorization/kernels/masked_matmul_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/factorization/kernels/wals_solver_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/factorization/ops/clustering_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/factorization/ops/factorization_ops.cc"
      #"${tensorflow_SOURCE_DIR}/tensorflow/contrib/ffmpeg/decode_audio_op.cc"
      #"${tensorflow_SOURCE_DIR}/tensorflow/contrib/ffmpeg/encode_audio_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/framework/kernels/zero_initializer_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/framework/ops/variable_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/kernels/adjust_hsv_in_yiq_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/kernels/bipartite_match_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/kernels/image_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/kernels/segmentation_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/kernels/single_image_random_dot_stereograms_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/ops/distort_image_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/ops/image_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/ops/single_image_random_dot_stereograms_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/layers/kernels/sparse_feature_cross_kernel.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/layers/ops/sparse_feature_cross_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/libsvm/kernels/decode_libsvm_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/libsvm/ops/libsvm_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/kernels/nccl_manager.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/kernels/nccl_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/ops/nccl_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nearest_neighbor/kernels/hyperplane_lsh_probes.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nearest_neighbor/ops/nearest_neighbor_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/resampler/kernels/resampler_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/resampler/ops/resampler_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/kernels/blas_gemm.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/kernels/gru_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/kernels/lstm_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/ops/gru_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/ops/lstm_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/seq2seq/kernels/beam_search_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/seq2seq/ops/beam_search_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/ops/tensor_forest_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/kernels/reinterpret_string_to_float_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/kernels/scatter_add_ndim_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/kernels/tree_utils.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/hard_routing_function_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/k_feature_gradient_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/k_feature_routing_function_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/routing_function_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/routing_gradient_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/stochastic_hard_routing_function_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/stochastic_hard_routing_gradient_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/unpack_path_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tensor_forest/hybrid/core/ops/utils.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/text/kernels/skip_gram_kernels.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/text/ops/skip_gram_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tpu/ops/cross_replica_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tpu/ops/infeed_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tpu/ops/outfeed_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tpu/ops/replication_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/tpu/ops/tpu_configuration_ops.cc"
    )
  list(APPEND tf_core_kernels_srcs ${tf_contrib_kernels_srcs})
endif(tensorflow_BUILD_CONTRIB_KERNELS)

# Cloud libraries require curl and boringssl.
# Curl is not supported yet anyway so we remove for now.
file(GLOB tf_core_kernels_cloud_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/cloud/kernels/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/cloud/kernels/*.cc"
)
list(REMOVE_ITEM tf_core_kernels_srcs ${tf_core_kernels_cloud_srcs})

file(GLOB_RECURSE tf_core_kernels_exclude_srcs
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*test*.h"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*test*.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*testutil.h"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*testutil.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*test_utils.h"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*test_utils.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*main.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*.cu.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/fuzzing/*"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/hexagon/*"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/remote_fused_graph_rewriter_transform*.cc"
)
list(REMOVE_ITEM tf_core_kernels_srcs ${tf_core_kernels_exclude_srcs})

if(WIN32)
  file(GLOB_RECURSE tf_core_kernels_windows_exclude_srcs
      # not working on windows yet
      "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/neon/*"
      # not in core - those are loaded dynamically as dll
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nearest_neighbor/kernels/hyperplane_lsh_probes.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nearest_neighbor/ops/nearest_neighbor_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/resampler/kernels/resampler_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/kernels/blas_gemm.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/kernels/gru_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/kernels/lstm_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/ops/gru_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/ops/lstm_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/seq2seq/kernels/beam_search_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/seq2seq/ops/beam_search_ops.cc"
      # temporarily disable nccl (nccl itself needs to be ported to windows first)
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/kernels/nccl_manager.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/kernels/nccl_ops.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/ops/nccl_ops.cc"
  )
  list(REMOVE_ITEM tf_core_kernels_srcs ${tf_core_kernels_windows_exclude_srcs})
else(WIN32)
  if(tensorflow_ENABLE_GPU)
    file(GLOB_RECURSE tf_core_kernels_gpu_exclude_srcs
        # temporarily disable nccl as it needs to be ported with gpu
        "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/kernels/nccl_manager.cc"
        "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/kernels/nccl_ops.cc"
        "${tensorflow_SOURCE_DIR}/tensorflow/contrib/nccl/ops/nccl_ops.cc"
    )
    list(REMOVE_ITEM tf_core_kernels_srcs ${tf_core_kernels_gpu_exclude_srcs})
  endif(tensorflow_ENABLE_GPU)
endif(WIN32)

file(GLOB_RECURSE tf_core_gpu_kernels_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/*.cu.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/framework/kernels/zero_initializer_op_gpu.cu.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/image/kernels/*.cu.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/rnn/kernels/*.cu.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/seq2seq/kernels/*.cu.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/contrib/resampler/kernels/*.cu.cc"
)

if(WIN32 AND tensorflow_ENABLE_GPU)
  file(GLOB_RECURSE tf_core_kernels_cpu_only_srcs
      # GPU implementation not working on Windows yet.
      "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/matrix_diag_op.cc"
      "${tensorflow_SOURCE_DIR}/tensorflow/core/kernels/one_hot_op.cc")
  list(REMOVE_ITEM tf_core_kernels_srcs ${tf_core_kernels_cpu_only_srcs})
  add_library(tf_core_kernels_cpu_only OBJECT ${tf_core_kernels_cpu_only_srcs})
  add_dependencies(tf_core_kernels_cpu_only tf_core_cpu)
  # Undefine GOOGLE_CUDA to avoid registering unsupported GPU kernel symbols.
  get_target_property(target_compile_flags tf_core_kernels_cpu_only COMPILE_FLAGS)
  if(target_compile_flags STREQUAL "target_compile_flags-NOTFOUND")
    set(target_compile_flags "/UGOOGLE_CUDA")
  else()
    set(target_compile_flags "${target_compile_flags} /UGOOGLE_CUDA")
  endif()
  set_target_properties(tf_core_kernels_cpu_only PROPERTIES COMPILE_FLAGS ${target_compile_flags})
endif(WIN32 AND tensorflow_ENABLE_GPU)

add_library(tf_core_kernels OBJECT ${tf_core_kernels_srcs})
add_dependencies(tf_core_kernels tf_core_cpu)

if (WIN32)
  target_compile_options(tf_core_kernels PRIVATE /MP)
endif (WIN32)
if (tensorflow_ENABLE_GPU)
  set_source_files_properties(${tf_core_gpu_kernels_srcs} PROPERTIES CUDA_SOURCE_PROPERTY_FORMAT OBJ)
  set(tf_core_gpu_kernels_lib tf_core_gpu_kernels)
  cuda_add_library(${tf_core_gpu_kernels_lib} ${tf_core_gpu_kernels_srcs})
  set_target_properties(${tf_core_gpu_kernels_lib}
                        PROPERTIES DEBUG_POSTFIX ""
                        COMPILE_FLAGS "${TF_REGULAR_CXX_FLAGS}"
  )
  add_dependencies(${tf_core_gpu_kernels_lib} tf_core_cpu)
endif()

########################################################
# tf_core_profiler library
########################################################
file(GLOB_RECURSE tf_core_profiler_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/*.proto"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/tfprof_options.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/tfprof_options.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/advisor/*.h"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/advisor/*.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/platform/regexp.h"
)

file(GLOB_RECURSE tf_core_profiler_exclude_srcs
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/*test.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/advisor/*test.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/print_model_analysis.cc"
    "${tensorflow_SOURCE_DIR}/tensorflow/core/profiler/internal/print_model_analysis.h"
)
list(REMOVE_ITEM tf_core_profiler_srcs ${tf_core_profiler_exclude_srcs})

add_library(tf_core_profiler OBJECT ${tf_core_profiler_srcs})
add_dependencies(tf_core_profiler tf_core_lib)

########################################################
# tf_grappler library
########################################################
file(GLOB tf_grappler_srcs
   "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/clusters/single_machine.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/core/grappler/clusters/single_machine.h"
   "${tensorflow_SOURCE_DIR}/tensorflow/python/grappler/cost_analyzer.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/python/grappler/cost_analyzer.h"
   "${tensorflow_SOURCE_DIR}/tensorflow/python/grappler/model_analyzer.cc"
   "${tensorflow_SOURCE_DIR}/tensorflow/python/grappler/model_analyzer.h"
 )

add_library(tf_grappler OBJECT ${tf_grappler_srcs})

add_dependencies(tf_grappler tf_core_cpu)

if(tensorflow_ENABLE_GRPC_SUPPORT)
  add_subdirectory(distributed_runtime)
endif()

set(tf_core_targets
    tf_protos_cc tf_core_lib force_rebuild_target tf_core_framework
    tf_core_cpu tf_core_direct_session tf_user_ops tf_core_ops tf_debug_ops
    tf_core_kernels tf_core_profiler tf_grappler)
if(WIN32 AND tensorflow_ENABLE_GPU)
  list(APPEND tf_core_targets tf_core_kernels_cpu_only)
endif()
foreach(core_target ${tf_core_targets})
  set_target_properties(${core_target} PROPERTIES FOLDER "core")    
endforeach()
