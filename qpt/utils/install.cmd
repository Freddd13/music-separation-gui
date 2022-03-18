echo off
chcp 65001
cd /d %~dp0
set QPT_COLOR=False
set QPT_MODE=Debug
set PYTHONPATH=Python/Lib/site-packages;Python/Lib;Python
set PATH=Python/Lib/site-package;Python/Lib;Python;%PATH%
cls
echo Installing torch
"./Python/python.exe" "-m" "pip" "install" "./opt/packages/ttkbootstrap-1.5.1-py3-none-any.whl"
"./Python/python.exe" "-m" "pip" "install" "./opt/packages/numpy-1.18.5-cp37-cp37m-win_amd64.whl"
"./Python/python.exe" "-m" "pip" "install" "./opt/packages/torch-1.7.1+cu110-cp37-cp37m-win_amd64.whl"
"./Python/python.exe" "-m" "pip" "install" "./opt/packages/torchvision-0.8.2+cu110-cp37-cp37m-win_amd64.whl"
"./Python/python.exe" "-m" "pip" "install" "./opt/packages/torchaudio-0.7.2-cp37-none-win_amd64.whl"
echo Done, opening run.exe.
start run.exe
pause