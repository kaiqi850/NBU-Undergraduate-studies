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
host = '10.20.196.78'
port = 1883
topic = 'esp8266'

# 创建 Excel 工作簿和工作表（用于存储原始数据）
def create_mqtt_data_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Sensor Data"
    ws.append(["Temperature", "Humidity", "deviceId", "Timestamp"])  # 设置表头
    wb.save(
        r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx")  # 保存为 Excel 文件

# 创建 Excel 工作簿和工作表（用于存储预测数据）
def create_predicted_data_excel():
    wb = Workbook()
    ws = wb.active
    ws.title = "Predicted Data"
    ws.append(["Temperature", "Humidity", "deviceId", "Timestamp"])  # 设置表头
    wb.save(
        r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\predicted_data.xlsx")  # 保存为 Excel 文件

# LSTM模型定义（与训练部分兼容）
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_layer_size, output_size, num_layers=2, dropout=0.3, bidirectional=True):
        super(LSTMModel, self).__init__()
        # 添加双向LSTM
        self.lstm = nn.LSTM(input_size, hidden_layer_size, num_layers=num_layers,
                            batch_first=True, dropout=dropout, bidirectional=bidirectional)
        self.fc = nn.Linear(hidden_layer_size * 2 if bidirectional else hidden_layer_size, output_size)

    def forward(self, x):
        lstm_out, (hn, cn) = self.lstm(x)
        predictions = self.fc(lstm_out[:, -1])  # 使用最后时间步的输出进行预测
        return predictions

# 构建LSTM模型
def build_model():
    model = LSTMModel(input_size=2, hidden_layer_size=200, output_size=2, num_layers=3, dropout=0.3)
    model.load_state_dict(torch.load("model.pth"))  # 加载预训练模型
    model.eval()  # 设置为评估模式
    return model

# 初始化LSTM模型
model = build_model()

# 数据归一化
scaler = MinMaxScaler(feature_range=(0, 1))

# 预测函数：预测未来 60 个点
def predict_from_excel():
    # 从 Excel 中读取数据
    wb = load_workbook(
        r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx")
    ws = wb.active
    data = pd.DataFrame(ws.values)
    data.columns = ["Temperature", "Humidity", "deviceId", "Timestamp"]  # 设置列名

    # 忽略表头行
    data = data.iloc[1:]

    # 进行数据预处理
    data_values = data[["Temperature", "Humidity"]].astype(float).values  # 转换为浮点数
    scaled_data = scaler.fit_transform(data_values)

    # 创建时间序列数据集
    time_step = 10  # 修改为10步进行试验
    X = []
    for i in range(len(scaled_data) - time_step):
        X.append(scaled_data[i:i + time_step])
    X = np.array(X)

    # 转换为 LSTM 模型所需的输入形状
    current_input = torch.tensor(X[-1].reshape(1, time_step, 2), dtype=torch.float32)

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
        future_time = current_time + timedelta(minutes=(i + 1))  # 每隔 1 分钟递增
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

    # 保存预测数据到 Excel 文件
    wb.save(
        r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\predicted_data.xlsx")


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
        wb = load_workbook(
            r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx")  # 打开已存在的 Excel 文件
        ws = wb.active
        ws.append([temperature, humidity, sensor_id, readable_time])  # 追加数据
        wb.save(
            r"C:\Users\asus\Desktop\x\试卷卷卷子\网络工程\Intelligent-temperature-and-humidity-system\public\mqtt_data.xlsx")

        # 每次新数据到达后从 Excel 读取并进行预测
        predict_from_excel()

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
