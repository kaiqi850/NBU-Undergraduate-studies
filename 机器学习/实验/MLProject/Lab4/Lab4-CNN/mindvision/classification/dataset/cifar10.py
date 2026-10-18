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
""" Create the CIFAR10 dataset. """

import os
import pickle
from typing import Optional, Callable, Union, Tuple
import numpy as np

import mindspore.dataset.vision.c_transforms as transforms

from mindvision.dataset.download import read_dataset
from mindvision.dataset.meta import Dataset, ParseDataset
from mindvision.check_param import Validator
from mindvision.engine.class_factory import ClassFactory, ModuleType

__all__ = ["Cifar10", "ParseCifar10"]


@ClassFactory.register(ModuleType.DATASET)
class Cifar10(Dataset):
    """
    The directory structure of Cifar10 dataset looks like:

        ./
        └── cifar-10-batches-py
             ├── data_batch_1
             ├── data_batch_2
             ├── data_batch_3
             ├── data_batch_4
             ├── data_batch_5
             ├── test_batch
             ├── readme.html
             └── batches.meta

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
            self.parse_cifar10 = ParseCifar10(path=os.path.join(path, split))
            load_data = self.parse_cifar10.parse_dataset
        else:
            load_data = read_dataset

        super(Cifar10, self).__init__(path=path,
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
        return self.parse_cifar10.index2label

    def download_dataset(self):
        """Download the Cifar10 data if it doesn't exist already."""
        if self.split == "infer":
            raise ValueError("Download is not supported for infer.")
        self.parse_cifar10.download_and_extract_archive()

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


class ParseCifar10(ParseDataset):
    """
    DownLoad and parse Cifar10 dataset.
    """
    url_path = {"path": "http://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz",
                "md5": "c58f30108f718f92721af3b95e74349a"}
    base_dir = "cifar-10-batches-py"
    classes_key = "label_names"

    extract = {
        "train": [
            ("data_batch_1", "c99cafc152244af753f735de768cd75f"),
            ("data_batch_2", "d4bba439e000b95fd0a9bffe97cbabec"),
            ("data_batch_3", "54ebc095f3ab1f0389bbae665268c751"),
            ("data_batch_4", "634d18415352ddfa80567beed471001a"),
            ("data_batch_5", "482c414d41f54cd18b22e5b47cb7c3cb"),
        ],
        "test": [
            ("test_batch", "40351d587109b95175f43aff81a1287e")
        ],
        "meta": [
            ("batches.meta", "5ff9c542aee3614f3951f8cda6e48888")
        ]
    }

    def download_and_extract_archive(self):
        """Download the Cifar10 dataset if it doesn't exists."""
        path = os.path.split(self.path)[0]
        bool_list = []
        # Check whether the file exists and check value of md5.
        for value in self.extract.values():
            for i in value:
                filename, md5 = i[0], i[1]
                file_path = os.path.join(path, self.base_dir, filename)
                bool_list.append(
                    os.path.isfile(file_path) and self.download.check_md5(file_path, md5)
                )

        if all(bool_list):
            return

        # download files
        self.download.download_and_extract_archive(self.url_path["path"],
                                                   download_path=path,
                                                   md5=self.url_path["md5"])

    def __load_meta(self):
        """Load meta file."""
        meta_file = self.extract["meta"][0][0]
        meta_md5 = self.extract["meta"][0][1]
        meta_path = os.path.join(os.path.split(self.path)[0], self.base_dir, meta_file)

        if not os.path.isfile(meta_path) and self.download.check_md5(meta_path, meta_md5):
            raise RuntimeError(
                "Metadata file not found or check md5 value is incorrect. You can set download=True.")

        with open(meta_path, "rb") as f:
            data = pickle.load(f, encoding="latin1")
            classes = data[self.classes_key]
            index2label = {i: v for i, v in enumerate(classes)}
            return index2label

    def __load_cifar_batch(self):
        """Load single batch of cifar."""
        if not os.path.isfile(self.data_path) and self.download.check_md5(self.data_path, self.md5):
            raise RuntimeError(
                "Dataset file not found or check md5 value is incorrect. You can set download=True.")
        with open(self.data_path, "rb") as f:
            data_dict = pickle.load(f, encoding="latin1")

        data = data_dict["data"]
        labels = data_dict["labels"] if "labels" in data_dict else data_dict["fine_labels"]

        data = data.reshape(-1, 3, 32, 32).transpose(0, 2, 3, 1)
        labels = np.array(labels, dtype=np.int32)

        return data, labels

    def parse_dataset(self):
        """Parse data from Cifar10 dataset file."""
        data_list = []
        labels_list = []
        file_list = self.extract[os.path.basename(self.path)]
        self.index2label = self.__load_meta()

        for file_name, md5 in file_list:
            self.data_path = os.path.join(os.path.split(self.path)[0], self.base_dir, file_name)
            self.md5 = md5
            data, labels = self.__load_cifar_batch()
            data_list.append(data)
            labels_list.append(labels)

        data = np.concatenate(data_list, axis=0)
        labels = np.concatenate(labels_list, axis=0)

        return data, labels
