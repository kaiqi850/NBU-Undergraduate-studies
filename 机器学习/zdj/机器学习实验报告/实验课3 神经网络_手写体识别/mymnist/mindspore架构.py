import os
import time
import numpy as np
import mindspore
from mindspore import nn
from mindspore import context
from mindspore import Tensor
from mindspore.train.serialization import save_checkpoint
from mindspore.train.serialization import load_checkpoint
from mindspore.nn.metrics import Accuracy
from mindspore.nn.metrics import ConfusionMatrix
from mindspore.nn.metrics import Precision
from mindspore.nn.metrics import Recall
from mindspore.nn.metrics import F1
from mindspore.common.initializer import Normal
from mindspore.common.initializer import XavierUniform
from mindspore.ops import operations as P
from mindspore.common.parameter import Parameter
from mindspore.train.model import Model
from mindspore.train.callback import ModelCheckpoint
from mindspore.train.callback import CheckpointConfig
from mindspore.train.callback import LossMonitor
from mindspore.train.callback import SummaryCollector
from mindspore.dataset.transforms import py_transforms
from mindspore.dataset.transforms import vision
from mindspore.dataset import MnistDataset
from mindspore.dataset import batch
from mindspore.dataset import GeneratorDataset
from mindspore.dataset import dataset_to_iterator
from mindspore.common import dtype as mstype
from mindspore.ops import functional as F
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

context.set_context(mode=context.GRAPH_MODE, device_target="GPU", save_graphs=False)

summary_path = "runs/LeNet5"
num_classes = 10
batch_size = 8
save_checkpoint_path = "saved/"
save_model_name = "LeNet"


class LeNet5(nn.Cell):
    def __init__(self, num_class=10, num_channel=1):
        super(LeNet5, self).__init__()
        self.conv1 = nn.Conv2d(num_channel, 6, 5, pad_mode='valid')
        self.conv2 = nn.Conv2d(6, 16, 5, pad_mode='valid')
        self.fc1 = nn.Dense(16 * 5 * 5, 120, weight_init=XavierUniform(), bias_init=XavierUniform())
        self.fc2 = nn.Dense(120, 84, weight_init=XavierUniform(), bias_init=XavierUniform())
        self.fc3 = nn.Dense(84, num_class, weight_init=XavierUniform(), bias_init=XavierUniform())
        self.relu = nn.ReLU()
        self.max_pool2d = nn.MaxPool2d(kernel_size=2, stride=2)
        self.flatten = nn.Flatten()

    def construct(self, x):
        x = self.conv1(x)
        x = self.relu(x)
        x = self.max_pool2d(x)
        x = self.conv2(x)
        x = self.relu(x)
        x = self.max_pool2d(x)
        x = self.flatten(x)
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        return x


def create_dataset(data_path, batch_size=32, repeat_size=1,
                   num_parallel_workers=1):
    # define dataset
    mnist_ds = MnistDataset(data_path)
    # define map operations
    trans = [
        vision.Resize((32, 32)),
        vision.HWC2CHW(),
        vision.Normalize((0.1307,), (0.3081,)),
    ]
    # apply map operations on images
    mnist_ds = mnist_ds.map(operations=trans, input_columns="image", num_parallel_workers=num_parallel_workers)
    # apply repeat operations
    mnist_ds = mnist_ds.repeat(repeat_size)
    # apply batch operations
    mnist_ds = mnist_ds.batch(batch_size)
    return mnist_ds


def train_net(data_path, epoch_size, repeat_size, batch_size, save_checkpoint_path,
              save_model_name):
    ds_train_path = os.path.join(data_path, "train")
    mnist_ds = create_dataset(ds_train_path, batch_size=batch_size, repeat_size=repeat_size)
    net = LeNet5(num_class=num_classes)
    loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True, reduction='mean')
    opt = nn.Adam(params=net.trainable_params(), learning_rate=0.001)
    model = Model(net, loss, opt, metrics={"Accuracy": Accuracy()})
    time_cb = SummaryCollector(summary_dir=summary_path)
    ckpt_config = CheckpointConfig(save_checkpoint_steps=1875, keep_checkpoint_max=10)
    ckpt_cb = ModelCheckpoint(prefix="checkpoint_lenet", directory=save_checkpoint_path, config=ckpt_config)
    loss_cb = LossMonitor()
    callbacks = [time_cb, ckpt_cb, loss_cb]
    model.train(epoch_size, mnist_ds, callbacks=callbacks)
    save_checkpoint(net, os.path.join(save_checkpoint_path, save_model_name + ".ckpt"))


if __name__ == '__main__':
    train_net(data_path="mnist", epoch_size=10, repeat_size=1, batch_size=32,
              save_checkpoint_path=save_checkpoint_path, save_model_name=save_model_name)
