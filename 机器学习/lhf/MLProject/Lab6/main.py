import numpy as np
import pandas as pd
from math import *


# P(c)
def pre_prob(datasets):
    pos_prob = 1.0 * (np.sum(datasets[:, -1] == 1.0) + 1) / (np.shape(datasets)[0] + 2)
    neg_prob = 1.0 * (np.sum(datasets[:, -1] == 0.0) + 1) / (np.shape(datasets)[0] + 2)
    return [pos_prob, neg_prob]


def cond_attr_prob(datasets, test_data):
    # shape[属性数,类别数]，表示P(x_i|c)
    cond_result = np.zeros([np.shape(datasets)[1] - 1, 2])
    pos_data = datasets[datasets[:, -1] == 1.0, :]
    neg_data = datasets[datasets[:, -1] == 0.0, :]
    for i in range(6):
        # P(x_i|1)
        cond_result[i, 1] = 1.0 * (np.sum(pos_data[:, i] == test_data[0, i]) + 1) / (np.sum(datasets[:, -1] == 1.0) + 2)
        # P(x_i|0)
        cond_result[i, 0] = 1.0 * (np.sum(neg_data[:, i] == test_data[0, i]) + 1) / (np.sum(datasets[:, -1] == 0.0) + 2)
    for i in range(6, 8):
        pos_mean = np.mean(datasets[(datasets[:, -1] == 1.0), i])
        pos_std = np.std(datasets[(datasets[:, -1] == 1.0), i])
        neg_mean = np.mean(datasets[(datasets[:, -1] == 0.0), i])
        neg_std = np.std(datasets[(datasets[:, -1] == 0.0), i])
        cond_result[i, 1] = 1.0 / (sqrt(2.0 * np.pi) * pos_std) * \
                            np.exp(-1 * (test_data[0, i] - pos_mean) ** 2 / (2 * pos_std ** 2))
        cond_result[i, 0] = 1.0 / (sqrt(2.0 * np.pi) * neg_std) * \
                            np.exp(-1 * (test_data[0, i] - neg_mean) ** 2 / (2 * neg_std ** 2))
    return cond_result


def classify_data(cond_result, pre_result):
    pos_result = pre_result[1]
    neg_result = pre_result[0]
    for i in range(np.shape(cond_result)[0]):
        pos_result *= cond_result[i, 1]
        neg_result *= cond_result[i, 0]
    if pos_result > neg_result:
        print('好瓜')
    else:
        print('坏瓜')
    print('好瓜分数：', pos_result)
    print('坏瓜分数：', neg_result)


def main():
    df_train = pd.read_csv('watermelon3_0_En.csv')
    train_data = df_train.to_numpy()[:, 1:]
    df_test = pd.read_csv('test.csv')
    test_data = df_test.to_numpy()[:, 1:]
    print('Train Data')
    print(train_data)
    print('Test Data')
    print(test_data)

    # 类先验概率计算
    pre_result = pre_prob(train_data)
    # 类条件概率计算
    cond_result = cond_attr_prob(train_data, test_data)
    # 分类
    classify_data(cond_result, pre_result)


if __name__ == '__main__':
    main()
