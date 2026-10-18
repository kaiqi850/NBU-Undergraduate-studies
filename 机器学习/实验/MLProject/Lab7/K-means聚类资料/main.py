import numpy as np
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
# 实验给定的程序包
import utilities


def get_data():
    data, _ = utilities.load_data('data_multivar.txt')
    print(data)
    return data

def plot_data(data):
    x = data[:, 0]
    y = data[:, 1]
    plt.figure()
    plt.scatter(x, y, marker='o', facecolors='none', edgecolors='k', s=30)
    x_min, x_max = min(x) - 1, max(x) + 1
    y_min, y_max = min(y) - 1, max(y) + 1

    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    plt.title('Input Data')
    plt.show()

def kmean_train(data):
    # 初始化方法、簇的数目、初始化随机次数
    init_method = 'random'
    num_clusters = 6
    init_random_num = 10
    # 定义K-Means模型
    kmeans = KMeans(init=init_method, n_clusters=num_clusters, n_init=init_random_num)
    # 数据拟合
    kmeans.fit(data)
    # 绘图
    plt.figure()
    plt.clf()
    x = data[:, 0]
    y = data[:, 1]
    # 绘制原始数据图像
    plt.scatter(x, y, marker='o', facecolors='none', edgecolors='k', s=30)
    # 获取簇心数据
    center = kmeans.cluster_centers_
    # 对于簇心进行绘图
    plt.scatter(center[:, 0], center[:, 1], marker='o', s=100, linewidths=3, color='k', zorder=10, facecolors='red')
    # 数据范围
    x_min, x_max = min(x) - 1, max(x) + 1
    y_min, y_max = min(y) - 1, max(y) + 1
    # 调整绘图的数据范围
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    # 去除坐标刻度
    plt.xticks(())
    plt.yticks(())
    plt.title('KMeans init:{}, num_clusters:{}, n_init:{}'.format(init_method, num_clusters, init_random_num))
    # 网格粒度
    step_size = 0.01
    # 获取一个网格，根据数据范围进行生成
    x_values, y_values = np.meshgrid(np.arange(x_min, x_max, step_size), np.arange(y_min, y_max, step_size))
    # 对于网格上的每一个点传入训练好的K-Means进行分类
    predicted_labels = kmeans.predict(np.c_[x_values.ravel(), y_values.ravel()])
    # 将分类结果进行形状调整
    predicted_labels = predicted_labels.reshape(x_values.shape)
    # 绘图，与原数据图像一起
    plt.imshow(predicted_labels, interpolation='nearest',
               extent=(x_values.min(), x_values.max(), y_values.min(), y_values.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')
    plt.show()

def find_best_k(data):
    init_method = 'random'
    init_random_num = 10
    k_list = []
    scores = []
    # 定义K-Means模型
    for k in range(2, 10):
        # 聚类簇数为k
        kmeans = KMeans(init=init_method, n_clusters=k, n_init=init_random_num)
        # 拟合数据
        kmeans.fit(data)
        # 获取标签
        labels = kmeans.labels_
        # 计算轮廓系数
        scores.append(silhouette_score(data, labels))
        k_list.append(k)
    plt.plot(k_list, scores)
    plt.show()

if __name__ == '__main__':
    data = get_data()
    print(len(data))
    plot_data(data)
    kmean_train(data)
    find_best_k(data)
