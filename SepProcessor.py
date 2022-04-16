from bytesep.models.lightning_modules import get_model_class
from bytesep.separator import Separator
from bytesep.utils import load_audio, read_yaml

import os
import sys
import ctypes
import pathlib
import shutil
import time
from typing import NoReturn

import numpy as np
import soundfile
import torch

LOCAL_CHECKPOINTS_DIR = os.path.join(os.getcwd(), "models")

def init_abn() -> NoReturn:
    # Need to use torch.distributed if models contain inplace_abn.abn.InPlaceABNSync.
    import torch.distributed as dist

    dist.init_process_group(
        'gloo', init_method='file:///tmp/somefile', rank=0, world_size=1
    )


def build_separator(config_yaml: str, checkpoint_path: str, device: str) -> Separator:
    r"""Build separator.

    Args:
        config_yaml: str
        checkpoint_path: str
        device: "cuda" | "cpu"

    Returns:
        separator: Separator
    """

    # Read config file.
    configs = read_yaml(config_yaml)
    sample_rate = configs['train']['sample_rate']
    input_channels = configs['train']['input_channels']
    output_channels = configs['train']['output_channels']
    target_source_types = configs['train']['target_source_types']
    target_sources_num = len(target_source_types)
    model_type = configs['train']['model_type']

    segment_seconds = 30
    segment_samples = int(segment_seconds * sample_rate)
    batch_size = 1

    print("Using {} for separating ..".format(device))

    models_contains_inplaceabn = False

    if models_contains_inplaceabn:
        init_abn(models_contains_inplaceabn)

    # Get model class.
    Model = get_model_class(model_type)

    # Create model.
    model = Model(
        input_channels=input_channels,
        output_channels=output_channels,
        target_sources_num=target_sources_num,
    )

    # Load checkpoint.
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint["model"])

    # Move model to device.
    model.to(device)

    # Create separator.
    separator = Separator(
        model=model,
        segment_samples=segment_samples,
        batch_size=batch_size,
        device=device,
    )

    return separator


def match_audio_channels(audio: np.array, input_channels: int) -> np.array:
    r"""Match input audio to correct channels.

    Args:
        audio: (audio_channels, audio_segments)
        input_channels: int

    Returns:
        (input_channels, audio_segments)
    """

    audio_channels = audio.shape[0]

    if audio_channels == input_channels:
        return audio

    elif audio_channels == 2 and input_channels == 1:
        return np.mean(audio, axis=0)[None, :]

    elif audio_channels == 1 and input_channels == 2:
        return np.tile(audio, (2, 1))

    else:
        raise NotImplementedError


def separate_file(  config_yamls, checkpoint_paths, audio_path, output_path,
                    scale_volume, cpu, extension, source_type, progress) -> NoReturn:
    r"""Separate a single file.
     """

    deal_with_mats()
    task_num = 1 if len(config_yamls) == 1 else 2

    if cpu or not torch.cuda.is_available():
        device = torch.device('cpu')
    else:
        device = torch.device('cuda')
        print("GPU: ",torch.cuda.get_device_name(0))

    if os.path.dirname(output_path) != "":
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    for i, (config_yaml, checkpoint_path) in enumerate(zip(config_yamls, checkpoint_paths)):
        # Read yaml files.
        configs = read_yaml(config_yaml)
        sample_rate = configs['train']['sample_rate']
        input_channels = configs['train']['input_channels']

        # deal with output suffix
        type_dict = {0: 'vocal', 1: 'accompaniment'}
        type_str = source_type if source_type != "both" else type_dict[i]
        if extension:
            suffix = os.path.basename(audio_path).split('.')[-2] + \
                     f"_{type_str}." + extension
        else:
            suffix = os.path.basename(audio_path).split('.')[-2] + \
                     f"_{type_str}." + os.path.basename(audio_path).split('.')[-1]

        # Build Separator.
        separator = build_separator(config_yaml, checkpoint_path, device)

        # Load audio.
        audio = load_audio(audio_path=audio_path, mono=False, sample_rate=sample_rate)
        audio = match_audio_channels(audio, input_channels)

        # Separate
        input_dict = {'waveform': audio}
        separate_time = time.time()

        sep_audio = separator.separate(input_dict)  # (input_channels, audio_samples)

        print('Separate time: {:.3f} s'.format(time.time() - separate_time))

        # Write out separated audio.
        if scale_volume:
            sep_audio /= np.max(np.abs(sep_audio))

        # Write out separated audio.
        tmp_wav_path = os.path.join("tmp.wav")
        target_path = os.path.join(output_path, suffix)
        soundfile.write(file=tmp_wav_path, data=sep_audio.T, samplerate=sample_rate)

        cmd = os.path.join(os.getcwd(), "tools/ffmpeg.exe") + \
                f' -y -loglevel panic -i "{tmp_wav_path}" "{target_path}"'
        os.system(cmd)
        os.remove(tmp_wav_path)

        print(f'Write out to {target_path}')
        print( (i+1) / task_num * 100)
        progress.do_simple_progress( (i+1) / task_num * 100)

