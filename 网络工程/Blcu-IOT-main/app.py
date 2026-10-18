from flask import Flask, jsonify,request
import Dbconn
from Common import Resp
from Common import Config
from Auth import Auth
import datetime
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)
CORS(app, supports_credentials=True)










# 处理最大温湿度变化的函数
def get_max_sensor():
    # 获取最近10分钟内的数据
    db = Dbconn.Mysql()
    sql_select = ("SELECT id, (MAX(temperature) - MIN(temperature)) + (MAX(wet) - MIN(wet)) AS temp_change_sum,(MAX(temperature) - MIN(temperature)) AS temperature_change,(MAX(wet) - MIN(wet)) AS wet_change FROM detail_data WHERE update_time >= DATE_SUB(NOW(), INTERVAL 10 MINUTE) GROUP BY id ORDER BY temp_change_sum DESC LIMIT 1;")
    result = db.dbSelect(sql_select)
    json_result = {}
    if len(result) > 0:
        json_result['sensor_id'] = result[0][0]
        json_result['temp_change_sum'] = result[0][1]
        json_result['temperature_change'] = result[0][2]
        json_result['wet_change'] = result[0][3]
    return json_result


# 定义接口路由
@app.route('/max_sensor', methods=['GET'])
def max_sensor():
    # 调用函数获取最大温湿度变化的传感器
    result = get_max_sensor()
    # 将结果以JSON格式返回
    return jsonify(result)


@app.route('/user_login', methods=['POST'])
def user_login():

    data = request.get_json()
    username = data.get('loginName')
    password = data.get('loginPwd')
    db = Dbconn.Mysql()
    ret = db.dbSelect("SELECT username,password FROM user_info WHERE username= '{}' ".format(username))
    if not len(ret) == 1:
        return Resp.error('用户名或密码错误')

    passhash = ret[0][1]
    if not Auth.check_password(passhash, password):
        return Resp.error('用户名或密码错误')


    JWT = Auth.encode_jwt(ret[0][1])
    userinfo = {
        'username': ret[0][1],

    }
    return Resp.success(body={
        'token': JWT,
        'userinfo': userinfo

    })

