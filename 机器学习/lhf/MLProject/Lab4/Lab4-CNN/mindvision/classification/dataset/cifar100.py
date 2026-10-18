# Copyright 2022 Huawei Technologies Co., Ltd
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
""" Create the CIFAR100 dataset. """

import os
from typing import Optional, Callable, Union, Tuple

import mindspore.dataset.vision.c_transforms as transforms

from mindvision.dataset.download import read_dataset
from mindvision.dataset.meta import Dataset
from mindvision.check_param import Validator
from mindvision.classification.dataset.cifar10 import ParseCifar10
from mindvision.engine.class_factory import ClassFactory, ModuleType

__all__ = ["Cifar100", "ParseCifar100"]


@ClassFactory.register(ModuleType.DATASET)
class Cifar100(Dataset):
    """
    The directory structure of Cifar100 dataset looks like:

        ./
        └── cifar-100-python
             ├── train
             ├── test
             ├── meta
             └── file.txt~

    Args:
        path (string): Root directory of the Mnist dataset or inference image.
        split (str): The dataset split, supports "train", "test", or "infer". Default: "train".
        transform (callable, optional): A function transform that takes in a image. Default:None.
        target_transform (callable, optional): A function transform that takes in a label. Default:None.
        batch_size (int): Batch size of dataset. Default:32.
        repeat_num (int): The repeat num of dataset. Default:1.
        shuffle (bool, optional): Whether or not to perform shuffle on the dataset. Default:None.
        num_parallel_workers (int): Number of subprocess used to fetch the dataset in parallel.Default: 1.
        num_shards (int, optional): Number of shards that the dataset will be divided into. Default: None.
        shard_id (int, optional): The shard ID within num_shards. Default: None.
        resize (int, tuple): The output size of the resized image. If size is an integer, the smaller edge of the
        image will be resized to this value with the same image aspect ratio. If size is a sequence of length 2,
        it should be (height, width). Default: 224.
        download (bool) : Whether to download the dataset. Default: False.
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
                 resize: Union[int, Tuple[int, int]] = 224,
                 download: bool = False):
        Validator.check_string(split, ["train", "test", "infer"], "split")

        if split != "infer":
            self.parse_cifar100 = ParseCifar100(path=os.path.join(path, split))
            load_data = self.parse_cifar100.parse_dataset
        else:
            load_data = read_dataset

        super(Cifar100, self).__init__(path=path,
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
                                       download=download)

    @property
    def index2label(self):
        """Get the mapping of indexes and labels."""
        return self.parse_cifar100.index2label

    def download_dataset(self):
        """Download the Cifar100 data if it doesn't exist already."""
        if self.split == "infer":
            raise ValueError("Download is not supported for infer.")
        self.parse_cifar100.download_and_extract_archive()

    def default_transform(self):
        """Set the default transform for Cifar10 dataset."""
        trans = []
        if self.split == "train":
            trans += [
                transforms.RandomCrop((32, 32), (4, 4, 4, 4)),
                transforms.RandomHorizontalFlip(prob=0.5)
            ]

        trans += [
            transforms.Resize(self.resize),
            transforms.Rescale(1.0 / 255.0, 0.0),
            transforms.Normalize([0.4914, 0.4822, 0.4465], [0.2023, 0.1994, 0.2010]),
            transforms.HWC2CHW()
        ]

        return trans


class ParseCifar100(ParseCifar10):
    """
    DownLoad and parse Cifar100 dataset.
    """
    url_path = {"path": "https://www.cs.toronto.edu/~kriz/cifar-100-python.tar.gz",
                "md5": "eb9058c3a382ffc7106e4002c42a8d85"}
    base_dir = "cifar-100-python"
    classes_key = "fine_label_names"

    extract = {
        "train": [
            ("train", "16019d7e3df5f24257cddd939b257f8d")
        ],
        "test": [
            ("test", "f0ef6b0ae62326f3e7ffdfab6717acfc")
        ],
        "meta": [
            ("meta", "7973b15100ade9c7d40fb424638fde48")
        ]
    }
