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
""" Create the MNIST dataset. """

import os
import struct
from typing import Optional, Callable, Union, Tuple
import numpy as np

import mindspore.dataset.vision.c_transforms as transforms
from mindspore.dataset.vision import Inter

from mindvision.dataset.download import read_dataset
from mindvision.dataset.meta import Dataset, ParseDataset
from mindvision.io.path import check_file_exist
from mindvision.check_param import Validator
from mindvision.engine.class_factory import ClassFactory, ModuleType

__all__ = ["Mnist", "ParseMnist"]


@ClassFactory.register(ModuleType.DATASET)
class Mnist(Dataset):
    """
    Mnist dataset loader, It has train directory and test directory.
    The directory structure of Mnist dataset looks like:

        ./mnist/
        ├── test
        │   ├── t10k-images-idx3-ubyte
        │   └── t10k-labels-idx1-ubyte
        └── train
            ├── train-images-idx3-ubyte
            └── train-labels-idx1-ubyte

    Args:
        path(string): Root directory of the Mnist dataset or inference image.
        split(str): The dataset split, supports "train", "test", or "infer". Default: "train".
        transform(callable, optional): A function transform that takes in a image. Default:None.
        target_transform(callable, optional): A function transform that takes in a label. Default:None.
        batch_size(int): Batch size of dataset. Default:32.
        repeat_num(int): The repeat num of dataset. Default:1.
        shuffle(bool, optional): Whether or not to perform shuffle on the dataset. Default:None.
        num_parallel_workers(int, optional): Number of subprocess used to fetch the dataset in parallel.Default: None.
        num_shards(int, optional): Number of shards that the dataset will be divided into. Default: None.
        shard_id(int, optional): The shard ID within num_shards. Default: None.
        resize(int, tuple): The output size of the resized image. If size is an integer, the smaller edge of the
        image will be resized to this value with the same image aspect ratio. If size is a sequence of length 2,
        it should be (height, width). Default: 32.
        download(bool) : Whether to download the dataset. Default: False.
    """

    def __init__(self,
                 path: str,
                 split: str = "train",
                 transform: Optional[Callable] = None,
                 target_transform: Optional[Callable] = None,
                 batch_size: int = 32,
                 repeat_num: int = 1,
                 shuffle: Optional[bool] = None,
                 num_parallel_workers: int = 1,
                 num_shards: Optional[int] = None,
                 shard_id: Optional[int] = None,
                 resize: Union[int, Tuple[int, int]] = 32,
                 download: bool = False):
        Validator.check_string(split, ["train", "test", "infer"], "split")
        mode = "L"

        if split != "infer":
            self.parse_mnist = ParseMnist(path=os.path.join(path, split))
            load_data = self.parse_mnist.parse_dataset
        else:
            load_data = read_dataset

        super(Mnist, self).__init__(path=path,
                                    split=split,
                                    load_data=load_data,
                                    transform=transform,
                                    target_transform=target_transform,
                                    batch_size=batch_size,
                                    repeat_num=repeat_num,
                                    resize=resize,
                                    shuffle=shuffle,
                                    num_parallel_workers=num_parallel_workers,
                                    num_shards=num_shards,
                                    shard_id=shard_id,
                                    download=download,
                                    mode=mode)

    @property
    def index2label(self):
        """Get the mapping of indexes and labels."""
        return {0: 'zero', 1: 'one', 2: 'two', 3: 'three', 4: 'four',
                5: 'five', 6: 'six', 7: 'seven', 8: 'eight', 9: 'nine'}

    def download_dataset(self):
        """Download the MNIST data if it doesn't exist already."""
        if self.split == "infer":
            raise ValueError("Download is not supported for infer.")
        self.parse_mnist.download_and_extract_archive()

    def default_transform(self):
        """Set the default transform for Mnist dataset."""
        rescale = 1.0 / 255.0
        shift = 0.0
        rescale_nml = 1 / 0.3081
        shift_nml = -1 * 0.1307 / 0.3081

        # define map operations
        trans = [
            transforms.Resize(size=self.resize, interpolation=Inter.LINEAR),
            transforms.Rescale(rescale, shift),
            transforms.Rescale(rescale_nml, shift_nml),
            transforms.HWC2CHW(),
        ]
        return trans


class ParseMnist(ParseDataset):
    """
    DownLoad and parse Mnist dataset.
    """
    url_path = 'http://yann.lecun.com/exdb/mnist/'

    resources = {"train": [("train-images-idx3-ubyte.gz", "f68b3c2dcbeaaa9fbdd348bbdeb94873"),
                           ("train-labels-idx1-ubyte.gz", "d53e105ee54ea40749a09fcbcd1e9432")],
                 "test": [("t10k-images-idx3-ubyte.gz", "9fb629c4189551a2d022fa330f9573f3"),
                          ("t10k-labels-idx1-ubyte.gz", "ec29112dd5afa0611ce80d1b7f02629c")]}

    def download_and_extract_archive(self):
        """Download the MNIST dataset if it doesn't exists."""
        bool_list = []
        # Check whether the file exists and check value of md5.
        for url, _ in self.resources[os.path.basename(self.path)]:
            filename = os.path.splitext(url)[0]
            file_path = os.path.join(self.path, filename)
            bool_list.append(os.path.isfile(file_path))
        if all(bool_list):
            return

        os.makedirs(self.path, exist_ok=True)

        # download files
        for filename, md5 in self.resources[os.path.basename(self.path)]:
            url = os.path.join(self.url_path, filename)
            self.download.download_and_extract_archive(url,
                                                       download_path=self.path,
                                                       filename=filename,
                                                       md5=md5)

    def __decode_idx3_ubyte(self):
        """Parse idx3 files."""
        check_file_exist(self.image_path)
        bin_data = open(self.image_path, "rb").read()
        fmt_header = '>iiii'
        offset = 0
        _, num_images, num_rows, num_cols = struct.unpack_from(fmt_header, bin_data, offset)
        image_size = num_rows * num_cols
        offset += struct.calcsize(fmt_header)
        fmt_image = '>' + str(image_size) + 'B'
        images = np.empty((num_images, num_rows, num_cols, 1), dtype=np.float32)

        for i in range(num_images):
            images[i] = np.array(struct.unpack_from(fmt_image, bin_data, offset)).reshape((num_rows, num_cols, 1))
            offset += struct.calcsize(fmt_image)

        return images

    def __decode_idx1_ubyte(self):
        """Parse idx1 files."""
        check_file_exist(self.label_path)
        bin_data = open(self.label_path, "rb").read()
        fmt_header = '>ii'
        offset = 0
        _, num_images = struct.unpack_from(fmt_header, bin_data, offset)
        offset += struct.calcsize(fmt_header)
        fmt_label = '>B'
        labels = np.empty(num_images, dtype=np.int32)

        for i in range(num_images):
            labels[i] = struct.unpack_from(fmt_label, bin_data, offset)[0]
            offset += struct.calcsize(fmt_label)

        return labels

    def parse_dataset(self):
        """Parse data from Mnist dataset file."""
        url_list = self.resources[os.path.basename(self.path)]
        image_file = os.path.splitext(url_list[0][0])[0]
        label_file = os.path.splitext(url_list[1][0])[0]

        self.image_path = os.path.join(self.path, image_file)
        self.label_path = os.path.join(self.path, label_file)

        data = self.__decode_idx3_ubyte()
        label = self.__decode_idx1_ubyte()

        return data, label
