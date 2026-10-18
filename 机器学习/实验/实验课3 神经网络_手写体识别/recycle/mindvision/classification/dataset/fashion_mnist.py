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
""" Create the Fashion MNIST dataset. """

import os
from typing import Optional, Callable, Union, Tuple

from mindspore.dataset.vision import Inter
import mindspore.dataset.vision.c_transforms as transforms

from mindvision.dataset.meta import Dataset
from mindvision.check_param import Validator
from mindvision.dataset.download import read_dataset
from mindvision.classification.dataset.mnist import ParseMnist
from mindvision.engine.class_factory import ClassFactory, ModuleType

__all__ = ["FashionMnist", "ParseFashionMnist"]


@ClassFactory.register(ModuleType.DATASET)
class FashionMnist(Dataset):
    """
    Fashion Mnist dataset loader, It has train directory and test directory.
    The directory structure of Mnist dataset looks like:

        ./fashion_mnist/
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
            self.parse_fashion_mnist = ParseFashionMnist(path=os.path.join(path, split))
            load_data = self.parse_fashion_mnist.parse_dataset
        else:
            load_data = read_dataset

        super(FashionMnist, self).__init__(path=path,
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
        return {0: 'T-shirt/top', 1: 'Trouser', 2: 'Pullover', 3: 'Dress', 4: 'Coat',
                5: 'Sandal', 6: 'Shirt', 7: 'Sneaker', 8: 'Bag', 9: 'Ankle boot'}

    def download_dataset(self):
        """Download the Fashion MNIST data if it doesn't exist already."""
        if self.split == "infer":
            raise ValueError("Download is not supported for infer.")
        self.parse_fashion_mnist.download_and_extract_archive()

    def default_transform(self):
        """Set the default transform for Fashion Mnist dataset."""
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


class ParseFashionMnist(ParseMnist):
    """
    DownLoad and parse FashionMnist dataset.
    """
    url_path = "http://fashion-mnist.s3-website.eu-central-1.amazonaws.com/"

    resources = {"train": [("train-images-idx3-ubyte.gz", "8d4fb7e6c68d591d4c3dfef9ec88bf0d"),
                           ("train-labels-idx1-ubyte.gz", "25c81989df183df01b3e8a0aad5dffbe")],
                 "test": [("t10k-images-idx3-ubyte.gz", "bef4ecab320f06d8554ea6380940ec79"),
                          ("t10k-labels-idx1-ubyte.gz", "bb300cfdad3c16e7a12a480ee83cd310")]}
