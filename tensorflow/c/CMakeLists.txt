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
# tf_c_framework library
########################################################
set(tf_c_srcs
    "${CMAKE_CURRENT_SOURCE_DIR}/c_api.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/c_api.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/c_api_function.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/eager/c_api.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/eager/c_api.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/eager/c_api_debug.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/eager/tape.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/checkpoint_reader.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/checkpoint_reader.h"
    "${CMAKE_CURRENT_SOURCE_DIR}/tf_status_helper.cc"
    "${CMAKE_CURRENT_SOURCE_DIR}/tf_status_helper.h"
)

add_library(tf_c OBJECT ${tf_c_srcs})
add_dependencies(
  tf_c
  tf_cc_framework
  tf_cc_while_loop
  tf_core_lib
  tf_protos_cc)

set_target_properties(tf_c PROPERTIES FOLDER "c")
