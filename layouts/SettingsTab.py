from qgui.notebook_tools import *


class SettingsTab(object):
    def __init__(self):
        self.tab_index = 2

        self._vocal_ckpt_button = ChooseFileTextButton(name="vocal_ckpt_button_{}".format(self.tab_index), tab_index = self.tab_index,
                                                        label_info="vocal ckpt", entry_info="auto", button_info="select") 
        self._vocal_yaml_button = ChooseFileTextButton(name="vocal_yaml_button_{}".format(self.tab_index), tab_index = self.tab_index,
                                                        label_info="vocal yaml", entry_info="auto", button_info="select")                                                         
        self._accomp_ckpt_button = ChooseFileTextButton(name="accomp_ckpt_button_{}".format(self.tab_index),tab_index = self.tab_index,
                                                        label_info="accomp ckpt", entry_info="auto", button_info="select")
        self._accomp_yaml_button = ChooseFileTextButton(name="accomp_yaml_button_{}".format(self.tab_index),tab_index = self.tab_index,
                                                        label_info="accomp yaml", entry_info="auto", button_info="select")                                                        
        self._check_button = CheckButton(options=[("选择1", 0), ("选择2", 1), ("选择3", 0)], tab_index=self.tab_index)
        self._combo = Combobox(options=["选择1", "选择2", "选择3"], tab_index=self.tab_index)
        self._processbar = Progressbar(name = "processbar_{}".format(self.tab_index), tab_index=self.tab_index)
        self._save_button = RunButton(name = "run_button_{}".format(self.tab_index), 
                                     bind_func = (lambda x: None),
                                     text = "Save",
                                     tab_index=self.tab_index)
        self._save_button.icon = None
    
    @property
    def vocal_ckpt_button(self):
        return self._vocal_ckpt_button

    @property
    def vocal_yaml_button(self):
        return self._vocal_yaml_button

    @property
    def accomp_ckpt_button(self):
        return self._accomp_ckpt_button
    @property
    def accomp_yaml_button(self):
        return self._accomp_yaml_button

    @property
    def processbar(self):
        return self._processbar

    @property
    def save_button(self):
        return self._save_button

    @save_button.setter
    def save_button(self, func):
        self._save_button.bind_func = func


    def retrieve(self):
        return [
                self._vocal_ckpt_button,
                self._vocal_yaml_button,
                self._accomp_ckpt_button,
                self._accomp_yaml_button,
                self._save_button
                ]