def separate_dir(config_yamls, checkpoint_paths, audios_dir, outputs_dir,
                scale_volume, cpu, extension, source_type,  progress) -> NoReturn:
    r"""Separate all audios in a directory.
     """
    deal_with_mats()
    if cpu or not torch.cuda.is_available():
        device = torch.device('cpu')
    else:
        device = torch.device('cuda')
        print("GPU: ",torch.cuda.get_device_name(0))

    os.makedirs(outputs_dir, exist_ok=True)
    audio_names = sorted(os.listdir(audios_dir))
    audios_num = len(audio_names)
    task_num = audios_num if len(config_yamls) == 1 else audios_num * 2

    for i, (config_yaml, checkpoint_path) in enumerate(zip(config_yamls, checkpoint_paths)):
        configs = read_yaml(config_yaml)
        sample_rate = configs['train']['sample_rate']
        separator = build_separator(config_yaml, checkpoint_path, device)

        for n, audio_name in enumerate(audio_names):
            # deal with path and suffix
            audio_path = os.path.join(audios_dir, audio_name)
            type_dict = {0: 'vocal', 1: 'accompaniment'}
            type_str = source_type if source_type != "both" else type_dict[i]
            if extension:
                suffix = os.path.basename(audio_path).split('.')[-2] + \
                        f"_{type_str}." + extension
            else:
                suffix = os.path.basename(audio_path).split('.')[-2] + \
                        f"_{type_str}." + os.path.basename(audio_path).split('.')[-1]

            # Load audio.
            audio = load_audio(audio_path=audio_path, mono=False, sample_rate=sample_rate)

            # Separate
            input_dict = {'waveform': audio}
            separate_time = time.time()

            sep_audio = separator.separate(input_dict)  # (input_channels, audio_samples)

            print('Separate time: {:.3f} s'.format(time.time() - separate_time))

            # Write out separated audio.
            if scale_volume:
                sep_audio /= np.max(np.abs(sep_audio))

            # postprocess
            tmp_wav_path = os.path.join("tmp.wav")
            target_path = os.path.join(outputs_dir, suffix)
            soundfile.write(file=tmp_wav_path, data=sep_audio.T, samplerate=sample_rate)

            cmd = os.path.join(os.getcwd(), "tools/ffmpeg.exe") + \
                    f' -y -loglevel panic -i "{tmp_wav_path}" "{target_path}"'
            os.system(cmd)
            os.remove(tmp_wav_path)

            # inform observer
            progress.do_multiple_progress( (n + 1 + i*audios_num) / task_num * 100)
            print(f'{n+1} / {audios_num}, Write out to {outputs_dir}')

