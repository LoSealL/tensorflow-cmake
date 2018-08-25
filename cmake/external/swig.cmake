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
include (ExternalProject)

set(swig_TAG 3.0.12)
if(WIN32)
  set(swig_URL https://github.com/LoSealL/tensorflow-cmake/releases/download/swig-3.0.12/swigwin-3.0.12.zip)
  set(swig_FOLDER_NAME swigwin-${swig_TAG})
  set(swig_ARCHIVE_NAME swigwin-${swig_TAG}.zip)
  set(swig_SUFFIX .exe)
else()
  set(swig_URL https://github.com/LoSealL/tensorflow-cmake/releases/download/swig-3.0.12/swig-3.0.12.tar.gz)
  set(swig_FOLDER_NAME swigwin-${swig_TAG})
  set(swig_ARCHIVE_NAME swigwin-${swig_TAG}.tar.gz)
endif()

set(SWIG_EXECUTABLE ${CMAKE_CURRENT_BINARY_DIR}/${swig_FOLDER_NAME}/swig${swig_SUFFIX})
if(NOT EXISTS ${DOWNLOAD_LOCATION}/${swig_ARCHIVE_NAME})
  file(DOWNLOAD ${swig_URL} ${DOWNLOAD_LOCATION}/${swig_ARCHIVE_NAME} SHOW_PROGRESS)
endif()
if(NOT EXISTS ${SWIG_EXECUTABLE})
  execute_process(
      COMMAND ${CMAKE_COMMAND} -E tar xvf ${DOWNLOAD_LOCATION}/${swig_ARCHIVE_NAME})
endif()
