import SepGUI
from SepProcessor import separate_file, separate_dir, get_paths
import pathlib

from qgui import CreateQGUI, MessageBox
from qgui.banner_tools import BaseBarTool, GitHub
from qgui.notebook_tools import *
from qgui.manager import QStyle, HORIZONTAL

LOCAL_CHECKPOINTS_DIR = os.path.join(pathlib.Path.home(), "bytesep_data")

class MainUI(object):
    def __init__(self):
        self.single_source_file = ""
        self.single_aim_dir = ""
        self.multiple_source_dir = ""
        self.multiple_aim_dir = ""
        
        self.vocal_ckpt_yaml, self.vocal_ckpt_file =  get_paths("vocals", "ResUNet143_Subbandtime")
        self.accomp_ckpt_yaml, self.accomp_ckpt_file = get_paths("accompaniment", "ResUNet143_Subbandtime") 

        self.single_source_type_vocal = False
        self.single_source_type_accomp = True
        self.multiple_source_type_vocal = False
        self.multiple_source_type_accomp = True

        self.open_after_generation = True

        self.single_output_extension = ""
        self.multiple_output_extension = ""

        self.setup_UI()

    # def update_single_extension(self, args):
    #     print(self.single_output_extension)
    

    # def update_multiple_extension(self, args):
    #     print(self.multiple_output_extension)
    
    def setup_UI(self):
        self.setup_base()
        self.setup_layout()
        self.setup_bind_func()
        self.setup_construct()

    def setup_base(self):
        self.Gui = CreateQGUI(title="Music Separation",  # 界面标题
                   tab_names=["单文件分离", "批量分离", "设置"])
        self.Gui.add_banner_tool(GitHub(url="https://github.com/bytedance/music_source_separation", name="在Github上查看原项目"))
        self.Gui.add_banner_tool(GitHub(url="https://github.com/QPT-Family/QGUI", name="在Github上查看本GUI项目"))
        self.Gui.set_navigation_about(author="Freddd13",
                                version="0.0.1",
                                github_url="https://github.com/Freddd13",
                                other_info=["GUI for bytesep"])
        self.Gui.set_navigation_about(author="qiuqiangkong",
                                version="0.0.1",
                                github_url="https://github.com/qiuqiangkong",
                                other_info=["Bytesep core"]) 

    def setup_layout(self):
        self.tab1 = SepGUI.QuickTab()
        self.tab2 = SepGUI.AdvancedTab()
        self.tab3 = SepGUI.SettingsTab()

    def setup_bind_func(self):
        # bind functions
        self.tab1.source_button.bind_func = self.update_single_source_file
        self.tab1.aim_dir.bind_func = self.update_single_aim_dir
        self.tab2.source_dir_button.bind_func = self.update_multiple_source_dir
        self.tab2.aim_dir_button.bind_func = self.update_multiple_aim_dir
        self.tab3.vocal_ckpt_button.bind_func = self.update_vocal_ckpt_file
        self.tab3.accomp_ckpt_button.bind_func = self.update_accomp_ckpt_file 

        self.tab1.check_button.bind_func = self.update_single_source_type
        self.tab2.check_button.bind_func = self.update_multiple_source_type

        # bind open target button
        self.tab1.open_button.bind_func = self.open_single_target_folder
        self.tab2.open_button.bind_func = self.open_multiple_target_folder
        self.tab1.toggle_button.bind_func = self.change_single_after_open
        self.tab2.toggle_button.bind_func = self.change_multiple_after_open


        # extension
        # callback err!!!
            # self.tab1.combo.bind_func = self.update_single_extension
            # self.tab2.combo.bind_func = self.update_multiple_extension

        # sep bind funcs
        self.tab1.run_button.bind_func = self.run_single
        self.tab2.run_button.bind_func = self.run_multiple

    def setup_construct(self):
        self.construct(self.tab1)
        self.construct(self.tab2)
        self.construct(self.tab3)
    
    def construct(self, obj):
        for elem in obj.retrieve():
            self.Gui.add_notebook_tool(elem)    

    ############### bind_funcs ################

    def update_single_source_file(self, args):
        self.single_source_file = args[self.tab1.source_button.name].get()
    
    def update_single_aim_dir(self, args):
        self.single_aim_dir = args[self.tab1.aim_dir.name].get()

    def update_multiple_source_dir(self, args):
        self.multiple_source_dir = args[self.tab2.source_dir_button.name].get()
    
    def update_multiple_aim_dir(self, args):
        self.multiple_aim_dir = args[self.tab2.aim_dir_button.name].get()

    def update_vocal_ckpt_file(self, args):
        self.vocal_ckpt_file = args[self.tab3.vocal_ckpt_button.name].get()

    def update_accomp_ckpt_file(self, args):
        self.accomp_ckpt_file = args[self.tab3.accomp_ckpt_button.name].get()

    def update_single_source_type(self, args):
        # 这里设计真的诡异
        self.single_source_type_vocal = bool( args[self.tab1.check_button.name + "-人声"].get() )
        self.single_source_type_accomp = bool( args[self.tab1.check_button.name + "-伴奏"].get() )
    
    def update_multiple_source_type(self, args):
        self.multiple_source_type_vocal = bool( args[self.tab2.check_button.name + "-人声"].get() )
        self.multiple_source_type_accomp = bool( args[self.tab2.check_button.name + "-伴奏"].get() )


    # callbacks
    def do_simple_progress(self, value):
        self.tab1.processbar.get_arg_info().set(value)

    def do_multiple_progress(self, value):
        self.tab2.processbar.get_arg_info().set(value)

    def open_single_target_folder(self, args):
        os.startfile(self.single_aim_dir)

    def open_multiple_target_folder(self, args):
        os.startfile(self.multiple_aim_dir)

    def change_single_after_open(self, args):
        # ????????????????????????
        self.open_after_generation = True if bool( args[self.tab1.toggle_button.name + '-'].get() ) else False
    
    def change_multiple_after_open(self, args):
        self.open_after_generation = True if bool( args[self.tab2.toggle_button.name + '-'].get() ) else False     
    
    
    ############ interact with seperator ############



