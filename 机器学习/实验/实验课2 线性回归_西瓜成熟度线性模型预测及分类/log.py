import pandas as pd
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

# 读取数据
excel_name = "./西瓜数据集.xlsx"
data = pd.read_excel(excel_name)

# 提取特征和目标变量
x = data[data.columns[1:3]].values
y = data[data.columns[3]].values

# 拆分训练集和测试集
x_train, x_test, y_train, y_test = model_selection.train_test_split(x, y, test_size=0.1, shuffle=True)

# 使用逻辑回归模型
L = LogisticRegression(max_iter=200)
L.fit(x_train, y_train)

# 预测测试集
y_predict = L.predict(x_test)

# 输出预测结果与真实结果
print("预测结果:", y_predict)
print("真实结果:", y_test)

# 计算并输出准确率
accuracy = metrics.accuracy_score(y_test, y_predict)
print(f"准确率: {accuracy}")

# 计算并输出交叉熵损失
log_loss = metrics.log_loss(y_test, L.predict_proba(x_test))
print(f"交叉熵损失: {log_loss}")

# 输出模型系数
print("模型系数:", L.coef_)
