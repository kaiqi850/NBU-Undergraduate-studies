# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
""" Video input output module. """

from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple, Union

import mindspore as ms


def write_video(
        filename: str,
        video_tensor: ms.Tensor,
        fps: float,
        video_codec: str = "libx264",
        options: Optional[Dict[str, Any]] = None,
        audio_tensor: Optional[ms.Tensor] = None,
        audio_fps: Optional[float] = None,
        audio_codec: Optional[str] = None,
        audio_options: Optional[Dict[str, Any]] = None) -> None:
    """
    Writes 4d tensor in [T, H, W, C] format in a video file, where the `T` is video frames,
    `H` and `W` is the is height and weight of the video frames, `C` is the number of channels.

    Args:
        filename (str): Path where the video will be saved in location.
        video_tensor (Tensor[T, H, W, C]): Tensor containing the individual frames tensor in
            [T, H, W, C] format.
        fps (Number): Video frames per second, like 30 fps.
        video_codec (str): The name of the video codec, i.e. "libx264", "h264", etc.
        options (Dict): Dictionary containing options to be passed into the PyAV video stream
        audio_tensor (Tensor[C, N]): Tensor containing the audio, where C is the number of channels
            and N is the number of samples
        audio_fps (Number): Audio sample rate, typically 44100 or 48000.
        audio_codec (str): The name of the audio codec, i.e. "mp3", "aac", etc.
        audio_options (Dict): Dictionary containing options to be passed into the PyAV audio stream.
    """

    raise ValueError("Waiting to be implementation.")


def read_video(
        filename: str,
        start_pts: Union[float, Fraction] = 0,
        end_pts: Optional[Union[float, Fraction]] = None,
        pts_unit: str = "pts") -> Tuple[ms.Tensor, ms.Tensor, Dict[str, Any]]:
    """
    Reads a video from a file, returning both the video frames as well as the audio frames.

    Args:
        filename (str): Path to the video file.
        start_pts (int if pts_unit = 'pts', float / Fraction if pts_unit = 'sec', optional):
            The start presentation time of the video.
        end_pts (int if pts_unit = 'pts', float / Fraction if pts_unit = 'sec', optional):
            The end presentation time.
        pts_unit (str, optional): Unit in which start_pts and end_pts values will be interpreted,
            either 'pts' or 'sec'. Defaults to 'pts'.

    Returns:
        vframes (Tensor[T, H, W, C]): the `T` video frames.
        aframes (Tensor[K, L]): The audio frames, where `K` is the number of channels and `L` is the number of points.
        info (Dict): Metadata for the video and audio. Can contain the fields video_fps (float) and audio_fps (int).
    """

    raise ValueError("Waiting to be implementation.")


def read_video_timestamps(
        filename: str,
        pts_unit: str = "pts") -> Tuple[List[int], Optional[float]]:
    """
    List the video frames timestamps. Note that the function decodes the whole video frame-by-frame.

    Args:
        filename (str): path to the video file.
        pts_unit (str, optional): unit in which timestamp values will be returned. Either 'pts' or 'sec'.
        Defaults to 'pts'.

    Returns:
        pts (List[int] if pts_unit = 'pts', List[Fraction] if pts_unit = 'sec'):
            presentation timestamps for each one of the frames in the video.
        video_fps (float, optional): the frame rate for the video
    """

    raise ValueError("Waiting to be implementation.")
