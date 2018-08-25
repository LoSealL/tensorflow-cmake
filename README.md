### NOTICE
The original tensorflow [readme](./README_TF.md).

### TensorFlow CMake for Windows
Because beyond tensorflow `r1.11`, tensorflow officially drop CMake build files, and support only bazel, so I personally try to maintain a cmake build scripts for tensorflow.

### Environment
The following lists prerequisite softwares and libraries:
- [python3](https://www.python.org/) (v3.6 in *Anaconda* is recommended)
- [cmake](https://cmake.org/download/) >= 3.12
- [git](https://git-scm.com/download/win)
- cuda == 9.0
- cudnn == 7.0

The following lists prerequisite pip packages:
- absl-py >= 0.2.2
- protobuf >= 3.6.0
- numpy**
- six
- setuptools
- wheel

Compilers (tested by me):
- VS 2015 (vc14), or
- VS 2017 (vc15)***

*Swig is pre-downloaded into `./_build`

**You should the same version of numpy in __BUILD__ and __USE__

***When you use the newest VS 2017, CUDA compile check may fail, to resolve this, see [here](https://github.com/LoSealL/tensorflow-cmake/wiki/Resolve-CUDA-compile-check-error-in-CMAKE)

### How to compile

Start into VS x64 prompt.

====================

```bash
> mkdir _build && cd _build
> cmake .. -A x64 -T host=x64 ^
  -DCMAKE_BUILD_TYPE=Release ^
  -DPYTHON_EXECUTABLE=%PYTHON_EXECUTABLE% ^
  -DPYTHON_LIBRARIES=%PYTHON_LIB% ^
  -Dtensorflow_ENABLE_GPU=<ON/OFF> ^
  -Dtensorflow_BUILD_SHARED_LIB=<ON/OFF> ^
  -Dtensorflow_WIN_CPU_SIMD_OPTIONS=/arch:AVX2 ^
  -Dtensorflow_ENABLE_MKL_SUPPORT=<ON/OFF> ^
  -Dtensorflow_ENABLE_MKLDNN_SUPPORT=<ON/OFF> ^
  -Dtensorflow_BUILD_PYTHON_BINDINGS=<ON/OFF> ^
  -Dtensorflow_DISABLE_EIGEN_FORCEINLINE=<ON/OFF> ^
  -Dtensorflow_ENABLE_GRPC_SUPPORT=ON ^
  -Dtensorflow_ENABLE_SSL_SUPPORT=<ON/OFF> ^
  -Dtensorflow_ENABLE_SNAPPY_SUPPORT=<ON/OFF>
> cmake --build . --config Release --target tf_python_build_pip_package
```

Note: `^` is another line, GRPC must set `ON`, `WIN_CPU_SIMD_OPTIONS` can set to `OFF` if you don't know what's AVX. `PYTHON_EXECUTABLE` and `PYTHON_LIB` should specify to your own path.(Path to python.exe and python36.lib for instance)



OR your can try experimentally script `make.bat` to auto search required path

```bash
> make && cd _build
> cmake --build . --config Release --target tf_python_build_pip_package
```

Before doing this, your must edit `make.bat` and your own options (such as GPU or MKL)



### File Re-organized

The original cmake files are all in the `./tensorflow/contrib/cmake`, it's better to add `CMakeLists.txt` to each sub-folders

-----

THANKS TO ALL THE CONTRIBUTORS TO CMAKE SCRIPTS
