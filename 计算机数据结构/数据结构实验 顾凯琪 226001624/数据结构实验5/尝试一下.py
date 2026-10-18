import pandas as pd
import folium
import requests
import random
import math
import heapq

# 百度地图API密钥
api_key = 'REPLACE_WITH_YOUR_VALUE'

# 初始化地图
m = folium.Map(location=[35, 105], zoom_start=5)

# 读取CSV文件
csv_file_path = 'subway.csv'
df = pd.read_csv(csv_file_path, encoding='utf-8', errors='ignore')


# 提取所有城市列表
all_cities = set(df.iloc[:, 0]).union(set(df.iloc[:, 2]))

# 存储地址及其经纬度信息
location_dict = {}

# 获取每个城市的经纬度信息
for city in all_cities:
    # 构造地理编码请求URL
    geocode_url = f"http://api.map.baidu.com/geocoding/v3/?address={city}&output=json&ak={api_key}"

    # 发送请求并获取响应
    response = requests.get(geocode_url)
    data = response.json()

    if data['status'] == 0:
        # 获取经纬度
        lng = data['result']['location']['lng']
        lat = data['result']['location']['lat']
        location_dict[city] = (lat, lng)
        print(f"{city} 经度: {lng}, 纬度: {lat}")

        # 添加标记到地图
        folium.Marker([lat, lng], popup=city).add_to(m)
    else:
        print(f"获取 {city} 的地理编码信息失败")

# 构建图
graph = {city: {} for city in location_dict}
for index, row in df.iterrows():
    start = row.iloc[0]
    end = row.iloc[2]
    start_coords = location_dict[start]
    end_coords = location_dict[end]

    # 计算两点之间的距离
    distance = math.sqrt((start_coords[0] - end_coords[0]) ** 2 + (start_coords[1] - end_coords[1]) ** 2)

    # 在图中添加边
    graph[start][end] = distance

    # 画线
    folium.PolyLine([start_coords, end_coords], color="blue", weight=2.5, opacity=1).add_to(m)
    print(f"路线: {start} -> {end} 距离: {distance}")

# Dijkstra 算法
def dijkstra(graph, start, end):
    # 初始化
    pq = [(0, start)]
    distances = {node: float('inf') for node in graph}
    previous_nodes = {node: None for node in graph}
    distances[start] = 0
    visited = set()

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_node in visited:
            continue

        visited.add(current_node)

        if current_node == end:
            break

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    # 构建最短路径
    path = []
    current_node = end
    while previous_nodes[current_node] is not None:
        path.insert(0, current_node)
        current_node = previous_nodes[current_node]
    if path:
        path.insert(0, current_node)
    return path, distances[end]

# 输入起点和终点城市
start_city = input("北京")
end_city = input("宁波")

# 计算最短路径
shortest_path, shortest_distance = dijkstra(graph, start_city, end_city)
print(f"从 {start_city} 到 {end_city} 的最短路径: {shortest_path}")
print(f"最短路径距离: {shortest_distance}")

# 在地图上绘制最短路径
path_coords = [location_dict[city] for city in shortest_path]
folium.PolyLine(path_coords, color="red", weight=2.5, opacity=1).add_to(m)

# 保存地图到HTML文件
m.save('baidu_map_routes.html')

# 输出地图
m