def get_paths(source_type: str, model_type: str) -> [str, str]:

    r"""Get config_yaml and checkpoint paths.

    Args:
        source_type: str, "vocals" | "accompaniment"
        model_type: str, "MobileNet_Subbandtime" | "ResUNet143_Subbandtime"

    Returns:
        config_yaml: str
        checkpoint_path: str
    """

    local_checkpoints_dir = LOCAL_CHECKPOINTS_DIR
    error_message = "Checkpoint is incomplete, please download again!"

    try:
        if model_type == "MobileNet_Subbandtime":

            if source_type == "vocals":

                config_yaml = os.path.join(
                    local_checkpoints_dir,
                    "train_scripts/musdb18/vocals-accompaniment,mobilenet_subbandtime.yaml",
                )

                checkpoint_path = os.path.join(
                    local_checkpoints_dir,
                    "mobilenet_subbtandtime_vocals_7.2dB_500k_steps_v2.pth",
                )
                assert os.path.getsize(checkpoint_path) == 4621773, error_message

            elif source_type == "accompaniment":

                config_yaml = os.path.join(
                    local_checkpoints_dir,
                    "train_scripts/musdb18/accompaniment-vocals,mobilenet_subbandtime.yaml",
                )

                checkpoint_path = os.path.join(
                    local_checkpoints_dir,
                    "mobilenet_subbtandtime_accompaniment_14.6dB_500k_steps_v2.pth",
                )
                assert os.path.getsize(checkpoint_path) == 4621773, error_message

            else:
                raise NotImplementedError

        elif model_type == "ResUNet143_Subbandtime":

            if source_type == "vocals":

                config_yaml = os.path.join(
                    local_checkpoints_dir,
                    "train_scripts/musdb18/vocals-accompaniment,resunet_subbandtime.yaml",
                )

                checkpoint_path = os.path.join(
                    local_checkpoints_dir,
                    "resunet143_subbtandtime_vocals_8.7dB_500k_steps_v2.pth",
                )
                assert os.path.getsize(checkpoint_path) == 414046363, error_message

            elif source_type == "accompaniment":

                config_yaml = os.path.join(
                    local_checkpoints_dir,
                    "train_scripts/musdb18/accompaniment-vocals,resunet_subbandtime.yaml",
                )

                checkpoint_path = os.path.join(
                    local_checkpoints_dir,
                    "resunet143_subbtandtime_accompaniment_16.4dB_500k_steps_v2.pth",
                )
                assert os.path.getsize(checkpoint_path) == 414036369, error_message

            else:
                raise NotImplementedError

        else:
            raise NotImplementedError

    except:
        download_checkpoints()

    return config_yaml, checkpoint_path


def download_checkpoints() -> NoReturn:
    r"""Download checkpoints and config yaml files from Zenodo."""

    zenodo_dir = "https://zenodo.org/record/5804160/files"
    local_checkpoints_dir = LOCAL_CHECKPOINTS_DIR

    # Download checkpoints.
    checkpoint_names = [
        "mobilenet_subbtandtime_vocals_7.2dB_500k_steps_v2.pth?download=1",
        "mobilenet_subbtandtime_accompaniment_14.6dB_500k_steps_v2.pth?download=1",
        "resunet143_subbtandtime_vocals_8.7dB_500k_steps_v2.pth?download=1",
        "resunet143_subbtandtime_accompaniment_16.4dB_500k_steps_v2.pth?download=1",
    ]

    os.makedirs(local_checkpoints_dir, exist_ok=True)

    for checkpoint_name in checkpoint_names:

        remote_checkpoint_link = os.path.join(zenodo_dir, checkpoint_name).replace('\\', '/')
        local_checkpoint_link = os.path.join(
            local_checkpoints_dir, checkpoint_name.split("?")[0]
        )
        command_str = os.path.join(os.getcwd(), "tools/wget.exe") + \
                        f" -O {local_checkpoint_link} {remote_checkpoint_link}"
        os.system(command_str)

    # Download and unzip config yaml files.
    remote_zip_scripts_link = os.path.join(
        zenodo_dir,
        "train_scripts.zip?download=1").replace('\\', '/'
    )
    local_zip_scripts_path = os.path.join(local_checkpoints_dir, "train_scripts.zip")

    cmd1 = os.path.join(os.getcwd(), "tools/wget.exe") + f" -O {local_zip_scripts_path} {remote_zip_scripts_link}"
    cmd2 = os.path.join(os.getcwd(), "tools/unzip.exe") + f" {local_zip_scripts_path} -d {local_checkpoints_dir}"
    os.system(cmd1)
    os.system(cmd2)


def deal_with_mats():
    '''
        Mat should at {filters_dir}. We first try to copy mat to that dir. 
        If it failed, we try to download from zenodo.
        Anyway, we want to get a admin power to ensure success.
    '''
    filters_dir = f'{str( pathlib.Path.home() )}/bytesep_data/filters'
    source_dir = './models/filters'

    for _name in ['f_4_64.mat', 'h_4_64.mat']:
        _source = os.path.join(source_dir, _name)
        _path = os.path.join(filters_dir, _name)

        if not os.path.isfile(_path):
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
            os.makedirs(os.path.dirname(_path), exist_ok=True)
            try:
                shutil.copyfile(_source, _path)

            except Exception as error:
                print(error)
                print("Downloading mat...")
                remote_path = (
                    f"https://zenodo.org/record/5513378/files/{_name}?download=1"
                )

                command_str = os.path.join(os.getcwd(), "tools/wget.exe") + f'-O "{_path}" "{remote_path}"'
                os.system(command_str)
