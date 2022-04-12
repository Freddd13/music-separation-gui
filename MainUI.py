from layouts.SingleTab import *
from layouts.MultipleTab import *
from layouts.SettingsTab import *

from SepProcessor import get_paths, separate_file, separate_dir

from qgui import CreateQGUI, MessageBox
from qgui.banner_tools import GitHub
from qgui.notebook_tools import *

import pathlib


LOCAL_CHECKPOINTS_DIR = os.path.join(os.getcwd(), "models")

class MainLayout(object):
    def __init__(self):
        self.setup_UI()

    def setup_UI(self):
        self.setup_base()
        self.setup_layout()
        self.setup_bind_func()
        self.setup_construct()

    def setup_base(self):
        self.Gui = CreateQGUI(title="Music Separation", 
                   tab_names=["Single", "Batch", "Settings"])
        self.Gui.add_banner_tool(GitHub(url="https://github.com/bytedance/music_source_separation", name="Original Repo"))
        self.Gui.add_banner_tool(GitHub(url="https://github.com/Freddd13/music-seperation-gui", name="GUI Repo"))
        self.Gui.set_navigation_about(author="Freddd13",
                                version="0.0.3",
                                github_url="https://github.com/Freddd13",
                                other_info=["GUI for bytesep"])
        self.Gui.set_navigation_about(author="qiuqiangkong",
                                version="21-12-25",
                                github_url="https://github.com/qiuqiangkong",
                                other_info=["Bytesep core"]) 

    def setup_layout(self):
        self.tab1 = SingleTab()
        self.tab2 = MultipleTab()
        self.tab3 = SettingsTab()

    def setup_construct(self):
        self.construct(self.tab1)
        self.construct(self.tab2)
        self.construct(self.tab3)
    
    def construct(self, obj):
        for elem in obj.retrieve():
            self.Gui.add_notebook_tool(elem)    



class MainBind(MainLayout):
    def __init__(self):
        super().__init__()
        ### These params should exist as a state but there seems no way to let a input box's change invoke its\
        ### filebtn's callback function.
        ### Thus I get them from btns every time in the operating functions:
        # self.single_source_file = ""
        # self.single_aim_dir = ""
        # self.multiple_source_dir = ""
        # self.multiple_aim_dir = ""
        self.vocal_ckpt_yaml, self.vocal_ckpt_file =  get_paths("vocals", "ResUNet143_Subbandtime")
        self.accomp_ckpt_yaml, self.accomp_ckpt_file = get_paths("accompaniment", "ResUNet143_Subbandtime") 

        self.single_source_type_vocal = False
        self.single_source_type_accomp = True
        self.multiple_source_type_vocal = False
        self.multiple_source_type_accomp = True

        self.open_after_generation = True

        self.single_output_extension = ""
        self.multiple_output_extension = "" 

    def setup_bind_func(self):
        # bind functions
            # self.tab1.source_button.bind_func = self.update_single_source_file
            # self.tab1.aim_dir.bind_func = self.update_single_aim_dir
            # self.tab2.source_dir_button.bind_func = self.update_multiple_source_dir
            # self.tab2.aim_dir_button.bind_func = self.update_multiple_aim_dir
        
        # bind save setting
        self.tab3.save_button = self.update_ckpt_and_yaml   

        # bind source selection
        self.tab1.check_button = self.update_single_source_type
        self.tab2.check_button = self.update_multiple_source_type

        # bind open target
        self.tab1.open_button = self.open_single_target_folder
        self.tab2.open_button = self.open_multiple_target_folder
        self.tab1.toggle_button = self.change_single_after_open
        self.tab2.toggle_button = self.change_multiple_after_open

        # extension -> allback err!!!
            # self.tab1.combo.bind_func = self.update_single_extension
            # self.tab2.combo.bind_func = self.update_multiple_extension

        # bind run separation
        self.tab1.run_button = self.run_single
        self.tab2.run_button = self.run_multiple


    ############### bind_funcs ################

    # def update_single_extension(self, args):
    #     print(self.single_output_extension)
    
    # def update_multiple_extension(self, args):
    #     print(self.multiple_output_extension)

    # def update_single_source_file(self, args):
    #     self.single_source_file = args[self.tab1.source_button.name].get()
    
    # def update_single_aim_dir(self, args):
    #     self.single_aim_dir = args[self.tab1.aim_dir.name].get()

    # def update_multiple_source_dir(self, args):
    #     self.multiple_source_dir = args[self.tab2.source_dir_button.name].get()
    
    # def update_multiple_aim_dir(self, args):
    #     self.multiple_aim_dir = args[self.tab2.aim_dir_button.name].get()

    def update_single_source_type(self, args):
        self.single_source_type_vocal = int( args[self.tab1.check_button.name + "-Vocals"].get() )
        self.single_source_type_accomp = int( args[self.tab1.check_button.name + "-Accompaniment"].get() )
    
    def update_multiple_source_type(self, args):
        self.multiple_source_type_vocal = int( args[self.tab2.check_button.name + "-Vocals"].get() )
        self.multiple_source_type_accomp = int( args[self.tab2.check_button.name + "-Accompaniment"].get() )

    # ui-operating callbacks
    def do_simple_progress(self, value):
        self.tab1.processbar.get_arg_info().set(value)

    def do_multiple_progress(self, value):
        self.tab2.processbar.get_arg_info().set(value)

    def open_single_target_folder(self, args):
        single_aim_dir = args[self.tab1.aim_dir.name].get()
        if not os.path.exists(single_aim_dir):
            single_aim_dir = '.'
        os.startfile(single_aim_dir)

    def open_multiple_target_folder(self, args):
        multiple_aim_dir =  args[self.tab2.aim_dir_button.name].get()
        if not os.path.exists(multiple_aim_dir):
            multiple_aim_dir = '.'
        os.startfile(multiple_aim_dir)

    def change_single_after_open(self, args):
        # ????????????????????????
        self.open_after_generation = True if int( args[self.tab1.toggle_button.name + '-'].get() ) else False
    
    def change_multiple_after_open(self, args):
        self.open_after_generation = True if int( args[self.tab2.toggle_button.name + '-'].get() ) else False     

    def update_ckpt_and_yaml(self, args):
        vocal_ckpt = args[self.tab3.vocal_ckpt_button.name].get()
        vocal_yaml = args[self.tab3.vocal_yaml_button.name].get()
        accomp_ckpt = args[self.tab3.accomp_ckpt_button.name].get()
        accomp_yaml = args[self.tab3.accomp_yaml_button.name].get()
        
        self.vocal_ckpt_file = vocal_ckpt if vocal_ckpt != "auto" else self.vocal_ckpt_file
        self.vocal_ckpt_yaml = vocal_yaml if vocal_yaml != "auto" else self.vocal_ckpt_yaml
        self.accomp_ckpt_file = accomp_ckpt if accomp_ckpt != "auto" else self.accomp_ckpt_file
        self.accomp_ckpt_yaml = accomp_yaml if accomp_yaml != "auto" else self.accomp_ckpt_yaml

        MessageBox.info("Set vocal ckpt to {}.\n".format(self.vocal_ckpt_file) + \
                        "Set vocal yaml to {}.\n".format(self.vocal_ckpt_yaml) + \
                        "Set accomp ckpt to {}.\n".format(self.accomp_ckpt_file) + \
                        "Set accomp yaml to {}.\n".format(self.accomp_ckpt_yaml)
        )

    # sep-operating functions
    def run_single(self):
        return NotImplementedError
    
    def run_multiple(self):
        return not NotImplementedError


