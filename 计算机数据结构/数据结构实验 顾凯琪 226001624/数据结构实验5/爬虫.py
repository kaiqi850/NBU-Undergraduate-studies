import requests
from bs4 import BeautifulSoup
import csv

# 目标URL（假设这是中国铁路某个页面的URL）
url = 'https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc&fs=%E5%8C%97%E4%BA%AC,BJP&ts=%E8%A5%BF%E5%AE%89,XAY&date=2024-06-10&flag=N,N,Y'

# 发送HTTP GET请求
response = requests.get(url)

# 检查请求是否成功
if response.status_code == 200:
    # 解析HTML内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找包含列车路线的表格或元素（需要根据实际页面结构调整）
    routes = []
    for route in soup.find_all('div', class_='route-class'):  # 假设页面中有'div'元素包含路线信息
        train_number = route.find('span', class_='train-number').text
        start_station = route.find('span', class_='start-station').text
        end_station = route.find('span', class_='end-station').text
        duration = route.find('span', class_='duration').text

        routes.append([train_number, start_station, end_station, duration])

    # 将数据保存到CSV文件
    with open('train_routes.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Train Number', 'Start Station', 'End Station', 'Duration'])
        writer.writerows(routes)

    print('数据已保存到 train_routes.csv 文件中')
else:
    print('请求失败，状态码：', response.status_code)
