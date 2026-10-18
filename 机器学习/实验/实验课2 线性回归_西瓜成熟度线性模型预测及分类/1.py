import sklearn
import matplotlib.pyplot as plt
from sklearn import model_selection
from sklearn import linear_model #导入线性回归模型
from sklearn import metrics#导入模型度量
import xlrd
import pandas as pd
from sklearn.linear_model import LinearRegression

excel_file = '西瓜数据集.xlsx'
data = pd.read_excel(excel_file)

data = data.iloc[:, 1:]  # 去掉第一列

# 假设最后一列是目标变量，其他列是特征
x = data.iloc[:, :-1]  # 取所有行，去掉最后一列作为特征
y = data.iloc[:, -1]   # 取所有行，最后一列作为目标变量

x_train,x_test,y_train,y_test = model_selection.train_test_split(x,y,test_size=0.2)

L_R = LinearRegression()
L_R.fit(x_train,y_train)

y_train_predict = L_R.predict(x_train)
plt.plot([i for i in range(len(y_train_predict))],y_train_predict)
plt.plot([i for i in range(len(y_train))],y_train)
plt.show()