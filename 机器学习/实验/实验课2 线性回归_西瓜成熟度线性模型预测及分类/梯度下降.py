import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import model_selection

class LogisticRegressionGD:
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.learning_rate = learning_rate  # 学习率
        self.n_iterations = n_iterations    # 迭代次数
        self.weights = None                 # 权重
        self.bias = None                    # 偏置
        self.losses = []                    # 用于记录每次迭代的损失

    def sigmoid(self, z):
        # Sigmoid函数
        return 1 / (1 + np.exp(-z))

    def compute_loss(self, X, y):
        # 计算交叉熵损失
        n_samples = len(y)
        y_predicted = self.sigmoid(np.dot(X, self.weights) + self.bias)
        # 防止对数运算中的log(0)出现
        epsilon = 1e-15
        y_predicted = np.clip(y_predicted, epsilon, 1 - epsilon)
        loss = -(1 / n_samples) * np.sum(y * np.log(y_predicted) + (1 - y) * np.log(1 - y_predicted))
        return loss

    def fit(self, X, y):
        n_samples, n_features = X.shape          # 样本数量和特征数量
        self.weights = np.zeros(n_features)      # 初始化权重
        self.bias = 0                            # 初始化偏置

        # 梯度下降
        for i in range(self.n_iterations):
            linear_model = np.dot(X, self.weights) + self.bias          # 计算线性模型
            y_predicted = self.sigmoid(linear_model)                    # 计算预测值

            # 计算梯度
            dw = (1 / n_samples) * np.dot(X.T, (y_predicted - y))       # 计算权重的梯度
            db = (1 / n_samples) * np.sum(y_predicted - y)              # 计算偏置的梯度

            # 更新参数
            self.weights -= self.learning_rate * dw                     # 更新权重
            self.bias -= self.learning_rate * db                        # 更新偏置

            # 记录损失值
            if i % 100 == 0:
                loss = self.compute_loss(X, y)
                self.losses.append(loss)
                print(f"Iteration {i}, Loss: {loss}")

    def predict(self, X):
        linear_model = np.dot(X, self.weights) + self.bias             # 计算线性模型
        y_predicted = self.sigmoid(linear_model)                       # 计算预测值
        y_predicted_cls = [1 if i > 0.5 else 0 for i in y_predicted]   # 将概率值转换为类别
        return np.array(y_predicted_cls)                               # 返回预测类别

    def plot_loss(self):
        # 绘制损失变化曲线
        plt.plot(range(0, len(self.losses)*100, 100), self.losses, color='red')
        plt.title('Loss Function During Training')
        plt.xlabel('Iterations (x100)')
        plt.ylabel('Loss')
        plt.show()

    def plot_decision_boundary(self, X, y):
        # 绘制决策边界
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1

        xx, yy = np.meshgrid(np.arange(x_min, x_max, 0.01),
                             np.arange(y_min, y_max, 0.01))

        Z = self.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        plt.contourf(xx, yy, Z, alpha=0.75, cmap=plt.cm.coolwarm)
        plt.scatter(X[:, 0], X[:, 1], c=y, s=30, edgecolor='k', cmap=plt.cm.coolwarm)
        plt.title('Logistic Regression Decision Boundary')
        plt.show()

if __name__ == '__main__':
    # 读取数据
    excel_name = "西瓜数据集.xlsx"
    data = pd.read_excel(excel_name)

    # 提取特征和目标变量
    x = data[data.columns[1:3]].values
    y = data[data.columns[3]].values

    # 拆分训练集和测试集
    x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.1, shuffle=True)

    # 创建模型并训练
    model = LogisticRegressionGD(learning_rate=0.01, n_iterations=1000)
    model.fit(x_train, y_train)

    # 进行预测
    predictions = model.predict(x_test)
    print("预测结果:", predictions)
    print("真实结果:", y_test)

    # 输出交叉熵损失
    final_loss = model.compute_loss(x_test, y_test)
    print(f"最终交叉熵损失: {final_loss}")

    # 输出模型系数
    print("模型系数 (权重):", model.weights)
    print("模型偏置:", model.bias)

    # 绘制损失函数变化曲线
    model.plot_loss()

    # 如果特征是二维的，绘制决策边界
    model.plot_decision_boundary(x_train, y_train)
