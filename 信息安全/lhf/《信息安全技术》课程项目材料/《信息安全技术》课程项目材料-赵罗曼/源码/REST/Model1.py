import numpy as np
import pandas as pd
import cv2 as cv2
import hamming


# 将图片source_image切割成子图
def image_cut(source_image, cut_height, cut_width):
    height, width, channel = source_image.shape
    num_h = int(height / cut_height)
    num_w = int(width / cut_width)
    divide_image = np.zeros([num_h * num_w, cut_height, cut_width, channel], np.uint8)
    cnt = 0
    for i in range(0, num_h):
        for j in range(0, num_w):
            pic = source_image[i * cut_height:(i + 1) * cut_height, j * cut_width:(j + 1) * cut_width, :]
            divide_image[cnt, :, :, :] = pic
            cnt += 1
    return divide_image


# 导入训练好的簇心数据
data_center = np.array(pd.read_csv('./resources/center_result_s.csv'))[:, 1:]


def dist(A, B):
    return np.sqrt(np.sum(np.square(A - B)))


# 获取块的均值、索引
def find_index(img):
    avg = np.mean(img)
    img = img - avg
    centers = np.array(img.flatten())
    index = 0
    min_dist = 10000000000000000000000000
    for i in range(0, data_center.shape[0]):
        data_cnt = data_center[i]
        cnt_dist = dist(data_cnt, centers)
        if cnt_dist < min_dist:
            min_dist = cnt_dist
            index = i
    # print(min_dist)
    return avg, index


# 将块均值与索引处理成备份恢复信息
def trans_to_code(avg, index):
    binary_avg = bin(int(avg))[2:]
    length = len(binary_avg)
    for i in range(length, 8):
        binary_avg = '0' + binary_avg
    binary_index = bin(index)[2:]
    length = len(binary_index)
    for i in range(length, 8):
        binary_index = '0' + binary_index
    code = binary_avg + binary_index
    # print(int(avg), index)
    return code


def convHL(h, l):
    if h >= 0:
        x = l + int((h + 1) / 2)
        y = l - int(h / 2)
    else:
        x = l + int(h / 2)
        y = l - int((h - 1) / 2)
    return x, y


def embed_msg(img, msg):
    ori_img = img.copy()
    H, W = img.shape[:2]
    img_data = img.reshape(-1)

    loc_1 = []
    loc_2 = []
    lsb_2 = {}
    len_msg = len(msg)
    k1 = 0
    k2 = 0
    k3 = 0

    for i in range(len_msg):
        # 取像素对，相邻两个即可
        x = img_data[2 * i] * 1.0
        y = img_data[2 * i + 1] * 1.0
        # 计算均值和差值
        h = x - y
        l = int((x + y) / 2)
        # 正常情况下可进行差值拓展后的结果
        hs_1 = 2 * h + msg[i]
        # 若不可拓展则考虑直接覆盖LSB，则需要记录原有的LSB了
        hs_2 = 2 * int(h / 2) + msg[i]
        # 优先拓展
        if abs(hs_1) <= min(2 * (255 - l), 2 * l + 1):
            # 均值一直不变，使用拓展后的差值计算对应的像素对
            xs, ys = convHL(hs_1, l)
            loc_1.append(2 * i)
            k1 = k1 + 1
        elif abs(hs_2) <= min(2 * (255 - l), 2 * l + 1):
            xs, ys = convHL(hs_2, l)
            loc_2.append(2 * i)
            lsb_2[2 * i] = int(h) % 2  # 原来的lsb位
            k2 = k2 + 1
        else:
            k3 = k3 + 1
        img_data[2 * i] = xs
        img_data[2 * i + 1] = ys
    new_img = img_data.reshape(H, W)
    return loc_1, loc_2, lsb_2, new_img, ori_img


def embed_msg_b(img, msg):
    ori_img = img.copy()
    H, W = img.shape[:2]
    img_data = img.reshape(-1)
    data_list = []
    for i, dt in enumerate(img_data):
        data_list.append({
            'id': i,
            'val': dt
        })
    data_list = sorted(data_list, key=lambda item: item["val"])
    # print(data_list)
    loc_1 = []
    loc_2 = []
    lsb_2 = {}
    len_msg = len(msg)
    k1 = 0
    k2 = 0
    k3 = 0
    for i in range(len_msg):
        # 取像素对，相邻两个即可
        x = data_list[2 * i]['val'] * 1.0
        y = data_list[2 * i + 1]['val'] * 1.0
        # 计算均值和差值
        h = x - y
        l = int((x + y) / 2)
        # 正常情况下可进行差值拓展后的结果
        hs_1 = 2 * h + msg[i]
        # 若不可拓展则考虑直接覆盖LSB，则需要记录原有的LSB了
        hs_2 = 2 * int(h / 2) + msg[i]
        xs = 0
        ys = 0
        # 优先拓展
        if abs(hs_1) <= min(2 * (255 - l), 2 * l + 1):
            # 均值一直不变，使用拓展后的差值计算对应的像素对
            xs, ys = convHL(hs_1, l)
            loc_1.append(2 * i)
            k1 = k1 + 1
        elif abs(hs_2) <= min(2 * (255 - l), 2 * l + 1):
            # print(abs(hs_1), min(2 * (255 - l), 2 * l + 1))
            xs, ys = convHL(hs_2, l)
            loc_2.append(2 * i)
            lsb_2[2 * i] = int(h) % 2  # 原来的lsb位
            k2 = k2 + 1
        else:
            k3 = k3 + 1
        data_list[2 * i]['val'] = xs
        data_list[2 * i + 1]['val'] = ys
    data_list = sorted(data_list, key=lambda item: item["id"])
    for i, dt in enumerate(data_list):
        img_data[i] = data_list[i]['val']
    new_img = img_data.reshape(H, W)
    # print(k1, k2, k3)
    return loc_1, loc_2, lsb_2, new_img, ori_img


