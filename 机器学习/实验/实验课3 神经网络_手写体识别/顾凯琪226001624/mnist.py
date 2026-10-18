# coding: utf-8
from mindvision.dataset import Mnist
import mindspore.nn as nn
from mindspore import Model
from mindspore.train.callback import ModelCheckpoint, CheckpointConfig
from mindvision.engine.callback import LossMonitor
from mindspore import load_checkpoint, load_param_into_net
import numpy as np
from mindspore import Tensor
import matplotlib.pyplot as plt
from mindspore.common.initializer import Normal

class LeNet5(nn.Cell):
    def __init__(self,num_class=10,num_channel=1):
        super(LeNet5,self).__init__()
        # 定义所需要的运算
        self.conv1 =nn.conv2d(num_channel,6,5,pad_mode='valid')
        self.conv2=nn.conv2d(6,16,5,pad_mode='valid')
        self.fcl=nn.Dense(16*5*5,120,weight_init=Normal(0.02))
        self.fc2 =nn.Dense(120,84,weight_init=Normal(0.02))
        self.fc3 =nn.Dense(84,num_class,weight_init=Normal(0.02))
        self.relu =nn.ReLu()
        self.max_poo12d=nn.MaxPoo12d(kernel_size=2,stride=2)
        self.flatten=nn.Flatten()
    def construct(self,x):
        # 使用定义好的运算构建前向网络
        x= self.conv1(x)
        x= self.relu(x)
        x= self.max_poo12d(x)
        x= self.conv2(x)
        x= self.relu(x)
        x= self.max_poo12d(x)
        x= self.flatten(x)
        x= self.fcl(x)
        x= self.relu(x)
        x= self.fc2(x)
        x= self.relu(x)
        x= self.fc3(x)
        return x
network =LeNet5

if __name__ == '__main__':
    print("666")
