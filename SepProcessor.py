import argparse
import os
import pathlib
import time
from typing import NoReturn

import numpy as np
import soundfile
import torch

from bytesep.models.lightning_modules import get_model_class
from bytesep.separator import Separator
from bytesep.utils import load_audio, read_yaml

LOCAL_CHECKPOINTS_DIR = os.path.join(pathlib.Path.home(), "bytesep_data")
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


def separate_file(config_yamls, checkpoint_paths, audio_path, output_path, scale_volume, cpu, extension, source_type, progress) -> NoReturn:
    r"""Separate a single file.

    Args:
        config_yaml: str, the config file of a model being trained.
        checkpoint_path: str, the path of checkpoint to be loaded.
        audio_path: str, path of file to be separated.
        output_path: str, path of separated file to be written.
        scale_volume: bool
        cpu: bool

    Returns:
        NoReturn
    """

    # Arguments & parameters
    # config_yaml = args.config_yaml
    # checkpoint_path = args.checkpoint_path
    # audio_path = args.audio_path
    # output_path = args.output_path
    # scale_volume = args.scale_volume
    # cpu = args.cpu
    
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

        type_dict = {0: 'vocal', 1: 'accompaniment'}
        type_str = source_type if source_type != "both" else type_dict[i]
        if extension:
            suffix = os.path.basename(audio_path).split('.')[-2] + "_{}.".format(type_str) + extension
        else:
            suffix = os.path.basename(audio_path).split('.')[-2] + "_{}.".format(type_str) + os.path.basename(audio_path).split('.')[-1]        

        # Build Separator.
        separator = build_separator(config_yaml, checkpoint_path, device)

        # Load audio.
        audio = load_audio(audio_path=audio_path, mono=False, sample_rate=sample_rate)
        # audio: (input_channels, audio_samples)

        audio = match_audio_channels(audio, input_channels)
        # audio: (input_channels, audio_samples)

        input_dict = {'waveform': audio}

        # Separate
        separate_time = time.time()

        sep_audio = separator.separate(input_dict)
        # (input_channels, audio_samples)

        print('Separate time: {:.3f} s'.format(time.time() - separate_time))

        # Write out separated audio.
        if scale_volume:
            sep_audio /= np.max(np.abs(sep_audio))

        # Write out separated audio.
        tmp_wav_path = os.path.join("tmp.wav")
        target_path = os.path.join(output_path, suffix)
        soundfile.write(file=tmp_wav_path, data=sep_audio.T, samplerate=sample_rate)

        os.system(
            'ffmpeg -y -loglevel panic -i "{}" "{}"'.format(tmp_wav_path, target_path)
        )
        os.remove(tmp_wav_path)

        print('Write out to {}'.format(target_path))
        print( (i+1) / task_num * 100)
        progress.do_simple_progress( (i+1) / task_num * 100)

def separate_dir(config_yamls, checkpoint_paths, audios_dir, outputs_dir, scale_volume, cpu, extension, source_type,  progress) -> NoReturn:
    r"""Separate all audios in a directory.

    Args:
        config_yaml: str, the config file of a model being trained.
        checkpoint_path: str, the path of checkpoint to be loaded.
        audios_dir: str, the directory of audios to be separated.
        output_dir: str, the directory to write out separated audios.
        scale_volume: bool, if True then the volume is scaled to the maximum value of 1.
        cpu: bool

    Returns:
        NoReturn
    """

    # Arguments & parameters
    # config_yaml = args.config_yaml
    # checkpoint_path = args.checkpoint_path
    # audios_dir = args.audios_dir
    # outputs_dir = args.outputs_dir
    # scale_volume = args.scale_volume
    # cpu = args.cpu


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

            audio_path = os.path.join(audios_dir, audio_name)

            # Load audio.
            audio = load_audio(audio_path=audio_path, mono=False, sample_rate=sample_rate)

            input_dict = {'waveform': audio}

            # Separate
            separate_time = time.time()

            sep_audio = separator.separate(input_dict)
            # (input_channels, audio_samples)

            type_dict = {0: 'vocal', 1: 'accompaniment'}
            type_str = source_type if source_type != "both" else type_dict[i]
            if extension:
                suffix = os.path.basename(audio_path).split('.')[-2] + "_{}.".format(type_str) + extension
            else:
                suffix = os.path.basename(audio_path).split('.')[-2] + "_{}.".format(type_str) + os.path.basename(audio_path).split('.')[-1]        
            

            print('Separate time: {:.3f} s'.format(time.time() - separate_time))

            # Write out separated audio.
            if scale_volume:
                sep_audio /= np.max(np.abs(sep_audio))

            # output_path = os.path.join(
            #     outputs_dir, '{}.mp3'.format(pathlib.Path(audio_name).stem)
            # )

            tmp_wav_path = os.path.join("tmp.wav")
            target_path = os.path.join(outputs_dir, suffix)
            soundfile.write(file=tmp_wav_path, data=sep_audio.T, samplerate=sample_rate)

            os.system(
                'ffmpeg -y -loglevel panic -i "{}" "{}"'.format(tmp_wav_path, target_path)
            )
            os.remove(tmp_wav_path)
            progress.do_multiple_progress( (n + 1 + i*audios_num) / task_num * 100)
            print('{} / {}, Write out to {}'.format(n+1, audios_num, outputs_dir))

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

    return config_yaml, checkpoint_path

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode")

    parser_separate = subparsers.add_parser("separate_file")
    parser_separate.add_argument(
        "--config_yaml",
        type=str,
        required=True,
        help="The config file of a model being trained.",
    )
    parser_separate.add_argument(
        "--checkpoint_path", type=str, required=True, help="Checkpoint path."
    )
    parser_separate.add_argument(
        "--audio_path",
        type=str,
        required=True,
        help="The path of audio to be separated.",
    )
    parser_separate.add_argument(
        "--output_path",
        type=str,
        required=True,
        help="The path to write out separated audio.",
    )
    parser_separate.add_argument(
        '--scale_volume',
        action='store_true',
        default=False,
        help="Set this flag to scale separated audios to maximum value of 1.",
    )
    parser_separate.add_argument(
        '--cpu',
        action='store_true',
        default=False,
        help="Set this flag to use CPU.",
    )

    parser_separate_dir = subparsers.add_parser("separate_dir")
    parser_separate_dir.add_argument(
        "--config_yaml",
        type=str,
        required=True,
        help="The config file of a model being trained.",
    )
    parser_separate_dir.add_argument(
        "--checkpoint_path", type=str, required=True, help="Checkpoint path."
    )
    parser_separate_dir.add_argument(
        "--audios_dir",
        type=str,
        required=True,
        help="The directory of audios to be separated.",
    )
    parser_separate_dir.add_argument(
        "--outputs_dir",
        type=str,
        required=True,
        help="The directory to write out separated audios.",
    )
    parser_separate_dir.add_argument(
        '--scale_volume',
        action='store_true',
        default=False,
        help="Set this flag to scale separated audios to maximum value of 1.",
    )
    parser_separate_dir.add_argument(
        '--cpu',
        action='store_true',
        default=False,
        help="Set this flag to use CPU.",
    )

    args = parser.parse_args()

    if args.mode == "separate_file":
        separate_file(args)

    elif args.mode == "separate_dir":
        separate_dir(args)

    else:
        raise NotImplementedError
