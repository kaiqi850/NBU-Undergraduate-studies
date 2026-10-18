import numpy as np
import PIL.Image as Image

# 打开隐写文件
picture = Image.open('爱莉希雅(秘密版).png')
pic_datas = np.array(picture).ravel().tolist()

# 字符的长度为4893
with open('./pic/secret.txt', encoding="utf-8") as file:
    secrets = file.read()

str_len = len(secrets)
print('字符的长度为：', str_len)

# 将图片拷贝一份，作为最终的图片数据
im_data = np.array(picture.copy()).ravel().tolist()


def lsb_decode(data):
    '''
    :param bin_index:  当前字符的ascii的二进制
    :param data: 取出数组像素的八个数值
    :return: LSB隐写后的字符
    '''
    str = ''
    for i in range(len(data)):
        print(bin(data[i])[2:])
        data_i_bin = bin(data[i])[2:][-1]
        str += data_i_bin
    return str


pic_idx = 0
# 采用LSB隐写技术，横向取数据，每次取9个数据，改变8个像素最低位
res_data = []

for i in range(len(secrets)):
    # 拿到第i个数据,转换成二进制
    data = im_data[i * 8: (i + 1) * 8]
    data_int = lsb_decode(data)
    # 找到最低位
    res_data.append(int(data_int, 2))

# 将二进制数据转换成ASCII
str_data = ''
for i in res_data:
    temp = chr(i)
    str_data += temp
print(str_data)
