# <p align="center">Music Separation GUI</p>
This repo provides a one-click install for bytedance's [music_source_separation](https://github.com/bytedance/music_source_separation) and an easy-to-use GUI. 
Users can deal with single or batch music separation easily under Windows.
The installer in the [release](https://github.com/Freddd13/music-separation-gui/releases) contains everything the program needs including cuda. 
![](https://raw.githubusercontent.com/Freddd13/picBed/master/img/Snipaste_2022-01-22_20-47-50.png)

# Installation
## Prerequisites
- An Nvidia graphic card with its driver installed (otherwises it will use CPU to infer) 
- Font Consolas

## Installation Guide
#### One click install (If you have no torch GPU environment):

Download the latest [release](https://github.com/Freddd13/music-separation-gui/releases).

To install, run `install.cmd`. 

Wait the terminal to download and install packages. If you encounter a win32 dll import error, try to run the `fix_win32_error.bat`.

**This may take some time, please be patient.**
**If it is stuck for too long, please try to press "Enter" on your keyboard!!!** (This problem may only occurs during the first opening.)

After the first installation, you can quickly start the program by running `run.exe` in the future. In fact, the `install.cmd` will provoke the `run.exe`. The former is to deal with torch packages, so there's no need to run it after the installation.

#### GUI only (If you have already got torch `1.7.1` GPU environment):

Please checkout [GUI only](#GUI only)

# Usage
After installation, you can delete `opt/package` to free some space.
You can choose either single music or multiple ones to seperate and get vocal, accompaniment or both. When dealing with a batch of songs, you need to put them in one clean folder.
If you have your own model and yaml, please switch to the Settings tab and load your own ckpt and yaml.



# Note
## CPU or GPU is being used?
After press the run button, check out the console message.
If it displays "using cuda for separation" and your GPU type, the GPU is being used. Otherwise it is CPU.

## GUI only
It's recommended to use the installer. If you have already got torch `1.7.1`'s gpu environment installed on your Windows PC or just want to use the gui, you can clone this repo to use it in your environment.

If you don't have proper torch installed and want to manually install gui, please first install torch gpu `1.7.1` using the following command.
```bash
conda install pytorch==1.7.1 torchvision==0.8.2 torchaudio==0.7.2 -c pytorch  # or use pip to install
```
Now you can install other things to use the GUI.
```bash
git clone git@github.com:Freddd13/music-seperation-gui.git
cd music-source-separator
pip install -r requirements.txt
python MainUI.py
```
## Supported platforms
The GUI itself is cross-platformed, however, the packaging tool used here currently only supports windows. If you have proper torch environment installed, you can also use it under linux and mac. Remember the program has been only tested under windows. But some code needs to be corrected to adapt other OS, for example, some `os.system code` with ".exe".

# References
[1] Qiuqiang Kong, Yin Cao, Haohe Liu, Keunwoo Choi, Yuxuan Wang, Decoupling Magnitude and Phase Estimation with Deep ResUNet for Music Source Separation, International Society for Music Information Retrieval (ISMIR), 2021.
```
@inproceedings{kong2021decoupling,
  title={Decoupling Magnitude and Phase Estimation with Deep ResUNet for Music Source Separation.},
  author={Kong, Qiuqiang and Cao, Yin and Liu, Haohe and Choi, Keunwoo and Wang, Yuxuan },
  booktitle={ISMIR},
  year={2021},
  organization={Citeseer}
}
```

# Acknowledgements

- [music_source_separation](https://github.com/bytedance/music_source_separation) -- The original repo
- [QPT](https://github.com/QPT-Family/QPT)  -- A python packaging tool that can pack cuda
- [QGUI](https://github.com/QPT-Family/QGUI) -- An ultra lightweight desktop graphical framework below 100K