class MainWindow(MainUI):
    def __init__(self):
        super(MainWindow, self).__init__()

    def run_single(self, args):
        if (not self.single_source_file) or (not self.single_aim_dir):
            MessageBox.info("Please specify both the source file and aim file!")
            return

        if self.single_source_type_accomp and self.single_source_type_vocal:
            source_type = "both"
            checkpoint_paths = [self.vocal_ckpt_file, self.accomp_ckpt_file]
            config_yamls = [self.vocal_ckpt_yaml, self.accomp_ckpt_yaml]

        elif self.single_source_type_vocal:
            source_type = "vocal"
            checkpoint_paths = [self.vocal_ckpt_file]
            config_yamls = [self.vocal_ckpt_yaml]

        elif self.single_source_type_accomp:
            source_type = "accompaniment"
            checkpoint_paths = [self.accomp_ckpt_file]
            config_yamls = [self.accomp_ckpt_yaml]          
        else:
            MessageBox.info("至少选择一种生成类型！")
            return

        # fucking callback error forces me to do this
        extension = self.tab1.combo.get_arg_info().get()
        if extension == "与源文件相同":
            extension = None

        separate_file(
                config_yamls = config_yamls,
                checkpoint_paths = checkpoint_paths,
                audio_path = self.single_source_file,
                output_path = self.single_aim_dir,
                scale_volume = False,
                cpu = False,
                extension = extension,
                source_type=source_type,
                progress = self        
        )

        if self.open_after_generation:
            os.startfile(self.single_aim_dir)
            
        

    def run_multiple(self, args):
        if (not self.multiple_source_dir) or (not self.multiple_aim_dir):
            MessageBox.info("Please specify both the source dir and aim dir!")
            return

        if self.multiple_source_type_accomp and self.multiple_source_type_vocal:
            source_type = "both"
            checkpoint_paths = [self.vocal_ckpt_file, self.accomp_ckpt_file]
            config_yamls = [self.vocal_ckpt_yaml, self.accomp_ckpt_yaml]

        elif self.multiple_source_type_vocal:
            source_type = "vocal"
            checkpoint_paths = [self.vocal_ckpt_file]
            config_yamls = [self.vocal_ckpt_yaml]

        elif self.multiple_source_type_accomp:
            source_type = "accompaniment"
            checkpoint_paths = [self.accomp_ckpt_file]
            config_yamls = [self.accomp_ckpt_yaml]          
        else:
            MessageBox.info("至少选择一种生成类型！")
            return

        extension = self.tab2.combo.get_arg_info().get()
        if extension == "与源文件相同":
            extension = None

        separate_dir(
                config_yamls = config_yamls,
                checkpoint_paths = checkpoint_paths,
                audios_dir = self.multiple_source_dir,
                outputs_dir = self.multiple_aim_dir,
                scale_volume = False,
                cpu = False,
                extension = extension,       
                source_type=source_type,                         
                progress = self
        )        

        if self.open_after_generation:
            os.startfile(self.multiple_aim_dir)


if __name__ == '__main__':
    M = MainWindow()
    M.Gui.run()