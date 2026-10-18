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
# ==============================================================================
"""Load COCO_Base dataset."""

import os
from typing import Callable, Optional, Union, Tuple

import numpy as np
from pycocotools.coco import COCO as cocotools

import mindspore.dataset.vision.c_transforms as transforms

from mindvision.check_param import Validator
from mindvision.dataset.download import read_dataset
from mindvision.dataset.meta import Dataset, ParseDataset
from mindvision.engine.class_factory import ClassFactory, ModuleType

__all__ = ["COCO", "ParseCOCO"]


@ClassFactory.register(ModuleType.DATASET)
class COCO(Dataset):
    """
    The directory structure of COCO dataset looks like:

        ./coco2017/
        ├── val2017
        │   ├── 000000000139.jpg
        │   ├── 000000000285.jpg
        │   └── ....
        ├── train2017
        │   ├── 000000000009.jpg
        │   ├── 000000000025.jpg
        │   └── ....
        └── annotations
            ├── captions_train2017.json
            ├── captions_val2017.json
            ├── instances_train2017.json
            ├── instances_val2017.json
            ├── person_keypoints_train2017.json
            └── person_keypoints_val2017.json

    Args:
        path(string): Root directory of the ImageNet dataset or inference image.
        anno_file: The path of annotations files.
        split(str): The dataset split, supports "train", "val", or "infer". Default: "train".
        transform(callable, optional):A function transform that takes in a image. Default: None.
        target_transform(callable, optional):A function transform that takes in a label. Default: None.
        batch_size(int): Batch size of dataset. Default: 64.
        resize(int, tuple): The output size of the resized image. If size is an integer, the smaller edge of the
        image will be resized to this value with the same image aspect ratio. If size is a sequence of length 2,
        it should be (height, width). Default: 224.
        repeat_num(int): The repeat num of dataset. Default: 1.
        shuffle(bool, optional): Whether or not to perform shuffle on the dataset. Default: None.
        download(bool): Whether to download the dataset. Default: False.
        mr_file(str, optional): The path of mindrecord files. Default: False.
        columns_list(tuple): The column name of output data. Default: ('image', 'image_id', "label").
        num_parallel_workers(int, optional): Number of subprocess used to fetch the dataset in parallel.Default: None.
        num_shards(int, optional): Number of shards that the dataset will be divided into. Default: None.
        shard_id(int, optional): The shard ID within num_shards. Default: None.
    """

    def __init__(self,
                 path: str,
                 anno_file: str,
                 split: str = "train",
                 transform: Optional[Callable] = None,
                 target_transform: Optional[Callable] = None,
                 batch_size: int = 64,
                 resize: Union[Tuple[int, int], int] = 300,
                 repeat_num: int = 1,
                 shuffle: Optional[bool] = None,
                 download: bool = False,
                 mr_file: Optional[str] = None,
                 columns_list: Tuple = ('image', 'image_id', "label"),
                 num_parallel_workers: int = 1,
                 num_shards: Optional[int] = None,
                 shard_id: Optional[int] = None) -> None:
        Validator.check_string(split, ["train", "val", "infer"], "split")

        if split != "infer":
            self.is_crowd = split == "train"
            self.parse_coco = ParseCOCO(path=path,
                                        anno_file=anno_file,
                                        is_crowd=self.is_crowd,
                                        mr_file=mr_file)
            load_data = self.parse_coco.parse_dataset
        else:
            load_data = read_dataset

        super(COCO, self).__init__(path=path,
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
                                   columns_list=columns_list)
        self.anno_file = anno_file

    def index2label(self):
        """
        Get the mapping of indexes and labels
        """
        parse_coco = ParseCOCO(path=self.path, anno_file=self.anno_file)

        return parse_coco.categories

    def download_dataset(self):
        raise ValueError("COCO dataset download is not supported.")

    def default_transform(self):
        mean = [0.485 * 255, 0.456 * 255, 0.406 * 255]
        std = [0.229 * 255, 0.224 * 255, 0.225 * 255]

        if self.split == "train":
            # Define map operations for training dataset
            trans = [
                transforms.RandomCropDecodeResize(size=self.resize,
                                                  scale=(0.08, 1.0),
                                                  ratio=(0.75, 1.333)),
                transforms.Normalize(mean=mean, std=std),
                transforms.HWC2CHW()
            ]
        else:
            # Define map operations for inference dataset
            trans = [
                transforms.Decode(),
                transforms.Resize((self.resize, self.resize)),
                transforms.Normalize(mean=mean, std=std),
                transforms.HWC2CHW()
            ]

        return trans


