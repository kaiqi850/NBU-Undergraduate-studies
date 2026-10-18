import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

# 设置随机种子
rnd = np.random.RandomState(42)

# 生成训练集
x_train = rnd.uniform(-3, 3, size=100)
y_train = np.sin(x_train) + rnd.normal(size=len(x_train)) / 3

# 生成测试集
x_test = rnd.uniform(-3, 3, size=100)
y_test = np.sin(x_test) + rnd.normal(size=len(x_test)) / 3

# 数据转换为二维数组
x_train_reshape = x_train.reshape(-1, 1)
x_test_reshape = x_test.reshape(-1, 1)

# 生成 30 阶多项式特征
poly = PolynomialFeatures(degree=30)
x_train_poly = poly.fit_transform(x_train_reshape)
x_test_poly = poly.fit_transform(x_test_reshape)

# 训练线性回归模型
lr = LinearRegression()
lr.fit(x_train_poly, y_train)

# 预测结果
y_predict_train = lr.predict(x_train_poly)
y_predict_test = lr.predict(x_test_poly)

# 创建 1 行 2 列的子图
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 绘制训练集结果
axes[0].scatter(x_train, y_train, color='k', label='Train Points')
axes[0].plot(np.sort(x_train), y_predict_train[np.argsort(x_train)], linewidth=2, color='g', label='Train Regression')
axes[0].set_title("Train Dataset & Regression")
axes[0].set_xlabel("x")
axes[0].set_ylabel("y")
axes[0].legend(loc="best")

# 绘制测试集结果
axes[1].scatter(x_test, y_test, color='r', label='Test Points')
axes[1].plot(np.sort(x_test), y_predict_test[np.argsort(x_test)], linewidth=2, color='b', label='Test Regression')
axes[1].set_title("Test Dataset & Regression")
axes[1].set_xlabel("x")
axes[1].set_ylabel("y")
axes[1].legend(loc="best")

# 调整子图布局
plt.tight_layout()
plt.show()
