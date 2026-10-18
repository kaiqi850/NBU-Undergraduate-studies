import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler  # 使用标准化
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt


# LSTM模型定义（使用双向LSTM和Dropout）
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size, num_layers=2, dropout=0.3, bidirectional=True):
        super(LSTMModel, self).__init__()
        # 添加双向LSTM
        self.lstm = nn.LSTM(input_size, hidden_layer_size, num_layers=num_layers,
                            batch_first=True, dropout=dropout, bidirectional=bidirectional)
        # 计算输出尺寸，双向LSTM会增加2倍的隐藏层单元数
        self.fc = nn.Linear(hidden_layer_size * 2 if bidirectional else hidden_layer_size, output_size)

    def forward(self, x):
        lstm_out, (hn, cn) = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1])  # 仅使用最后时刻的输出进行预测
        return predictions


# 从 Excel 读取数据
def read_data_from_excel(file_path):
    df = pd.read_excel(file_path)
    df = df.dropna(subset=["Temperature", "Humidity", "Timestamp"])  # 去掉缺失值

    # 提取时、分、秒特征
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    df['Minute'] = df['Timestamp'].dt.minute
    df['Second'] = df['Timestamp'].dt.second

    return df[["Temperature", "Humidity", "Hour", "Minute", "Second"]]


# 数据预处理（使用温度、湿度以及时分秒特征）
def prepare_data(data, time_step):
    scaler = StandardScaler()  # 使用标准化

    # 只保留需要的特征（温度、湿度、小时、分钟、秒）
    features = ["Temperature", "Humidity", "Hour", "Minute", "Second"]
    scaled_data = scaler.fit_transform(data[features])

    # 创建时间序列数据集
    X, y = [], []
    for i in range(len(scaled_data) - time_step):
        X.append(scaled_data[i:i + time_step])
        y.append(scaled_data[i + time_step, :2])  # 预测的是温度和湿度

    X = np.array(X)
    y = np.array(y)
    print(X.shape)

    return X, y, scaler


# 训练函数
def train_model(model, train_X, train_y, epochs=200, batch_size=64, learning_rate=0.0005):  # 调整学习率
    train_X = torch.tensor(train_X, dtype=torch.float32)
    train_y = torch.tensor(train_y, dtype=torch.float32)

    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    # 训练过程
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        # Forward pass
        output = model(train_X)

        # 计算损失
        loss = criterion(output, train_y)

        # 反向传播
        loss.backward()
        optimizer.step()

        # 每10个epoch打印一次损失
        if (epoch + 1) % 10 == 0:
            print(f'Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}')

    # 保存训练后的模型
    torch.save(model.state_dict(), "model.pth")
    print("Model training complete. Model saved as model.pth.")


# 读取 Excel 数据并进行训练
file_path = r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx"
data = read_data_from_excel(file_path)

# 数据预处理
time_step = 10
X, y, scaler = prepare_data(data, time_step)

# 构建训练集和验证集
train_X, val_X, train_y, val_y = train_test_split(X, y, test_size=0.2, shuffle=False)

# 转换为 PyTorch tensor
train_X = torch.tensor(train_X, dtype=torch.float32)
train_y = torch.tensor(train_y, dtype=torch.float32)
val_X = torch.tensor(val_X, dtype=torch.float32)
val_y = torch.tensor(val_y, dtype=torch.float32)

# 初始化 LSTM 模型，调整 input_size
model = LSTMModel(input_size=5, hidden_layer_size=200, output_size=2, num_layers=3, dropout=0.1)

# 训练模型
train_model(model, train_X, train_y, epochs=400, learning_rate=0.001)

# 预测和评估
model.eval()
with torch.no_grad():
    predictions = model(val_X)

# 逆归一化并显示结果
predictions = scaler.inverse_transform(np.hstack([predictions.numpy(), np.zeros((predictions.shape[0], 3))]))
val_y = scaler.inverse_transform(np.hstack([val_y.numpy(), np.zeros((val_y.shape[0], 3))]))

# 打印评估结果
print(f"预测值: {predictions[:5]}")
print(f"实际值: {val_y[:5]}")

# 可视化预测结果
plt.plot(val_y[:, 0], label='True Temperature')
plt.plot(predictions[:, 0], label='Predicted Temperature')
plt.legend()
plt.show()