class ParseCOCO(ParseDataset):
    """
    Parse COCO2017 dataset.

    Args:
        anno_file(str): The path of COCO annotations file.
        is_crowd(bool): Whether to use the crowd images. Default: False.
        mr_file(str): The path of mindrecord files. Default: None.
    """

    def __init__(self,
                 path: str,
                 anno_file: str,
                 is_crowd: bool = False,
                 mr_file: Optional[str] = None) -> None:
        super(ParseCOCO, self).__init__(path=path)
        self.data_path = "train2017" if "train" in os.path.split(anno_file)[-1] else "val2017"
        self.mr_file = mr_file
        self.iscrowd = is_crowd
        self.coco = cocotools(anno_file)
        self.ids = self.__filter_ids(list(sorted(self.coco.imgs.keys())))
        self.categories = {cat["id"]: cat["name"] for cat in self.coco.cats.values()}

    def __filter_ids(self, ids):
        """Filter the images whose bboxes are all crowd."""
        new_ids = []

        for i in ids:
            target = self.coco.loadAnns(self.coco.getAnnIds(i))
            is_all_crowd = [1 for ti in target if not (ti["iscrowd"] and not self.iscrowd)]

            if not is_all_crowd:
                continue

            new_ids.append(i)

        return new_ids

    def __xywh2xyxy(self, bbox):
        """xywh convert into xyxy format."""
        x_min = bbox[0]
        y_min = bbox[1]
        w = bbox[2]
        h = bbox[3]
        return [x_min, y_min, x_min + w, y_min + h]

    def __parse_annos(self):
        """Parse annotations."""
        targets = []
        pad_max_number = 128

        for i in self.ids:
            target = self.coco.loadAnns(self.coco.getAnnIds(i))
            bboxes = []
            labels = []

            for ti in target:

                # Filter the image's bbox which is crowd.
                if ti["iscrowd"] and not self.iscrowd:
                    continue

                # Transform the format of bbox
                bboxes.append(self.__xywh2xyxy(ti["bbox"]))
                labels.append(ti["category_id"])

            bboxes = np.pad(np.array(bboxes),
                            ((0, pad_max_number - len(bboxes)), (0, 0)),
                            mode="constant",
                            constant_values=0)
            labels = np.pad(np.array(labels),
                            ((0, pad_max_number - len(labels)),),
                            mode="constant",
                            constant_values=-1)
            trans_targt = np.hstack((bboxes, labels[:, np.newaxis]))
            targets.append(trans_targt)

        return targets

    def __parse_img(self):
        imgs = [
            os.path.join(self.path, self.data_path, self.coco.loadImgs(i)[0]["file_name"])
            for i in self.ids
        ]
        img_ids = [self.coco.loadImgs(i)[0]["id"] for i in self.ids]
        return imgs, img_ids

    def __trans_to_mr(self, mr_file):
        # to do
        return mr_file

    def parse_dataset(self):
        """Parse data from COCO dataset file"""
        # Parse the dataset
        imgs, img_ids = self.__parse_img()
        annos = self.__parse_annos()

        # Transform dataset to mindrecord files
        if self.mr_file:
            self.__trans_to_mr(self.mr_file)

        return imgs, img_ids, annos
