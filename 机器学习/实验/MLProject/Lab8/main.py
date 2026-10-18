import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_iris
from sklearn.decomposition import PCA
import matplotlib
# matplotlib.rcParams['font.family'] = 'SimHei'

def self_pca(data, n_components):
    # 每个样本特征减去特征的平均值
    data = data - np.mean(data, axis=0, keepdims=True)
    # m为样本数
    m, _ = data.shape
    # 计算协方差矩阵
    cov_mat = 1.0 / m * np.matmul(data.T, data)
    print(cov_mat.shape) # shape[4,4]
    # 计算协方差矩阵特征值及其对应的特征向量
    eig_values, eig_vector = np.linalg.eig(cov_mat)
    print(eig_values)
    # 对特征值进行排序，获取前n_components组特征的索引
    _index = np.argsort(-eig_values)[:n_components]
    # 获取对应的特征向量
    picked_eig_vector = eig_vector[:, _index]
    # 处理原数据集
    data_ndim = np.matmul(data, picked_eig_vector)
    print(data_ndim.shape)
    return data_ndim



def main():
    X = np.array(load_iris()['data'])
    y = np.array(load_iris()['target'])
    print(X.shape)
    print(y.shape)
    # pca_line = PCA().fit(X)
    # plt.plot([1, 2, 3, 4], np.cumsum(pca_line.explained_variance_ratio_))
    # plt.xticks([1, 2, 3, 4])
    # plt.xlabel("降维后的特征数量")
    # plt.ylabel("可解释方差贡献率")
    # plt.show()

    data_2d1 = self_pca(X, n_components=2)
    # plt.figure(figsize=(15, 4))
    # plt.subplot(121)
    plt.title("my_pca")
    plt.scatter(data_2d1[:, 0], data_2d1[:, 1], c=y)
    plt.show()

    sklearn_pca = PCA(n_components=2)
    data_2d2 = sklearn_pca.fit_transform(X)
    # plt.subplot(122)
    plt.title("sklearn_pca")
    plt.scatter(data_2d2[:, 0], data_2d2[:, 1], c=y)
    plt.show()



if __name__ == '__main__':
    main()