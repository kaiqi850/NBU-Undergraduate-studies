import paho.mqtt.client as mqtt
import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import time
import json

# MQTT服务器和主题信息
host = '192.168.194.88'
port = 1883
topic = 'eps8266'



# 创建LSTM模型
class LSTMModel(torch.nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.fc = torch.nn.Linear(hidden_layer_size, output_size)

    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1, :])  # 输出最后一个时间步的预测
        return predictions


# 初始化模型
input_size = 6  # 输入特征数（包括时间特征）
hidden_layer_size = 50  # 隐藏层大小
output_size = 2  # 输出特征数（温度和湿度）

model = LSTMModel(input_size=input_size, hidden_layer_size=hidden_layer_size, output_size=output_size)
model.load_state_dict(torch.load('temperature_humidity_lstm_model.pth'))
model.eval()

# 创建MinMaxScaler进行归一化
scaler = MinMaxScaler(feature_range=(0, 1))

# 用于存储最近60个数据点
real_time_data = []


# MQTT客户端回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # 订阅主题
    client.subscribe(topic)


def on_message(client, userdata, msg):
    global real_time_data
    print(f"Received message: {msg.topic} {str(msg.payload)}")

    # 解析接收到的JSON数据
    try:
        data = json.loads(msg.payload.decode('utf-8'))  # 解析JSON格式的字符串

        # 提取温湿度数据
        temperature = data.get('Temperature')
        humidity = data.get('Humidity')

        if temperature is not None and humidity is not None:
            timestamp = pd.Timestamp.now()

            # 存储实时数据
            real_time_data.append({'timestamp': timestamp, 'temperature': temperature, 'humidity': humidity})

            # 如果实时数据的长度超过60个时间步，则移除最旧的数据
            if len(real_time_data) > 60:
                real_time_data.pop(0)

            # 创建DataFrame并提取时间特征
            df = pd.DataFrame(real_time_data)
            df['Hour_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.hour / 24)
            df['Hour_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.hour / 24)
            df['Minute_sin'] = np.sin(2 * np.pi * df['timestamp'].dt.minute / 60)
            df['Minute_cos'] = np.cos(2 * np.pi * df['timestamp'].dt.minute / 60)

            # 特征归一化
            scaled_data = scaler.fit_transform(
                df[['temperature', 'humidity', 'Hour_sin', 'Hour_cos', 'Minute_sin', 'Minute_cos']])

            # 使用过去60个时间步的数据进行预测
            if len(scaled_data) >= 60:
                X_input = scaled_data[-60:].reshape(1, 60, -1)  # 转换为模型输入格式

                # 将数据传入模型进行预测
                with torch.no_grad():
                    predicted_scaled = model(torch.tensor(X_input, dtype=torch.float32))

                # 反归一化预测结果
                predicted_scaled = predicted_scaled.numpy().flatten()
                predicted_values = scaler.inverse_transform(
                    np.concatenate([predicted_scaled.reshape(-1, 1), np.zeros((predicted_scaled.shape[0], 5))],
                                   axis=1))[:, 0]

                # 输出预测结果
                print(
                    f"Predicted Temperature: {predicted_values[0]:.2f} °C, Predicted Humidity: {predicted_values[1]:.2f} %")
        else:
            print("Temperature or Humidity data missing in the received message.")

    except Exception as e:
        print(f"Error processing message: {e}")


# 构建MQTT客户端
client = mqtt.Client()

# 配置连接和接收信息的回调函数
client.on_connect = on_connect
client.on_message = on_message

# 连接服务器
client.connect(host, port)

# 处理网络流量、分派回调和处理重新连接的阻塞调用
client.loop_start()

# 让主程序继续运行，以便接收数据
try:
    while True:
        time.sleep(1)  # 保持程序运行
except KeyboardInterrupt:
    print("Program interrupted")
