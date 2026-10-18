import sklearn
import matplotlib.pyplot as plt
from sklearn import model_selection, linear_model, metrics
import pandas as pd
import numpy as np

# 读取数据
excel_name = "./西瓜数据集2.xlsx"
data = pd.read_excel(excel_name)

# 提取特征和目标变量
x = data.iloc[:, 1:3].values
y = data.iloc[:, 3].values


# 拆分训练集和测试集
x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.1, shuffle=True)

# 训练线性回归模型
L = linear_model.LinearRegression()
L.fit(x_train, y_train)

# 预测训练集
y_train_predict = L.predict(x_train)

# 绘图
plt.figure(figsize=(8, 5))  # 调整画布大小
plt.plot(range(len(y_train)), y_train, 'b-', label="true")  # 蓝色实线
plt.plot(range(len(y_train_predict)), y_train_predict, 'r--', label="predict")  # 红色虚线

# 添加标题、图例、坐标轴标签
plt.xlabel("sample")
plt.ylabel("values")
plt.title("train")
plt.legend()
plt.grid(True)  # 添加网格线
plt.show()

# 测试集预测
y_test_predict = L.predict(x_test)
print(y_test_predict)
print(y_test)

# 计算误差
err = metrics.mean_squared_error(y_test_predict, y_test)
print(f"测试集损失为: {err}")
print("模型系数:", L.coef_)
