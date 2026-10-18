import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from openpyxl import load_workbook
import matplotlib.dates as mdates

# 读取Excel数据
excel_filename = "mqtt_data.xlsx"
workbook = load_workbook(excel_filename)
sheet = workbook.active

# 提取数据
timestamps = []
temperatures = []
humidities = []
for row in sheet.iter_rows(min_row=2):
    timestamps.append(row[0].value)  # 时间戳
    temperatures.append(row[1].value)  # 温度
    humidities.append(row[2].value)  # 湿度

# 将数据转换为DataFrame
data = pd.DataFrame({
    'Timestamp': timestamps,
    'Temperature': temperatures,
    'Humidity': humidities
})

# 使用温度和湿度数据进行预测
# 归一化数据
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data[['Temperature', 'Humidity']])

# 创建LSTM输入数据的函数
def create_dataset(data, time_step=1):
    X, y = [], []
    for i in range(len(data) - time_step):
        X.append(data[i:(i + time_step), :])
        y.append(data[i + time_step, 0])  # 预测温度
    return np.array(X), np.array(y)

# 使用过去60个时间步的数据来预测下一个时间步
time_step = 60
X, y = create_dataset(scaled_data, time_step)

# 拆分数据集为训练集和测试集
train_size = int(len(X) * 0.8)
test_size = len(X) - train_size
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# 转换为PyTorch的Tensor
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1, 1)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).view(-1, 1)

# 定义LSTM模型
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.fc = nn.Linear(hidden_layer_size, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1, :])
        return predictions

# 初始化模型
input_size = X_train.shape[2]  # 输入特征数
hidden_layer_size = 50        # 隐藏层大小
output_size = 1               # 输出特征数（温度）

model = LSTMModel(input_size, hidden_layer_size, output_size)

# 定义损失函数和优化器
loss_function = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 训练模型
epochs = 200
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    y_train_pred = model(X_train_tensor)
    loss = loss_function(y_train_pred, y_train_tensor)
    loss.backward()
    optimizer.step()
    print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item()}")

torch.save(model.state_dict(), 'temperature_lstm_model.pth')

# 进行预测
model.eval()
y_pred = model(X_test_tensor).detach().numpy()

# 反归一化预测数据和实际数据
y_pred_rescaled = scaler.inverse_transform(np.hstack((y_pred, np.zeros((y_pred.shape[0], 1)))) )
y_test_rescaled = scaler.inverse_transform(np.hstack((y_test.reshape(-1, 1), np.zeros((y_test.shape[0], 1)))) )

# 绘制图表
plt.figure(figsize=(10, 6))

# 绘制实际温度和预测温度
plt.plot(data['Timestamp'][len(data) - len(y_test):], y_test_rescaled[:, 0], color='blue', label='Actual Temperature')
plt.plot(data['Timestamp'][len(data) - len(y_pred):], y_pred_rescaled[:, 0], color='red', label='Predicted Temperature')

# 设置图表标题和标签
plt.xlabel('Timestamp')
plt.ylabel('Temperature (°C)')
plt.title('Temperature Prediction using LSTM (PyTorch)')

# 格式化 x 轴时间戳，设置每隔一定间隔显示一个时间戳
plt.xticks(rotation=45)

# 设置时间刻度显示间隔，最大显示数目为20个标签
plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))  # 每隔1小时显示一个时间戳
plt.gca().xaxis.set_minor_locator(mdates.MinuteLocator(interval=6))  # 每隔6小时显示一个次刻度
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))  # 时间戳格式

# 自动调整布局以避免标签重叠
plt.tight_layout()

# 显示图例
plt.legend()

# 展示图表
plt.show()
