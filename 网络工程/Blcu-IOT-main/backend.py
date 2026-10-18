import time
import Dbconn
import paho.mqtt.client as mqtt
import json

# MQTT 代理地址和端口
broker_address = "localhost"
broker_port = 1883

db = Dbconn.Mysql()


# 处理 MQTT 消息的回调函数
def on_message(client, userdata, msg):
    # 解析 JSON 格式的数据包
    try:
        data = json.loads(msg.payload)
        sensor_id = data['sensor_id']
        temperature = data['temperature']
        wet = data['wet']
        update_time = data['update_time']
        # 处理温度数据
        print("接收到传感器编号为 {} 的温度数据，温度为: temperature = {} °C,更新时间是 {}".format(sensor_id, temperature,str(update_time)))
        tmp_list = []
        result_list = []
        tmp_list.append(sensor_id)
        tmp_list.append(temperature)
        tmp_list.append(wet)
        tmp_list.append(update_time)
        result_list.append(tmp_list)



        sql_insert = "INSERT INTO detail_data (`id`,`temperature`,`wet`,`update_time`) VALUES (%s,%s,%s,%s)"
        for i in range(0, len(result_list), 1000):
            db.dbSetBatch(sql_insert,result_list[i:i+1000])
            print("[+]记录成功")


    except Exception as e:
        print(f"处理消息时出错：{e}")



# 创建 MQTT 客户端对象
client = mqtt.Client()

# 设置连接和消息处理的回调函数
client.on_message = on_message

# 连接到 MQTT 代理
client.connect(broker_address, broker_port)

# 订阅传感器数据的主题
client.subscribe("sensors/+/data")

# 开启 MQTT 客户端的网络循环
client.loop_forever()
