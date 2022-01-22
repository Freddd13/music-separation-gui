from qpt.executor import CreateExecutableModule as CEM
from qpt.smart_opt import set_default_pip_source
from qpt.modules.cuda import CopyCUDAPackage
                                                     
module = CEM(work_dir="./resources",                
			launcher_py_path="./resources/MainUI.py", 
			save_path="./out",
			requirements_file="./resources/requirements.txt",
			sub_modules=[CopyCUDAPackage(cuda_version="11.0")],
			icon="test.ico"
			)   
module.make()