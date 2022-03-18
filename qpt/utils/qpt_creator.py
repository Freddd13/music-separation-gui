from qpt.executor import CreateExecutableModule as CEM
from qpt.smart_opt import set_default_pip_source
from qpt.modules.cuda import CopyCUDAPackage
                                                     
set_default_pip_source("https://pypi.python.org/simple")                                                     
module = CEM(work_dir="./resources",                
			launcher_py_path="./resources/MainUI.py", 
			save_path="./out",
			requirements_file="./resources/requirements.txt",
			sub_modules=[CopyCUDAPackage(cuda_version="11.0"),
						 CopyWhl2Packages('./torch-1.7.1+cu110-cp37-cp37m-win_amd64.whl'),
						 CopyWhl2Packages('./torchvision-0.8.2+cu110-cp37-cp37m-win_amd64.whl'),
						 CopyWhl2Packages('./torchaudio-0.7.2-cp37-none-win_amd64.whl'),
						],
			icon="test.ico"
			)   
module.make()