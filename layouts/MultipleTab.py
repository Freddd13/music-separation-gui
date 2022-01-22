from qgui.notebook_tools import *


class MultipleTab(object):
    def __init__(self):
        self.tab_index = 1

        self._source_dir_button = ChooseDirTextButton(name="source_dir_button_{}".format(self.tab_index), tab_index = self.tab_index,
                                                        label_info="Audio", entry_info= "", button_info="select") 
        self._aim_dir_button = ChooseDirTextButton(name="aim_dir_button_{}".format(self.tab_index),tab_index = self.tab_index,
                                                        label_info="Output", entry_info= "", button_info="select")
        self._check_button = CheckButton(name="check_button_{}".format(self.tab_index) ,options=[("Vocals", 0), ("Accompaniment", 1)], tab_index=self.tab_index, title="target_type")
        self._combo = Combobox(name = "combo_{}".format(self.tab_index), options=["Same as source", "mp3", "wav", "m4a","flac"], tab_index=self.tab_index,
                                title="output extension")
        self._toggle_button = ToggleButton(name = "toggle_button_{}".format(self.tab_index), options=("", 1), title="Auto open", tab_index=self.tab_index)
        self._open_button = RunButton(name = "open_button_{}".format(self.tab_index),
                                     text = "Open Output", 
                                     bind_func = (lambda x: None),
                                     tab_index=self.tab_index)
        self._open_button.icon = None                                
        self._processbar = Progressbar(name = "processbar_{}".format(self.tab_index), tab_index=self.tab_index, title="Progress")
        self._run_button = RunButton(name = "run_button_{}".format(self.tab_index), 
                                     bind_func = (lambda x: None),
                                     tab_index=self.tab_index,
                                     text="Run Batch")
    
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

    @check_button.setter
    def check_button(self, func):
        self._check_button.bind_func = func

    @open_button.setter
    def open_button(self, func):
        self._open_button.bind_func = func

    @toggle_button.setter
    def toggle_button(self, func):
        self._toggle_button.bind_func = func

    @run_button.setter
    def run_button(self, func):
        self._run_button.bind_func = func
    
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
