@echo off
REM Default building target.
set TARGET=tensorflow

if /I not "%1"=="" set TARGET=%1

pushd _build
echo Building %TARGET%...
cmake --build . --config Release --target %TARGET%
popd

goto EXIT
:DEBUG
echo TARGET=%TARGET%

:EXIT
echo Done.