class MainWindow(MainBind):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.init_environment()
    
    def init_environment(self):
            os.environ["PATH"] += os.pathsep + os.path.join(os.getcwd(), "tools")

    def run_single(self, args):
        single_source_file = args[self.tab1.source_button.name].get()
        single_aim_dir = args[self.tab1.aim_dir.name].get()

        if not ( os.path.exists(single_source_file) and os.path.exists(single_aim_dir) ):
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
            MessageBox.info("Please choose at least one source type!")
            return

        # fucking callback error forces me to do this
        extension = self.tab1.combo.get_arg_info().get()
        if extension == "Same as source":
            extension = None

        separate_file(
                config_yamls = config_yamls,
                checkpoint_paths = checkpoint_paths,
                audio_path = single_source_file,
                output_path = single_aim_dir,
                scale_volume = False,
                cpu = False,
                extension = extension,
                source_type=source_type,
                progress = self        
        )

        if self.open_after_generation:
            os.startfile(single_aim_dir)
        

    def run_multiple(self, args):
        multiple_source_dir = args[self.tab2.source_dir_button.name].get()
        multiple_aim_dir = args[self.tab2.aim_dir_button.name].get()
        if not ( os.path.exists(multiple_source_dir) and os.path.exists(multiple_aim_dir) ):
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
            MessageBox.info("Please choose at least one source type!！")
            return

        extension = self.tab2.combo.get_arg_info().get()
        if extension == "Same as source":
            extension = None

        separate_dir(
                config_yamls = config_yamls,
                checkpoint_paths = checkpoint_paths,
                audios_dir = multiple_source_dir,
                outputs_dir = multiple_aim_dir,
                scale_volume = False,
                cpu = False,
                extension = extension,       
                source_type=source_type,                         
                progress = self
        )        

        if self.open_after_generation:
            os.startfile(multiple_aim_dir)


if __name__ == '__main__':
    M = MainWindow()
    M.Gui.run()