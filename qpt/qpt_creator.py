# 导入QPT
from qpt.executor import CreateExecutableModule as CEM
from qpt.smart_opt import set_default_pip_source
from qpt.modules.cuda import CopyCUDAPackage

set_default_pip_source("https://pypi.tuna.tsinghua.edu.cn/simple")
#                                                        -----关于路径的部分，强烈建议使用绝对路径避免出现问题-----
module = CEM(work_dir="./EN",                # [项目文件夹]待打包的目录，并且该目录下需要有↓下方提到的py文件
             launcher_py_path="./EN/MainUI.py", # [主程序文件]用户启动EXE文件后，QPT要执行的py文件
             save_path="./out",
            requirements_file="./EN/requirements.txt",               
            icon="./test.ico")                         # [自定义图标文件]支持将exe文件设置为ico/JPG/PNG等格式的自定义图标
# 开始打包
module.make()