def embed_msg_c(img, msg):
    ori_img = img.copy()
    H, W = img.shape[:2]
    img_data = img.reshape(-1)
    len_msg = len(msg)
    for i in range(len_msg):
        # 取像素对，相邻两个即可
        x = img_data[2 * i] * 1.0
        y = img_data[2 * i + 1] * 1.0
        # 计算均值和差值
        h = x - y
        l = int((x + y) / 2)
        # 正常情况下可进行差值拓展后的结果
        hs_1 = 2 * h + msg[i]
        hs_2 = 2 * int(h / 2) + msg[i]
        # 均值一直不变，使用拓展后的差值计算对应的像素对
        if abs(hs_1) <= min(2 * (255 - l), 2 * l + 1):
            # 均值一直不变，使用拓展后的差值计算对应的像素对
            xs, ys = convHL(hs_1, l)
        else:
            xs, ys = convHL(hs_2, l)
        img_data[2 * i] = xs
        img_data[2 * i + 1] = ys
    new_img = img_data.reshape(H, W)
    return new_img, ori_img


def embed_msg_d(img, msg):
    ori_img = img.copy()
    H, W = img.shape[:2]
    img_data = img.reshape(-1)
    len_msg = len(msg)
    for i in range(len_msg):
        # 取像素对，相邻两个即可
        val = img_data[i]
        val = val & 0b11111110 | int(msg[i])
        img_data[i] = val
    new_img = img_data.reshape(H, W)
    return new_img, ori_img


def str2int(message):
    test_data = message
    Hidden_Data = np.zeros(len(test_data))
    for j in range(len(test_data)):
        Hidden_Data[j] = int(test_data[j])
    return Hidden_Data


def Embedded_watermark(source_image):
    # print(source_image.shape)
    cut_height, cut_width = 32, 32
    height, width, channel = source_image.shape
    num_row = height // cut_height
    num_col = width // cut_width

    divide_images = image_cut(source_image, cut_height, cut_width)  # 将图片做切割，返回三维数组
    num_sub_pic = divide_images.shape[0]  # 图片分割后的数量
    is_odd = False  # 标记是否有奇数子图的情况
    if num_sub_pic % 2 == 1:
        num_sub_pic -= 1
        is_odd = True  # 转化为偶数子图的情况并进行后续编码
    code_list = []  # 关联块生成备份验证信息
    for i in range(0, num_sub_pic, 2):
        avg1, index1 = find_index(divide_images[i])  # 块A均值与索引
        code1 = trans_to_code(avg1, index1)  # 转化为二进制码
        avg2, index2 = find_index(divide_images[i + 1])  # 块B均值与索引
        code2 = trans_to_code(avg2, index2)  # 转化为二进制码
        code_information = code1 + code2  # 拼接
        code_for_related_blocks = [int(x) for x in list(code_information)]
        hamming_for_related_blocks = "".join([str(x) for x in hamming.Hamming(code_for_related_blocks).hammingEncode()])
        final_code = code_information + hamming_for_related_blocks  # 原信息与其海明码拼接成最后信息 比率32+38 共70
        code_list.append(final_code)

    key1 = 5  # 两个密钥
    key2 = 7

    hidden_sub_img = divide_images  # 存储嵌入信息后的子图
    # print(hidden_sub_img.shape) 0 1 2 3 4 5

    for index1 in range(num_sub_pic):  # 遍历子图
        index2 = ((key1 * index1) % num_sub_pic + key2) % num_sub_pic  # 找其映射块
        # index2 = (index1 + (num_sub_pic // 2)) % num_sub_pic
        hidden_data = str2int(code_list[int(index1 / 2)])  # 找当前块的备份信息
        tar_img = divide_images[index2, :, :, 0]  # 得到映射块图像
        # loc_1, l2, ls2, new_img, ori_img = embed_msg(tar_img, hidden_data)  # 嵌入信息
        new_img, ori_img = embed_msg_d(tar_img, hidden_data)  # 嵌入信息
        hidden_sub_img[index2, :, :, 0] = new_img  # 将嵌入信息后的映射块保存

    cnt = 0
    result = np.zeros([num_row * cut_height, num_col * cut_width, channel], np.uint8)  # 输出图像规格
    for i in range(num_row):
        for j in range(num_col):
            sub_img = hidden_sub_img[cnt, :, :, :]  # 将嵌入信息后的块进行提取
            cnt += 1
            result[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32, :] = sub_img  # 保存
    return result


import imageio
import matplotlib.pyplot as plt

if __name__ == '__main__':
    img = imageio.imread(r'E:\Secure Project\REST\REST\Test\test1.bmp')

    emb_img = Embedded_watermark(img)

    imageio.imwrite(r'E:\Secure Project\REST\REST\Test\test1_emb.bmp', emb_img)

    ax = plt.subplot(1, 2, 1)
    plt.imshow(img)
    ax.axis('off')

    ax = plt.subplot(1, 2, 2)
    plt.imshow(emb_img)
    ax.axis('off')

    plt.tight_layout()
    plt.show()
    # embed_msg_b(img[0:30, 0:30, 0], str2int("101010100111"))
