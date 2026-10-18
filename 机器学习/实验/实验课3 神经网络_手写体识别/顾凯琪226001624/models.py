import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np


# 卷积层使用 torch.nn.Conv2d
# 激活层使用 torch.nn.ReLU
# 池化层使用 torch.nn.MaxPool2d
# 全连接层使用 torch.nn.Linear

class LeNet(nn.Module):
    def __init__(self, num_classes=10):
        super(LeNet, self).__init__()
        self.conv1 = nn.Sequential(nn.Conv2d(in_channels=1, out_channels=6, kernel_size=3, stride=1, padding=2),
                                   nn.ReLU(),
                                   nn.MaxPool2d(kernel_size=2))

        # 第一组卷积核
        self.conv2_1_1 = nn.Sequential(nn.Conv2d(in_channels=3, out_channels=1, kernel_size=5)
                                       , nn.ReLU())
        self.conv2_1_2 = nn.Sequential(nn.Conv2d(in_channels=4, out_channels=1, kernel_size=5)
                                       , nn.ReLU())
        self.conv2_1_3 = nn.Sequential(nn.Conv2d(in_channels=4, out_channels=1, kernel_size=5)
                                       , nn.ReLU())
        self.conv2_1_4 = nn.Sequential(nn.Conv2d(in_channels=6, out_channels=1, kernel_size=5))

        self.conv3 = nn.Sequential(nn.ReLU(),
                                   nn.MaxPool2d(kernel_size=2))

        self.fc1 = nn.Sequential(nn.Linear(16 * 5 * 5, 120),
                                 # 数据归一化处理
                                 nn.BatchNorm1d(120),
                                 nn.ReLU())

        self.fc2 = nn.Sequential(
            nn.Linear(120, 84),
            nn.BatchNorm1d(84),
            nn.ReLU(),
            nn.Linear(84, num_classes))
        # 最后的结果一定要变为 10，因为数字的选项是 0 ~ 9

    def forward(self, x):
        # print(x.shape)
        x = self.conv1(x)
        # print(x.shape)
        x_0, x_1, x_2, x_3, x_4, x_5 = x.split(1, dim=1)
        # print(x_0.shape)
        out_1_0 = self.conv2_1_1(torch.cat((x_0, x_1, x_2), 1))
        out_1_1 = self.conv2_1_1(torch.cat((x_1, x_2, x_3), 1))
        out_1_2 = self.conv2_1_1(torch.cat((x_2, x_3, x_4), 1))
        out_1_3 = self.conv2_1_1(torch.cat((x_3, x_4, x_5), 1))
        out_1_4 = self.conv2_1_1(torch.cat((x_4, x_5, x_0), 1))
        out_1_5 = self.conv2_1_1(torch.cat((x_5, x_0, x_1), 1))
        out_1 = torch.cat((out_1_0, out_1_1, out_1_2, out_1_3, out_1_4, out_1_5), 1)
        # print("第一组操作结束时维度：",out_1.shape)

        out_2_0 = self.conv2_1_2(torch.cat((x_0, x_1, x_2, x_3), 1))
        out_2_1 = self.conv2_1_2(torch.cat((x_1, x_2, x_3, x_4), 1))
        out_2_2 = self.conv2_1_2(torch.cat((x_2, x_3, x_4, x_5), 1))
        out_2_3 = self.conv2_1_2(torch.cat((x_3, x_4, x_5, x_0), 1))
        out_2_4 = self.conv2_1_2(torch.cat((x_4, x_5, x_0, x_1), 1))
        out_2_5 = self.conv2_1_2(torch.cat((x_5, x_0, x_1, x_2), 1))
        out_2 = torch.cat((out_2_0, out_2_1, out_2_2, out_2_3, out_2_4, out_2_5), 1)
        # print("第二组操作结束时维度：", out_2.shape)

        out_3_0 = self.conv2_1_3(torch.cat((x_0, x_1, x_3, x_4), 1))
        out_3_1 = self.conv2_1_3(torch.cat((x_1, x_2, x_4, x_5), 1))
        out_3_2 = self.conv2_1_3(torch.cat((x_2, x_3, x_5, x_0), 1))
        out_3 = torch.cat((out_3_0, out_3_1, out_3_2), 1)
        # print("第三组操作结束时维度：", out_3.shape)

        out_4 = self.conv2_1_4(x)
        # print("第四组操作结束时维度：", out_4.shape)

        x = torch.cat((out_1, out_2, out_3, out_4), 1)
        # print(x.shape)

        x = self.conv3(x)
        # print(x.shape)
        x = x.view(x.size()[0], -1)
        # print(x.shape)
        x = self.fc1(x)
        # print(x.shape)
        x = self.fc2(x)
        # print(x.shape)
        return x
