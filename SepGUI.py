import time

# 导入CreateQGUI模块
from qgui import CreateQGUI, MessageBox
# 【可选】导入自定义导航栏按钮模块、GitHub导航栏模块
from qgui.banner_tools import BaseBarTool, GitHub, AIStudio
# 【可选】一次性导入所有的主界面工具模块
from qgui.notebook_tools import *
# 【可选】导入占位符
from qgui.manager import QStyle, HORIZONTAL



class QuickTab(object):
    def __init__(self):
        self.tab_index = 0

        self._source_button = ChooseFileTextButton(name="source_button", tab_index=self.tab_index, 
                                                    label_info="音频路径")
        self._aim_dir = ChooseDirTextButton(name="aim_button", tab_index=self.tab_index,
                                                    label_info="输出路径")
        self._check_button = CheckButton(name="check_button_{}".format(self.tab_index), options=[("人声", 0), ("伴奏", 1)], tab_index=self.tab_index,
                                            title="生成目标" )
        self._combo = Combobox(name = "combo_{}".format(self.tab_index), options=["与源文件相同","customize", "mp3", "wav", "m4a","flac"], tab_index=self.tab_index,
                                title="输出格式")
        self._toggle_button = ToggleButton(name = "toggle_button_{}".format(self.tab_index), options=("", 1), title="完成后打开", tab_index=self.tab_index)
        self._open_button = RunButton(name = "open_button_{}".format(self.tab_index),
                                     text = "打开输出文件夹", 
                                     bind_func = (lambda x: None),
                                     tab_index=self.tab_index)
        self._open_button.icon = None
        self._processbar = Progressbar(name = "processbar_{}".format(self.tab_index), tab_index=self.tab_index)
        self._run_button = RunButton(name = "run_button_{}".format(self.tab_index), 
                                     bind_func = (lambda x: None),
                                     tab_index=self.tab_index)

    @property
    def source_button(self):
        return self._source_button
    
    @property
    def aim_dir(self):
        return self._aim_dir

    @property
    def check_button(self):
        return self._check_button

    @property
    def combo(self):
        return self._combo

    @property
    def toggle_button(self):
        return self._toggle_button

    @property
    def open_button(self):
        return self._open_button

    @property
    def processbar(self):
        return self._processbar

    @property
    def run_button(self):
        return self._run_button

    
    def retrieve(self):
        return [
                    self._source_button,
                    self._aim_dir,
                    HorizontalToolsCombine([
                        self._check_button,
                        self._toggle_button,
                    ]),
                    HorizontalToolsCombine([
                        self._combo,
                        self._open_button,
                    ]),
                    HorizontalToolsCombine([
                        self._processbar, 
                        self._run_button
                    ])
                ]  


class AdvancedTab(object):
    def __init__(self):
        self.tab_index = 1

        self._source_dir_button = ChooseDirTextButton(name="source_dir_button_{}".format(self.tab_index), tab_index = self.tab_index,
                                                        label_info="音频文件夹") 
        self._aim_dir_button = ChooseDirTextButton(name="aim_dir_button_{}".format(self.tab_index),tab_index = self.tab_index,
                                                        label_info="输出文件夹")
        self._check_button = CheckButton(name="check_button_{}".format(self.tab_index) ,options=[("人声", 0), ("伴奏", 1)], tab_index=self.tab_index)
        self._combo = Combobox(name = "combo_{}".format(self.tab_index), options=["与源文件相同","customize", "mp3", "wav", "m4a","flac"], tab_index=self.tab_index,
                                title="输出格式")
        self._toggle_button = ToggleButton(name = "toggle_button_{}".format(self.tab_index), options=("", 1), title="完成后打开", tab_index=self.tab_index)
        self._open_button = RunButton(name = "open_button_{}".format(self.tab_index),
                                     text = "打开输出文件夹", 
                                     bind_func = (lambda x: None),
                                     tab_index=self.tab_index)
        self._open_button.icon = None                                
        self._processbar = Progressbar(name = "processbar_{}".format(self.tab_index), tab_index=self.tab_index)
        self._run_button = RunButton(name = "run_button_{}".format(self.tab_index), 
                                     bind_func = (lambda x: None),
                                     tab_index=self.tab_index,
                                     text="开始批量生成")
    
    @property
    def source_dir_button(self):
        return self._source_dir_button
    
    @property
    def aim_dir_button(self):
        return self._aim_dir_button

    @property
    def check_button(self):
        return self._check_button

    @property
    def combo(self):
        return self._combo

    @property
    def toggle_button(self):
        return self._toggle_button

    @property
    def open_button(self):
        return self._open_button

    @property
    def processbar(self):
        return self._processbar

    @property
    def run_button(self):
        return self._run_button

    
    def retrieve(self):
        return [
                    self._source_dir_button,
                    self._aim_dir_button,
                    HorizontalToolsCombine([
                        self._check_button,
                        self._toggle_button,
                    ]),
                    HorizontalToolsCombine([
                        self._combo,
                        self._open_button,
                    ]),
                    HorizontalToolsCombine([
                        self._processbar, 
                        self._run_button
                    ])
                ]


class SettingsTab(object):
    def __init__(self):
        self.tab_index = 2

        self._vocal_ckpt_button = ChooseFileTextButton(name="vocal_ckpt_button_{}".format(self.tab_index), tab_index = self.tab_index,
                                                        label_info="人声模型") 
        self._accomp_ckpt_button = ChooseFileTextButton(name="accomp_ckpt_button_{}".format(self.tab_index),tab_index = self.tab_index,
                                                        label_info="伴奏模型")
        self._check_button = CheckButton(options=[("选择1", 0), ("选择2", 1), ("选择3", 0)], tab_index=self.tab_index)
        self._combo = Combobox(options=["选择1", "选择2", "选择3"], tab_index=self.tab_index)
        self._processbar = Progressbar(name = "processbar_{}".format(self.tab_index), tab_index=self.tab_index)
        self._run_button = RunButton(name = "run_button_{}".format(self.tab_index), 
                                     bind_func = (lambda x: None),
                                     tab_index=self.tab_index)
    
    @property
    def vocal_ckpt_button(self):
        return self._vocal_ckpt_button
    
    @property
    def accomp_ckpt_button(self):
        return self._accomp_ckpt_button

    @property
    def check_button(self):
        return self._check_button

    @property
    def combo(self):
        return self._combo

    @property
    def processbar(self):
        return self._processbar

    @property
    def run_button(self):
        return self._run_button

    
    def retrieve(self):
        return [
                self._vocal_ckpt_button,
                self._accomp_ckpt_button,
                self._check_button,
                self._combo,
                HorizontalToolsCombine([self._processbar, 
                                        self._run_button])
                ]


    