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
"""MindSpore Vision Classification training script."""

from mindspore import context, load_checkpoint, load_param_into_net
from mindspore.communication.management import init, get_rank, get_group_size
from mindspore.context import ParallelMode
from mindspore.nn.metrics import Accuracy
from mindspore.train import Model
from mindspore.train.callback import ModelCheckpoint, CheckpointConfig

from mindvision.check_param import Validator, Rel
from mindvision.classification.models.builder import build_classifier
from mindvision.engine.dataset.dataloader import build_dataloader
from mindvision.engine.loss.builder import build_loss
from mindvision.engine.lr_schedule.builder import build_lr_schedule
from mindvision.engine.optimizer.builder import build_optimizer
from mindvision.engine.callback import LossMonitor


def train_config(config):
    """Use yaml file for training."""
    context.set_context(**config.context)

    # Run distribute.
    if config.train.run_distribute:
        init()
        context.set_auto_parallel_context(device_num=get_group_size(),
                                          parallel_mode=ParallelMode.DATA_PARALLEL,
                                          gradients_mean=True)
        # Number of shards that the dataset will be divided into.
        config.data_loader.train.dataset.num_shards = get_group_size()
        # The shard ID within num_shards. This argument can only be specified when num_shards is also specified.
        config.data_loader.train.dataset.shard_id = get_rank()
        ckpt_save_dir = config.train.ckpt_path + "ckpt_" + str(get_rank()) + "/"
    else:
        ckpt_save_dir = config.train.ckpt_path

    # Data Pipeline.
    dataset_train = build_dataloader(config.data_loader, types='train')
    Validator.check_int(dataset_train.get_dataset_size(), 0, Rel.GT)

    # Create model.
    network = build_classifier(config.model)

    # Define loss function.
    network_loss = build_loss(config.loss)

    # Set lr scheduler.
    lr = build_lr_schedule(config.learning_rate)

    # Define optimizer.
    config.optimizer.params = network.trainable_params()
    config.optimizer.learning_rate = lr
    network_opt = build_optimizer(config.optimizer)

    # Load pretrained model.
    if config.train.pre_trained:
        param_dict = load_checkpoint(config.train.pretrained_model)
        load_param_into_net(network, param_dict)

    # Set the checkpoint config for the network.
    ckpt_config = CheckpointConfig(
        save_checkpoint_steps=config.train.save_checkpoint_steps,
        keep_checkpoint_max=config.train.keep_checkpoint_max)
    ckpt_callback = ModelCheckpoint(prefix=config.model_name,
                                    directory=ckpt_save_dir,
                                    config=ckpt_config)

    # Init the model.
    model = Model(network,
                  network_loss,
                  network_opt,
                  metrics={"Accuracy": Accuracy()})

    # Begin to train.
    model.train(config.train.epochs,
                dataset_train,
                callbacks=[ckpt_callback, LossMonitor(lr)],
                dataset_sink_mode=config.dataset_sink_mode)
