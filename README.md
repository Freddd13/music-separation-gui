# <p align="center">Music Separation GUI</p>
This repo provides a one-click install for bytedance's [music_source_separation](https://github.com/bytedance/music_source_separation) and an easy-to-use GUI. 
Users can deal with single or batch music separation easily under Windows.
The installer in the [release]() contains everything the program needs including cuda. 
![](https://raw.githubusercontent.com/Freddd13/picBed/master/img/Snipaste_2022-01-22_20-47-50.png)

# Installation
## Prerequisites
- An Nvidia graphic card (otherwises it will use cpu to infer)
- **[FFmpeg](https://www.wikihow.com/Install-FFmpeg-on-Windows) with its env variable properly set in your system**
- Font Consolas

## Installation Guide
Download the latest [release]().
Open `run.exe`, wait the terminal to download and install packages. This may take some time, please be patient. After the first installation, you can quickly start the program in the future.

# Usage
You can choose either single music or multiple ones to seperate and get vocal, accompaniment or both. When dealing with a batch of songs, you need to put them in one clean folder.
If you have your own model and yaml, please switch to the Settings tab and load your own ckpt and yaml.

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

# Note
## CPU or GPU is being used?
After press the run button, check out the console message.
If it displays "use cuda for separation" and your GPU type, the GPU is being used. Otherwise it is CPU.

## GUI only
It's recommended to use the installer. If you have already got torch 1.7.1's gpu environment installed on your Windows PC or just want to use the gui, you can clone this repo to use in your environment.

```bash
git clone git@github.com:Freddd13/music-seperation-gui.git
cd music-source-separator
pip install -r requirements.txt
python MainUI.py
```
## Supported platforms
The GUI itself is cross-platformed, however, the packaging tool used here currently only supports windows. If you have proper torch environment installed, you can also use under linux and mac. Remember the program has been only tested under windows.

# Acknowledgements

- [music_source_separation](https://github.com/bytedance/music_source_separation) -- The original repo
- [QPT](https://github.com/QPT-Family/QPT)  -- A python packaging tool that can pack cuda
- [QGUI](https://github.com/QPT-Family/QGUI) -- An ultra lightweight desktop graphical framework below 100K
