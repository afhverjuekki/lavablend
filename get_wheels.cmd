@echo off

set wheel_dir=./wheels
set blender_python_version=3.11
set list=win_amd64 manylinux_2_17_x86_64 macosx_11_0_arm64

rem Create wheels directory if it doesn't exist
if not exist "%wheel_dir%" mkdir "%wheel_dir%"

rem Download wheels for each platform
(for %%p in (%list%) do (
    echo Downloading wheels for %%p
    pip download rasterio --dest %wheel_dir% --only-binary=:all: --python-version=%blender_python_version% --platform=%%p
))

rem Delete numpy files
echo Deleting numpy files...
del "%wheel_dir%\numpy*"

pause


