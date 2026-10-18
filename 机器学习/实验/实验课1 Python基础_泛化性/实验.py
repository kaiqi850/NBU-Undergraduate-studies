import numpy as np
import matplotlib.pyplot as plt

# 生成 40 个样本，分成两类
np.random.seed(42)  # 保持结果可复现
num_samples = 40

# 生成第一类数据（20 个样本）
x1 = np.random.randn(20, 2) + [2, 2]  # 均值偏移

# 生成第二类数据（20 个样本）
x2 = np.random.randn(20, 2) + [-2, -2]  # 均值偏移

# 合并数据
X = np.vstack((x1, x2))
y = np.array([0] * 20 + [1] * 20)  # 类别标签

# 可视化
plt.scatter(X[:, 0], X[:, 1], c=y, cmap='coolwarm', edgecolors='k')
plt.title("Randomly Generated 2-Class Data (40 Samples)")
plt.xlabel("Feature 1")
plt.ylabel("Feature 2")
plt.show()
