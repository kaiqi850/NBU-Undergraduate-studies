import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import cv2 as cv2
from Model1 import image_cut


def get_file(abs_path):
    filenames = os.listdir(abs_path)
    path_list = []
    for file in filenames:
        if not file.startswith('.'):
            path_list.append(os.path.join(abs_path, file))
    return path_list


# 索引库图像聚类
def cluster_index(file_list):
    # 从文件列表中提取对应图片文件的特征
    features = []
    for file in file_list:
        img = cv2.imread(file)
        # print(img)
        cut_images = image_cut(img, 32, 32)
        for i in range(cut_images.shape[0]):
            cut_img = cut_images[i, :, :, :]
            feature = cut_img.flatten()
            feature = feature - np.mean(cut_img)
            features.append(feature)
    X = np.array(features)  # 特征向量  N*3072
    print(X.shape)
    # 样本可视化绘图
    '''
    plt.figure(1)
    plt.scatter(X[:,0],X[:,1],c='red',marker='o', label='see')
    plt.xlabel('petal length')
    plt.ylabel('petal width')
    plt.legend(loc=2)
    plt.show()
    '''
    # 根据轮廓系数寻找最优簇数
    # sil = []
    # kl = []
    # kmax = 4  # 设置最大的K值
    # for k in range(50, 60):
    #     kMeans = KMeans(n_clusters=k).fit(X)  # 以k为聚类K值构造分类器进行聚类
    #     labels = kMeans.labels_  # 获取聚类标签
    #     sil.append(silhouette_score(X, labels, metric='euclidean'))  # 计算当前K值下的轮廓系数
    #     kl.append(k)
    #     # print(k)
    # bestK = kl[sil.index(max(sil))]
    # # print('bestK',bestK)

    # 根据最优簇数K进行Kmean聚类
    # bestK=1000
    kmeans = KMeans(n_clusters=200, max_iter=1000000)
    kmeans.fit(X)
    label_result = kmeans.labels_
    center_result = kmeans.cluster_centers_

    # 函数返回聚类标签与簇心
    return label_result, center_result


def work(in_path, outpath):
    path_list = get_file(in_path)
    label_result, center_result = cluster_index(path_list)
    data = pd.DataFrame(center_result)  # 簇心的簇新坐标（1024维）
    data.to_csv(outpath)


def kmean_solve():
    # 索引库路径
    source_path = r'G:\DLData\Flicker1024\Test Picture'
    # 簇心数据输出路径（相对路径）
    out_csv_path = './resources/center_result_s.csv'
    work(source_path, out_csv_path)


if __name__ == "__main__":
    kmean_solve()
