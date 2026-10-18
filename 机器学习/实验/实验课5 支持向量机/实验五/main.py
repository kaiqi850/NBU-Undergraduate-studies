import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.preprocessing import StandardScaler
from sklearn import metrics
pd.set_option('display.max_columns',None)

data = pd.read_csv('./data.csv')
print(data.columns)
print(data.describe())

feature_mean = list(data.columns[2:12])
feature_se = list(data.columns[12:22])
feature_worst = list(data.columns[22:32])
feature_mean,feature_se,feature_worst

data.drop('id', axis=1, inplace=True)
data['diagnosis']=data['diagnosis'].map({'M':1,'B':0})
sns.countplot(data['diagnosis'],label='count')
plt.show()

corr = data[feature_mean].corr()
# corr = data[feature_se].corr()
# corr = data[feature_worst].corr() # 每类特征都进行绘图分析
plt.figure(figsize=(14,14))
sns.heatmap(corr, annot=True)
plt.show()

feature_remain = ['radius_mean','texture_mean','smoothness_mean','compactness_mean','symmetry_mean','fractal_dimension_mean']
train, test = train_test_split(data, test_size=0.2)

train_X = train[feature_remain]
train_y = train['diagnosis']
test_X = test[feature_remain]
test_y = test['diagnosis']

print(train_X['radius_mean'].std(), train_X['radius_mean'].mean())
ss = StandardScaler()
train_X = ss.fit_transform(train_X)
test_X = ss.fit_transform(test_X)
print(train_X[:,0].std(), train_X[:,0].mean())

model = svm.SVC(kernel='rbf',C=0.3,degree=3)
model.fit(train_X,train_y)

prediction = model.predict(test_X)
print('acc:',metrics.accuracy_score(prediction,test_y))
