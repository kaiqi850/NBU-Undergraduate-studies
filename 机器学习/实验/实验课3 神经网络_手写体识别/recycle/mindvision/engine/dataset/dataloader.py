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
# ==============================================================================
"""The module is used to load transforms pipeline of dataset."""

from typing import Dict

import cv2
import mindspore.dataset as ds

from mindvision.engine.dataset.builder import build_transforms, build_dataset_sampler, build_dataset
from mindvision.check_param import Validator


class DataLoader:
    """
    The dataset loader.

    Args:
        dataset: dataset object
        map_cfg(dataload_cfg): Config for ds.map().
        batch_cfg(dataload_cfg): Config for ds.batch().
        config(dataload_cfg): The data loader config dict.

    Examples:
        >>> dataloader = DataLoader(ds, map, batch, cfg)
        >>> ds = dataloder()
    """

    def __init__(self,
                 dataset,
                 map_cfg=None,
                 batch_cfg=None,
                 config=None,
                 maps_cfg=None):
        """Constructor for Dataloader"""
        self.dataset = dataset
        self.map_cfg = map_cfg
        self.maps_cfg = maps_cfg
        self.batch_cfg = batch_cfg
        self.config = config
        self.map_ops = None
        self.maps_ops = None
        self.per_batch_map = None

        if self.map_cfg and self.map_cfg.operations:
            self.map_ops = build_transforms(self.map_cfg.operations)

        if self.batch_cfg and self.batch_cfg.per_batch_map:
            self.per_batch_map = build_transforms(self.batch_cfg.per_batch_map)

        if self.maps_cfg:
            self.maps_ops = build_transforms(self.maps_cfg.operations)

    def __call__(self):
        """Generate MindSpore dataset object."""
        if self.config.thread_num and self.config.thread_num >= 0:
            cv2.setNumThreads(self.config.thread_num)

        if self.config.prefetch_size:
            ds.config.set_prefetch_size(self.config.prefetch_size)

        if self.maps_ops:
            for op, cfg in zip(self.maps_ops, self.maps_cfg.configs):
                dataset = self.dataset.map(operations=op, **cfg)

        if self.map_ops:
            self.map_cfg.pop('operations')
            dataset = self.dataset.map(operations=self.data_augment, **self.map_cfg)

        if self.per_batch_map:
            self.batch_cfg.pop('per_batch_map')
            dataset = dataset.batch(per_batch_map=self.per_batch_map, **self.batch_cfg)
        else:
            if self.batch_cfg.get('max_instance_count') is not None:
                max_instance_count = self.batch_cfg.pop('max_instance_count')
                self.batch_cfg['pad_info'] = {"mask": ([max_instance_count, None, None], 0)}
            dataset = dataset.batch(**self.batch_cfg)
        return dataset

    def data_augment(self, *args):
        """Data augmentation function."""
        if len(self.map_cfg.input_columns) == 1:
            result = args[0]
        else:
            result = args
        for op in self.map_ops:
            result = op(result)
        return result


def build_dataloader(cfg: Dict, types: str) -> DataLoader:
    """
    Build dataset loading class.

    Args:
        cfg(dict): The data loader config dict.
        types(str): The types are train, eval, infer.

    Returns:
        DataLoader object.
    """
    Validator.check_string(types, ["train", "eval", "infer"], "types")
    type_config = {'train': cfg.train, 'eval': cfg.eval, 'infer': cfg.infer}
    config = type_config.get(types)

    # Any data source convert to mindrecord.
    if config.mindrecord:
        x2mindrecord = build_dataset(config.mindrecord)
        x2mindrecord()
    # Used for custom dataset source.
    if config.dataset.source and config.dataset.source.type:
        config.dataset.source = build_dataset(config.dataset.source)

    # Init custom dataset sampler, sampler use for custom dataset source.
    if config.dataset.source and config.dataset.sampler:
        config.dataset.sampler.dataset_size = len(config.dataset.source)
        config.dataset.sampler = build_dataset_sampler(config.dataset.sampler)

    # Generate dataset object.
    if not (config.map.input_columns or config.maps):
        transform = {"transform": build_transforms(config.map.operations)}
        dataset = build_dataset(config.dataset, default_args=transform)
    else:
        dataset = build_dataset(config.dataset)

    if hasattr(dataset, 'run'):
        return dataset.run()

    # Init dataset loader.
    dataset_loader = DataLoader(dataset, config.map, config.batch, cfg, maps_cfg=config.maps)

    return dataset_loader
