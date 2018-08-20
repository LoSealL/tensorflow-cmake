### TensorFlow CMake for Windows
Because beyond tensorflow `r1.11`, tensorflow officially drop CMake build files, and support only bazel, so I personally try to maintain a cmake build scripts for tensorflow.

### Environment
The following lists prerequisite softwares and libraries:
- python3 (v3.6 in *Anaconda* is recommended)
- cmake >= 3.8.1
- git
- cuda 9.0
- cudnn 7.0
- swig*

The following lists prerequisite pip packages:
- absl-py >= 0.2.2
- protobuf >= 3.6.0
- numpy
- six
- setuptools
- wheel

Compilers (tested by me):
- VS 2015 (vc14), or
- VS 2017 (vc15)

*Swig is pre-downloaded into `./tools`

### File Re-organized

The original cmake files are all in the `./tensorflow/contrib/cmake`, it's better to add `CMakeLists.txt` to each sub-folders

-----

THANKS TO ALL THE CONTRIBUTORS TO CMAKE SCRIPTS