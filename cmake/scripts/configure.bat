@echo off

:BEGIN
REM Find python and python lib
where /Q python
if %errorlevel% neq 0 (
    echo Cannot find python. Please make sure python is in PATH.
    goto EXIT
)
for /F %%i in ('python -c "import sys; print(sys.executable)"') do (
    set PYTHON_PATH=%%i
)
set SHOW_VER_INT="import sys; print(sys.version_info.major, sys.version_info.minor)"
for /F "tokens=1,2 delims= " %%i in ('python -c %SHOW_VER_INT%') do (
    set PYTHON_VER=%%i%%j
)
set PYTHON_LIB=%PYTHON_PATH:~0,-10%libs\python%PYTHON_VER%.lib

REM Check python requirements
for /F "skip=2 tokens=1,2 delims= " %%i in ('pip list') do (
    if "%%i"=="numpy" set HAS_NUMPY=1
    if "%%i"=="absl-py" set HAS_ABSL=1
    if "%%i"=="protobuf" set HAS_PROTOBUF=1
    if "%%i"=="six" set HAS_SIX=1
    if "%%i"=="setuptools" set HAS_SETUPTOOLS=1
    if "%%i"=="wheel" set HAS_WHEEL=1
)
if not "%HAS_NUMPY%"=="1" pip install numpy
if not "%HAS_ABSL%"=="1" pip install absl-py
if not "%HAS_PROTOBUF%"=="1" pip install protobuf
if not "%HAS_SIX%"=="1" pip install six
if not "%HAS_SETUPTOOLS%"=="1" pip install setuptools
if not "%HAS_WHEEL%"=="1" pip install wheel

REM Find CUDA runtime.
where /Q cudart64*.dll
if %errorlevel%==0 (
    for /F %%i in ('where cudart64*.dll') do (
        set CUDA_RT=%%~ni
        set CUDA_VER=%CUDA_RT:~9,2%
        set CUDA_HOME=%%~dpi..\
        goto GENERATE
    )
)

:GENERATE
REM Generating cmake projects.
if /I not "%1"=="DEBUG" (
    if not exist _build mkdir _build
    pushd _build
    cmake .. -A x64 -T host=x64 -DCMAKE_BUILD_TYPE=Release ^
        -DPYTHON_EXECUTABLE=%PYTHON_PATH% ^
        -DPYTHON_LIBRARIES=%PYTHON_LIB% ^
        -Dtensorflow_ENABLE_GPU=OFF ^
        -DCUDNN_HOME=%CUDA_HOME% ^
        -Dtensorflow_BUILD_SHARED_LIB=ON ^
        -Dtensorflow_WIN_CPU_SIMD_OPTIONS=/arch:AVX2 ^
        -Dtensorflow_ENABLE_MKL_SUPPORT=OFF ^
        -Dtensorflow_ENABLE_MKLDNN_SUPPORT=OFF ^
        -Dtensorflow_BUILD_PYTHON_BINDINGS=ON ^
        -Dtensorflow_DISABLE_EIGEN_FORCEINLINE=ON ^
        -Dtensorflow_ENABLE_GRPC_SUPPORT=ON ^
        -Dtensorflow_ENABLE_SSL_SUPPORT=ON ^
        -Dtensorflow_ENABLE_SNAPPY_SUPPORT=ON
    popd
)
if /I "%1"=="DEBUG" (
    goto DEBUG
) else (
    goto EXIT
)

:DEBUG
echo PYTHON_PATH=%PYTHON_PATH%
echo PYTHON_VER=%PYTHON_VER%
echo PYTHON_LIB=%PYTHON_LIB%
echo CUDA_HOME=%CUDA_HOME%
echo CUDA_RT=%CUDA_RT%
echo CUDA_VER=%CUDA_VER%

:EXIT
echo Done.