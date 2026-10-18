import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import json
import datetime
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook

# MQTT服务器信息
host = '10.83.11.4'
port = 1883
topic = 'esp8266'

# 数据队列，用于存储温湿度值
max_points = 50  # 图上最多显示的点数
temperature_data = deque(maxlen=max_points)  # 存储温度数据
humidity_data = deque(maxlen=max_points)  # 存储湿度数据
time_data = deque(maxlen=max_points)  # 存储时间数据

# 初始化图表
plt.style.use('seaborn-darkgrid')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
line_temp, = ax1.plot([], [], label="Temperature (°C)", color='r')
line_hum, = ax2.plot([], [], label="Humidity (%)", color='b')

# 配置图表
ax1.set_ylim(10, 25)  # 根据温度范围调整
ax1.set_title("Real-Time Temperature")
ax1.set_ylabel("Temperature (°C)")
ax1.legend()

ax2.set_ylim(0, 100)  # 根据湿度范围调整
ax2.set_title("Real-Time Humidity")
ax2.set_xlabel("Time")
ax2.set_ylabel("Humidity (%)")
ax2.legend()

# 创建或加载 Excel 文件
excel_filename = "mqtt_data.xlsx"
try:
    workbook = load_workbook(excel_filename)
    sheet = workbook.active
except FileNotFoundError:
    workbook = Workbook()
    sheet = workbook.active
    # 写入表头
    sheet.append(["Timestamp", "Temperature (°C)", "Humidity (%)"])

# MQTT连接成功的回调
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

# MQTT接收到消息的回调
def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)  # 假设数据格式为 {"Temperature": 25.6, "Humidity": 43.3, "Timestamp": 1732339159}
        temp = data.get("Temperature", None)
        hum = data.get("Humidity", None)
        timestamp = data.get("Timestamp", None)

        # 转换时间戳为现实时间
        if timestamp is not None:
            readable_time = datetime.datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')
        else:
            raise ValueError("Invalid timestamp")

        # 打印接收到的数据
        if temp is not None and hum is not None:
            print(f"Temperature: {temp}°C, Humidity: {hum}%, Time: {readable_time}")
            temperature_data.append(temp)
            humidity_data.append(hum)
            time_data.append(readable_time)  # 存储现实时间

            # 将数据写入 Excel
            sheet.append([readable_time, temp, hum])
            workbook.save(excel_filename)  # 保存到文件
    except json.JSONDecodeError:
        print("Invalid data received:", msg.payload)
    except ValueError as e:
        print("Data error:", e)
    except Exception as e:
        print("Unexpected error:", e)

# 动态更新图表
def update(frame):
    if len(time_data) > 0:
        # 更新温度曲线
        line_temp.set_data(range(len(time_data)), temperature_data)
        ax1.set_xlim(0, len(time_data))  # 根据数据点动态调整x轴范围
        ax1.set_xticks(range(0, len(time_data), max(1, len(time_data) // 10)))  # 间隔标记时间
        ax1.set_xticklabels(list(time_data)[::max(1, len(time_data) // 10)], rotation=45, ha="right")

        # 更新湿度曲线
        line_hum.set_data(range(len(time_data)), humidity_data)
        ax2.set_xlim(0, len(time_data))  # 根据数据点动态调整x轴范围
        ax2.set_xticks(range(0, len(time_data), max(1, len(time_data) // 10)))  # 间隔标记时间
        ax2.set_xticklabels(list(time_data)[::max(1, len(time_data) // 10)], rotation=45, ha="right")

    return line_temp, line_hum

# 初始化MQTT客户端
client = mqtt.Client(protocol=mqtt.MQTTv311)  # 避免废弃警告
client.on_connect = on_connect
client.on_message = on_message
client.connect(host, port, keepalive=60)

# 启动动画
ani = FuncAnimation(fig, update, interval=500)  # 500ms更新一次

# 开始MQTT消息循环
client.loop_start()

# 显示图表
plt.tight_layout()
plt.show()
