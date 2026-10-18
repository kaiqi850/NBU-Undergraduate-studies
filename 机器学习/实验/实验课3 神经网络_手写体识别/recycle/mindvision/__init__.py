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
""" Init MindSpore Vision toolbox and benchmark. """

image_backend = "PIL"

video_backend = "av"


def set_image_backend(backend_package):
    """
    Specifies the package used to load images.

    Args:
        backend_package (string): Name of the image backend.
    """
    global image_backend
    support_backend_package = ["PIL"]

    if backend_package not in support_backend_package:
        raise ValueError(
            f"Invalid backend package '{backend_package}'. Options are '{support_backend_package}'.")

    image_backend = backend_package


def get_image_backend():
    """
    Gets the name of the package used to load images.

    Returns:
        str: Name of the image backend.
    """
    return image_backend


def set_video_backend(backend_package):
    """
    Specifies the package used to decode videos.

    Args:
        backend_package (string): Name of the video backend.
    """
    global video_backend
    support_backend_package = ["av"]

    if backend_package not in support_backend_package:
        raise ValueError(f"Invalid video backend '{backend_package}'. Options are '{support_backend_package}'.")

    video_backend = backend_package


def get_video_backend():
    """
    Returns the currently active video backend used to decode videos.

    Returns:
        str: Name of the video backend.
    """

    return video_backend
