import paho.mqtt.client as mqtt
import json
import time
from openpyxl import Workbook
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
# 服务器和主题信息
host = '10.83.11.4'
port = 1883
topic = 'esp8266'

# 创建 Excel 工作簿和工作表
wb = Workbook()
ws = wb.active
ws.title = "Sensor Data"
# 添加表头
ws.append(["Temperature", "Humidity", "ID", "Timestamp"])


# 当客户端接收到一个 CONNACK 响应时的回调函数
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # 订阅主题
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
            f"Received data: Temperature={temperature}, Humidity={humidity}, ID={sensor_id}, Timestamp={readable_time}")

        # 写入 Excel 表
        ws.append([temperature, humidity, sensor_id, readable_time])

        # 保存 Excel 文件
        wb.save("mqtt_data.xlsx")
    except Exception as e:
        print(f"Error processing message: {e}")


# 构建 MQTT 客户端
client = mqtt.Client()

# 配置连接和接收信息的回调函数
client.on_connect = on_connect
client.on_message = on_message

# 连接服务器
client.connect(host, port)


# 处理网络流量、分派回调和处理重新连接的阻塞调用
client.loop_forever()
