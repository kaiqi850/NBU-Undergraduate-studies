import os
import gzip
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_digits

def load_mnist(path, kind='train'):
    label_path = os.path.join(path,'{}-labels-idx1-ubyte'.format(kind))
    image_path = os.path.join(path,'{}-images-idx3-ubyte'.format(kind))
    with open(label_path, 'rb') as lp:
        labels = np.frombuffer(lp.read(), dtype=np.uint8, offset=8)
    with open(image_path, 'rb') as ip:
        images = np.frombuffer(ip.read(), dtype=np.uint8, offset=16).reshape(len(labels), 784)
    return images, labels

def image_disp(data_list):
    for i in range(4):
        feature = data_list[i]
        image = feature.reshape(28, 28)
        plt.subplot(2, 2, i+1)
        plt.imshow(image)
        plt.axis('off')
        # plt.tight_layout()
    plt.show()

x_train, y_train = load_mnist('./FashionMNIST/', kind='train')
x_test, y_test = load_mnist('./FashionMNIST/', kind='t10k')



seed_value = 2025  #随机种子
model = RandomForestClassifier(random_state=seed_value)
model.fit(x_train, y_train)  #模型训练
# 在训练集、测试集上进行预测
y_train_pred = model.predict(x_train)
y_test_pred = model.predict(x_test)


acc_train = (y_train_pred == y_train).sum() / len(y_train)
acc_test = (y_test_pred == y_test).sum() / len(y_test)
acc_train, acc_test

from sklearn.linear_model import LogisticRegression
logistic = LogisticRegression()
logistic.fit(x_train, y_train)
y_train_pred_logistic = logistic.predict(x_train)
y_test_pred_logistic = logistic.predict(x_test)
acc_train_logistic = (y_train_pred_logistic == y_train).sum() / len(y_train)
acc_test_logistic = (y_test_pred_logistic == y_test).sum() / len(y_test)
acc_train_logistic, acc_test_logistic

from sklearn.model_selection import cross_val_score
# 调参，绘制学习曲线来调参n_estimators（对随机森林影响最大）子树的数量
score_lt = []
# 每隔10步建立一个随机森林，获得不同n_estimators的得分
for i in range(0,200,10):
    rfc = RandomForestClassifier(n_estimators=i+1, random_state=90)
    score = cross_val_score(rfc, x_train, y_train, cv=10).mean()
    score_lt.append(score)
    print(score)
score_max = max(score_lt)
print('最大得分：{}'.format(score_max),
      '子树数量为：{}'.format(score_lt.index(score_max)*10+1))
# 绘制学习曲线
x = np.arange(1,201,10)
plt.subplot(111)
plt.plot(x, score_lt, 'r-')
plt.show()




list=[
    0.7669166666666667,
    0.8629666666666667,
    0.87285,
    0.8769,
    0.8780333333333333,
    0.8806999999999998,
    0.8812666666666666,
    0.8821666666666665,
    0.8825166666666668,
    0.8830666666666666,
    0.8836166666666665,
    0.8839333333333335,
    0.8842166666666668,
    0.8844166666666666,
    0.8845500000000002,
    0.8852833333333333,
    0.8848499999999999,
    0.8848499999999999,
    0.8844166666666666,
    0.8848499999999999,
]

x = np.arange(1,201,10)
print(len(x))
plt.subplot(111)
plt.title('Tree Number and Predict Accuracy')
plt.xlabel('Tree Number')
plt.ylabel('Predict Accuracy')
plt.plot(x, list, 'b-')
plt.show()

# def main():
#     # 加载数据
#     digits = load_digits()
#     x = digits.data
#     y = digits.target
#
#     # 划分训练集和测试集
#     x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
#
#     # 创建随机森林分类器
#     rfc = RandomForestClassifier(n_estimators=100, random_state=42)
#
#     # 拟合模型
#     rfc.fit(x_train, y_train)
#
#     # 输出训练集和测试集准确率
#     print("随机森林训练集准确率：", rfc.score(x_train, y_train))
#     print("随机森林测试集准确率：", rfc.score(x_test, y_test))
#
#     # 交叉验证（并行处理，需要放在主函数中）
#     score = cross_val_score(rfc, x_train, y_train, cv=5, n_jobs=8).mean()
#     print("10折交叉验证得分：", score)
#
# if __name__ == "__main__":
#     main()