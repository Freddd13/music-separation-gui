echo on
chcp 65001
cd /d %~dp0
set QPT_COLOR=False
set QPT_MODE=Debug
set PYTHONPATH=Python/Lib/site-packages;Python/Lib;Python
set PATH=Python/Lib/site-package;Python/Lib;Python;%PATH%
cls
"./Python/python.exe" "-m" "pip" "install" "pywin32==225"
"./Python/python.exe" "./python/scripts/pywin32_postinstall.py" "-install"
pause