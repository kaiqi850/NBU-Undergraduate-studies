import time
import os
from tqdm import tqdm
import logging
from models import LeNet
from torchvision import datasets, transforms
from tensorboardX import SummaryWriter
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import transforms
import warnings

# 忽略Warning
warnings.filterwarnings('ignore')

os.environ['CUDA_VISIBLE_DEVICES'] = '0'
Batch_size = 8
Save_path = "saved/"
Save_model = "LeNet"
Summary_path = r'runs/LeNet5'
Num_classes = 10
if not os.path.exists(Summary_path):
    os.mkdir(Summary_path)
writer = SummaryWriter(log_dir=Summary_path, purge_step=0)


def train():
    # train配置
    device = torch.device('cuda:0')
    model = LeNet(num_classes=Num_classes)
    # model = nn.DataParallel(model, device_ids=[0, 1])
    model.to(device)

    logger = initLogger("Mnist_LeNet")

    # loss
    criterion = nn.CrossEntropyLoss()

    # train data
    train_dataset = datasets.MNIST(root='.\mnist',
                                   train=True,
                                   transform=transforms.ToTensor(),  # 数据类型预处理，变成张量并归一化（/255）
                                   download=True)
    # 下载测试集
    val_dataset = datasets.MNIST(root='.\mnist',
                                 train=False,
                                 transform=transforms.ToTensor(),
                                 download=True)

    # 装载训练集
    train_loader = torch.utils.data.DataLoader(dataset=train_dataset,
                                               batch_size=Batch_size,
                                               shuffle=True)
    # 装载验证集
    val_loader = torch.utils.data.DataLoader(dataset=val_dataset,
                                             batch_size=Batch_size,
                                             shuffle=True)

    # optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001, weight_decay=0.0001)
    # 最优val准确率，根据这个保存模型
    val_max_OA = 0.0
    for epoch in range(100):
        # lr
        model.train()
        loss_sum = 0.0
        correct_sum = 0.0
        total = 0
        # train_loader为可迭代对象，ncols为自定义的进度条长度
        tbar = tqdm(train_loader, ncols=120)
        for batch_idx, (data, target) in enumerate(tbar):
            data = data.cuda()
            target = target.cuda()
            # data, target = data.to(device), target.to(device)
            optimizer.zero_grad()  # 清除梯度
            output = model(data)
            loss = criterion(output, target)
            loss_sum += loss.item()

            loss.backward()  # 反向传播，计算张量的梯度
            optimizer.step()  # 根据梯度更新网络参数
            # torch.max(x,dim=?) dim=0时返回每一列中最大值的那个元素的值和索引,dim=1时返回每一行中最大值的那个元素值和索引
            # 值无用，需要的是索引，也即0-9的标签，不用转化正好时标签
            # out输出10个类各自的概率，所以需要从每一条数据中取出最大的
            _, predicted = torch.max(output, 1)
            correct_sum += (predicted == target).sum()
            total += Batch_size
            oa = correct_sum.item() / total * 1.0
            # 轮次、损失总值、正确率
            tbar.set_description('TRAIN ({}) | Loss: {:.5f} | OA {:.5f} |'.format(
                epoch, loss_sum / ((batch_idx + 1) * Batch_size), oa))

        # 使用TensorBoard记录各指标曲线
        writer.add_scalar('train_loss', loss_sum / ((batch_idx + 1) * Batch_size), epoch)
        writer.add_scalar('train_oa', oa, epoch)

        # 每一轮次结束后记录运行日志
        logger.info('TRAIN ({}) | Loss: {:.5f} | OA {:.5f}'.format(
            epoch, loss_sum / ((batch_idx + 1) * Batch_size), oa))

        # val

        model.eval()
        loss_sum = 0.0
        correct_sum = 0.0
        total = 0
        tbar = tqdm(val_loader, ncols=120)
        class_precision = np.zeros(Num_classes)
        class_recall = np.zeros(Num_classes)
        class_f1 = np.zeros(Num_classes)
        # val_list=[]

        # data, target = data.to(device), target.to(device)
        with torch.no_grad():
            # 混淆矩阵
            conf_matrix_val = np.zeros((Num_classes, Num_classes))
            for batch_idx, (data, target) in enumerate(tbar):
                data = data.cuda()
                target = target.cuda()
                output = model(data)
                loss = criterion(output, target)
                loss_sum += loss.item()

                _, predicted = torch.max(output, 1)
                correct_sum += (predicted == target).sum()
                total += Batch_size

                oa = correct_sum.item() / total * 1.0

                c_predict = predicted.cpu().numpy()
                c_target = target.cpu().numpy()

                # 预测值为行标签、真值为列标签，类似两标签下的混淆矩阵
                '''
                        预测值
                真值  正      负
                正   TP      FN
                负   FN      TN
                '''
                for i in range(len(c_predict)):
                    conf_matrix_val[c_target[i], c_predict[i]] += 1
                for i in range(Num_classes):
                    # 每一类的precision
                    class_precision[i] = 1.0 * conf_matrix_val[i, i] / conf_matrix_val[:, i].sum()
                    # 每一类的recall
                    class_recall[i] = 1.0 * conf_matrix_val[i, i] / conf_matrix_val[i].sum()
                    # 每一类的f1
                    class_f1[i] = (2.0 * class_precision[i] * class_recall[i]) / (class_precision[i] + class_recall[i])

                tbar.set_description('VAL ({}) | Loss: {:.5f} | OA {:.5f} '.format(
                    epoch, loss_sum / ((batch_idx + 1) * Batch_size),
                    oa))
            # 保存最优oa对应的模型
            if oa > val_max_OA:
                val_max_OA = oa
                best_epoch = np.zeros(2)
                best_epoch[0] = epoch
                best_epoch[1] = conf_matrix_val.sum()
                if os.path.exists(Save_path) is False:
                    os.mkdir(Save_path)
                torch.save(model.state_dict(), os.path.join(Save_path, Save_model + '.pth'))
                np.savetxt(os.path.join(Save_path, Save_model + '_conf_matrix_val.txt'), conf_matrix_val, fmt="%d")
                np.savetxt(os.path.join(Save_path, Save_model + '_best_epoch.txt'), best_epoch, fmt="%d")

        writer.add_scalar('val_loss', loss_sum / ((batch_idx + 1) * Batch_size), epoch)
        writer.add_scalar('val_oa', oa, epoch)
        writer.add_scalar('Avarage_percision', class_precision.sum() / 10, epoch)
        writer.add_scalar('Avarge_recall', class_recall.sum() / 10, epoch)
        writer.add_scalar('Avarage_F1', class_f1.sum() / 10, epoch)

        logger.info('VAL ({}) | Loss: {:.5f} | OA {:.5f} |class_precision {}| class_recall {} | class_f1 {}|'.format(
            epoch, loss_sum / ((batch_idx + 1) * Batch_size),
            oa, toString(class_precision), toString(class_recall), toString(class_f1)))


def toString(IOU):
    result = '{'
    for i, num in enumerate(IOU):
        result += str(i) + ': ' + '{:.4f}, '.format(num)

    result += '}'
    return result


def initLogger(model_name):
    # 初始化log
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
    log_path = r'../logs'
    if not os.path.exists(log_path):
        os.mkdir(log_path)
    log_name = os.path.join(log_path, model_name + '_' + rq + '.log')
    logfile = log_name
    fh = logging.FileHandler(logfile, mode='w')
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


if __name__ == '__main__':
    train()