def get_sensor_data():
    sensors_data = []
    for i in range(5):
        sensor_data = {}
        sensor_data['id'] = 'Sensor ' + str(i + 1)
        sensor_data['temperature'] = round(random.uniform(20.0, 30.0), 2)
        sensor_data['humidity'] = round(random.uniform(40.0, 60.0), 2)
        sensor_data['time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sensors_data.append(sensor_data)
    return sensors_data

# 定义接口路由
@app.route('/sensors_data', methods=['GET'])
def get_sensors_data():
    db = Dbconn.Mysql()
    try:
        sql = "SELECT id, AVG(temperature) AS avg_temp,AVG(wet) AS avg_wet FROM detail_data WHERE update_time >= DATE_SUB(NOW(), INTERVAL 10 MINUTE) GROUP BY id;"
        results = db.dbSelect(sql)
        sensors_data = []
        for row in results:
            sensor_data = {}
            sensor_data['sensor_id'] = row[0]
            sensor_data['avg_temperature'] = row[1]
            sensor_data['avg_humidity'] = row[2]
            sensors_data.append(sensor_data)
        return jsonify({'code': 0, 'data': sensors_data})
    except Exception as e:
        print("Error fetching data from database: {}".format(str(e)))
        return jsonify({'code': -1, 'message': 'Error fetching data from database'})


@app.route('/temperature_change', methods=['GET'])
def get_temperature_change():
    db = Dbconn.Mysql()
    try:
        start_time = datetime.now() - timedelta(days=1)
        sql = "SELECT id, update_time, temperature FROM detail_data WHERE update_time >= '{}' ORDER BY update_time ASC;".format(
            start_time)
        results = db.dbSelect(sql)
        sensors_data = {}
        for row in results:
            sensor_id = 'Sensor ' + str(row[0])
            timestamp = row[1].strftime('%Y-%m-%d %H:%M:%S')
            temperature = row[2]
            if sensor_id not in sensors_data:
                sensors_data[sensor_id] = {
                    'timestamps': [],
                    'temperatures': []
                }
            sensors_data[sensor_id]['timestamps'].append(timestamp)
            sensors_data[sensor_id]['temperatures'].append(temperature)

        # 将传感器ID中的 "Sensor" 替换为 "传感器"
        sensors_data = {sensor.replace('Sensor', '传感器'): data for sensor, data in sensors_data.items()}

        return jsonify({'code': 0, 'data': sensors_data})
    except Exception as e:
        print("Error fetching data from database: {}".format(str(e)))
        return jsonify({'code': -1, 'message': 'Error fetching data from database'})



def adjust_temperature(data):
    db = Dbconn.Mysql()
    cur = db.conn.cursor()
    for item in data:
        sensor_id = item['id']
        origin_temp = item['origin_temp']
        new_temp = item['new_temp']
        update_time_str = item['update_time']
        update_time = datetime.fromisoformat(update_time_str[:-1])  # 解析时间字符串并去掉末尾的Z
        update_time= update_time.strftime("%Y-%m-%d %H:%M:%S")  # 将时间转换为MySQL的DATETIME格式

        # 将update_time_formatted作为参数传递给SQL语句执行插入操作

        sql_insert = "INSERT INTO temperature_adjust (id, origin_temp, new_temp, update_time) VALUES ('%s', '%s', '%s', '%s')" % (sensor_id, origin_temp, new_temp, update_time)
        cur.execute(sql_insert)
        sql_change = ""
    db.conn.commit()

# 定义接口路由
@app.route('/temperature_adjust', methods=['POST'])
def temperature_adjust():
    data = request.get_json()
    adjust_temperature(data)
    return jsonify({'status': 'success'})


@app.route('/register',methods=['POST'])
def register():
    # 获取前端传来的注册信息
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 判断用户名是否已被注册
    db = Dbconn.Mysql()
    sql_select = f"SELECT * FROM user_info WHERE username = '{username}'"
    res_select = db.dbSelect(sql_select)
    if res_select:
        return {'status': 'error', 'message': '该用户名已被注册'}

    # 对密码进行哈希加密存储
    password_hash = Auth.set_password(password)

    # 执行插入操作将用户名和加密后的密码存入数据库
    sql_insert = f"INSERT INTO user_info (username, password) VALUES ('{username}', '{password_hash}')"
    db.dbSelect(sql_insert)
    db.conn.commit()

    return {'status': 'success', 'message': '注册成功'}


# 处理温度统计的函数
def get_temperature_statistics():
    db = Dbconn.Mysql()
    sql_select = ("SELECT id, MAX(temperature), MIN(temperature) FROM detail_data WHERE update_time >= DATE_SUB(NOW(), INTERVAL 10 MINUTE) GROUP BY id;")
    result = db.dbSelect(sql_select)
    max_temps = []
    min_temps = []
    if len(result) > 0:
        for row in result:
            max_temps.append(row[1])
            min_temps.append(row[2])
    return {"maxTemps": max_temps, "minTemps": min_temps}


# 定义接口路由
@app.route('/temperature_statistics', methods=['GET'])
def temperature_statistics():
    # 调用函数获取温度统计数据
    result = get_temperature_statistics()
    # 将结果以JSON格式返回
    return jsonify({"code": 0, "data": result})


from flask import Flask, request, jsonify, make_response
import pandas as pd

@app.route('/export_data', methods=['GET'])
def predict_data():
    # 获取需要预测的传感器ID
    sensor_id = request.args.get('sensor_id')
    if sensor_id is None:
        sensor_id = random.choice(range(1, 6))
    sensor_id = "sensor" + str(sensor_id)

    # 获取最近24小时的数据
    db = Dbconn.Mysql()
    sql = "SELECT temperature, wet, update_time FROM detail_data WHERE id = '{}' AND update_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR) ORDER BY update_time ASC".format(sensor_id)
    print("SQL语句：", sql)

    result = db.dbSelect(sql)

    if len(result) == 0:
        return jsonify({'code': -1, 'message': 'No data found for the given sensor_id'})

    # 将查询结果转换为DataFrame格式
    data = pd.DataFrame(result, columns=['temperature', 'wet', 'update_time'])
    data['update_time'] = pd.to_datetime(data['update_time'])
    data.set_index('update_time', inplace=True)

    try:
        # 进行移动平均计算
        window_size = 6
        data_ma = data.rolling(window_size).mean()
        data_ma.dropna(inplace=True)

        # 训练模型并进行预测
        forecast = data_ma['temperature'].iloc[-1]
        forecast = pd.Series([forecast] * 24, index=pd.date_range(start=data_ma.index[-1], periods=24, freq='H'))
        prediction = pd.concat([data_ma, forecast.to_frame(name='temperature')])

        # 导出数据到Excel文件
        file_name = f'{sensor_id}_prediction.xlsx'
        with pd.ExcelWriter(file_name) as writer:
            prediction.to_excel(writer, sheet_name='data')

        # 将Excel文件以附件形式返回给前端
        with open(file_name, 'rb') as f:
            file_data = f.read()
        response = make_response(file_data)
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('Content-Disposition', 'attachment', filename=file_name)
        return response

    except Exception as e:
        print(f"Error occurred while forecasting: {e}")
        return jsonify({'code': -1, 'message': 'Error occurred while forecasting'})


@app.route('/growing_area_data', methods=['GET'])
def get_growing_area_data():
    db = Dbconn.Mysql()
    try:
        sql = "SELECT id, oid, SUM(number) AS number FROM real_time_state WHERE update_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR) GROUP BY id, oid;"
        results = db.dbSelect(sql)

        growing_area_data = []
        for row in results:
            area_data = {}
            area_data['id'] = row[0]
            area_data['oid'] = row[1]
            area_data['number'] = row[2]
            growing_area_data.append(area_data)

        return jsonify({'code': 0, 'data': growing_area_data})
    except Exception as e:
        print("Error fetching data from database: {}".format(str(e)))
        return jsonify({'code': -1, 'message': 'Error fetching data from database'})


# 模拟当前温度和目标温度
current_temperature = 25.0
target_temperature = 25.0
is_auto_control = False

# 随机生成当前温度
def get_random_temperature():
    global current_temperature
    current_temperature += random.uniform(-0.5, 0.5)
    return current_temperature

@app.route('/api/pid-control/start', methods=['POST'])
def start_auto_control():
    global is_auto_control, target_temperature
    data = request.get_json()
    target_temperature = data['targetTemperature']
    print(target_temperature)
    is_auto_control = True
    return jsonify({'message': '自动调节启动成功'})

@app.route('/api/pid-control/stop', methods=['POST'])
def stop_auto_control():
    global is_auto_control
    is_auto_control = False
    return jsonify({'message': '自动调节停止成功'})

@app.route('/api/pid-control/temp', methods=['GET'])
def get_temperature():
    global current_temperature, target_temperature
    current_temperature = get_random_temperature()
    return jsonify({
        'currentTemp': current_temperature,
        'targetTemp': target_temperature
    })


if __name__ == '__main__':
    app.run(debug=True,port=Config.APP_PORT,host='0.0.0.0')
