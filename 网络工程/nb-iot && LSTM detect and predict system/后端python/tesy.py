import paho.mqtt.client as mqtt
import json
import time
from openpyxl import Workbook, load_workbook
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime, timedelta

# 服务器和主题信息
host = '10.83.11.4'
port = 1883
topic = 'esp8266'

# 创建 Excel 工作簿和工作表（用于存储原始数据）
def create_mqtt_data_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Sensor Data"
    ws.append(["Temperature", "Humidity", "deviceId", "Timestamp"])  # 设置表头
    wb.save(r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx")  # 保存为 Excel 文件

# 创建 Excel 工作簿和工作表（用于存储预测数据）
def create_predicted_data_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Predicted Data"
    ws.append(["Temperature", "Humidity", "deviceId", "Timestamp"])  # 设置表头
    wb.save(r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\predicted_data.xlsx")  # 保存为 Excel 文件

# LSTM模型定义
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_layer_size, batch_first=True)
        self.fc = nn.Linear(hidden_layer_size, output_size)

    def forward(self, x):
        lstm_out, (hn, cn) = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1])  # 输出最后时间步的预测
        return predictions

# 构建LSTM模型
def build_model():
    model = LSTMModel(input_size=2, hidden_layer_size=200, output_size=2)
    model.eval()  # 设置为评估模式
    return model

# 初始化LSTM模型
model = build_model()

# 数据归一化
scaler = MinMaxScaler(feature_range=(0, 1))

# 数据缓冲区：用于存储最近接收到的 20 个数据点
data_buffer = []

# 数据缓冲区更新和预测
def add_data_for_prediction(temperature, humidity):
    global data_buffer

    # 添加新数据
    data_buffer.append([temperature, humidity])

    # 如果缓冲区的数据超过20个，则进行一次预测
    if len(data_buffer) >= 60:
        # 取最后20个数据点
        data_batch = np.array(data_buffer[-60:])

        # 进行预测
        predict_next_batch(data_batch)

# 批量预测函数：预测未来 60 个点（每隔 5 分钟）
def predict_next_batch(data_batch):
    # 将数据归一化
    scaled_data = scaler.fit_transform(data_batch)

    # 将数据转换为 LSTM 模型所需的形状
    current_input = torch.tensor(scaled_data.reshape(1, 60, 2), dtype=torch.float32)

    # 预测未来 60 个时间步
    predictions = []
    future_times = []

    # 获取当前时间
    current_time = datetime.now()

    for i in range(60):  # 预测未来 60 个点
        with torch.no_grad():
            prediction = model(current_input)  # 预测下一个时间步

        # 逆归一化
        predicted_values = scaler.inverse_transform(prediction.numpy())

        # 保存预测结果
        predictions.append(predicted_values[0])

        # 计算预测时间
        future_time = current_time + timedelta(minutes=(i + 1))  # 每隔 5 分钟递增
        future_times.append(future_time.strftime('%H:%M:%S'))

        # 使用预测结果作为下一个时间步的输入
        current_input = torch.tensor(
            np.append(current_input[:, 1:, :], prediction.unsqueeze(1), axis=1), dtype=torch.float32
        )

    # 将预测结果覆盖写入 Excel 文件
    wb = Workbook()  # 创建新的工作簿
    ws = wb.active
    ws.title = "Predicted Data"
    ws.append(["Temperature", "Humidity", "deviceId", "Timestamp"])  # 设置表头

    for i, (temp, hum) in enumerate(predictions):
        # 写入数据到工作表，ID 为 "Predicted"，时间为未来预测时间
        ws.append([temp, hum, "1", future_times[i]])
    wb.save(r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\predicted_data.xlsx")  # 保存到新的 Excel 文件

# 当客户端接收到一个 CONNACK 响应时的回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

# 当从服务器中收到消息时的回调函数
def on_message(client, userdata, msg):
    try:
        # 解析消息内容
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)

        # 从数据中提取字段
        temperature = data.get("Temperature")
        humidity = data.get("Humidity")
        sensor_id = data.get("ID")
        timestamp = data.get("Timestamp")

        # 将时间戳转化为时分秒格式
        readable_time = time.strftime('%H:%M:%S', time.localtime(timestamp))

        # 打印接收到的数据
        print(
            f"Received data: Temperature={temperature}, Humidity={humidity}, ID={sensor_id}, Timestamp={readable_time}"
        )

        # 将数据写入 Excel（mqtt_data.xlsx）
        wb = load_workbook(r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx")  # 打开已存在的 Excel 文件
        ws = wb.active
        ws.append([temperature, humidity, sensor_id, readable_time])  # 追加数据
        wb.save(r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx")

        # 追加到当前数据列表，进行批量预测
        add_data_for_prediction(temperature, humidity)

    except Exception as e:
        print(f"Error processing message: {e}")

# 构建 MQTT 客户端
client = mqtt.Client()

# 配置回调函数
client.on_connect = on_connect
client.on_message = on_message

# 连接服务器
client.connect(host, port)

# 启动 MQTT 客户端并开始循环
client.loop_forever()
