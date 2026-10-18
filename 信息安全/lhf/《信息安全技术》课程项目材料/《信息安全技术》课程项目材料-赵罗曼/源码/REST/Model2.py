import numpy as np
import hamming
import pandas as pd


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


def convHL(h, l):
    if h >= 0:
        x = l + int((h + 1) / 2)
        y = l - int(h / 2)
    else:
        x = l + int((h) / 2)
        y = l - int((h - 1) / 2)
    return x, y


base = [2 * x for x in range(70)]


def extractMsg(loc_1, loc_2, lsb_2, img_emd):
    H, W = img_emd.shape[:2]
    img_data = img_emd.copy().reshape(-1)
    n = len(loc_1 + loc_2)
    p_ext = []
    for i in range(n):
        loc = 2 * i
        xs = img_data[2 * i] * 1.0
        ys = img_data[2 * i + 1] * 1.0
        hs = xs - ys
        # 均值不变
        ls = int((xs + ys) / 2)
        # 取出的信息
        b = int(hs % 2)
        # 属于可扩展情况
        if loc in loc_1:
            # 恢复真正差值
            hs = (hs - b) / 2
            x, y = convHL(hs, ls)
        # 属于可改变，强行改变了LSB的情况
        elif loc in loc_2:
            # 恢复真正差值
            hs = (hs - b) + lsb_2[loc]
            x, y = convHL(hs, ls)
        p_ext.append(b)
        img_data[2 * i] = x
        img_data[2 * i + 1] = y
    res = img_data.reshape(H, W)
    return p_ext, res


def extract_msg_b(img_emd):
    H, W = img_emd.shape[:2]
    img_data = img_emd.copy().reshape(-1)
    n = 70
    p_ext = []
    for i in range(n):
        b = int(img_data[i] & 1)
        p_ext.append(b)
    res = img_data.reshape(H, W)
    return p_ext, res


def check(mes):
    basis = mes[:32]
    ham1 = mes[32:]
    ham2 = hamming.Hamming([int(x) for x in list(basis)]).hammingEncode()
    ham2 = "".join([str(x) for x in ham2])
    # print(ham1)
    # print(ham2)
    # print()
    return ham1 == ham2


data_center = np.array(pd.read_csv('./resources/center_result_s.csv'))[:, 1:]


def fix_pic(code):
    avg1 = int(code[0:8], 2)
    index1 = int(code[8:], 2)
    # print(avg1,index1)
    pic = data_center[index1]
    pic = pic + avg1
    pic = pic.reshape(32, 32, 3)
    return pic


def Fix_Picture(source_image):
    cut_height, cut_width = 32, 32
    height, width, channel = source_image.shape
    num_row = height // cut_height
    num_col = width // cut_width

    divide_images = image_cut(source_image, cut_height, cut_width)  # 将图片做切割，返回三维数组
    num_sub_pic = divide_images.shape[0]  # 同理特殊处理
    if num_sub_pic % 2 == 1:
        num_sub_pic -= 1

    wrong_index = []  # 记录出错点的索引
    img_list = divide_images
    code_list = []
    for index in range(num_sub_pic):  # 遍历子块
        img = divide_images[index, :, :, :]
        # mes, new_img = extractMsg(base, [], {}, img)  # 提取信息
        mes, new_img = extract_msg_b(img[:, :, 0])

        img_list[index, :, :, 0] = new_img
        mes = "".join([str(x) for x in mes])  # 转化为字符串
        code_list.append(mes)
        if check(mes):  # check函数判定是否受损 通过海明码检验
            # print(1)
            pass
        else:
            wrong_index.append(index)  # 记录出错索引

    result = np.full((num_row * 32, num_col * 32), 255)  # 空白画布
    cnt = 0
    for i in range(num_row):
        for j in range(num_col):
            if cnt in wrong_index:  # 若当前索引出错则将画布对应位置标记为黑色
                result[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32] = np.full((32, 32), 0)
            cnt += 1

    key1 = 5  # 两个密钥
    key2 = 11

    recover_img = source_image
    cnt = 0
    for i in range(num_row):
        for j in range(num_col):
            if cnt not in wrong_index:
                recover_img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32, :] = img_list[cnt]
            else:
                # 该块损毁
                index1 = index2 = 0
                if cnt % 2 == 0:
                    index1 = cnt
                    index2 = cnt + 1
                else:
                    index1 = cnt - 1
                    index2 = cnt
                # map_index1 = (index1 + (num_sub_pic // 2)) % num_sub_pic
                # map_index2 = (index2 + (num_sub_pic // 2)) % num_sub_pic
                map_index1 = ((key1 * index1) % num_sub_pic + key2) % num_sub_pic
                map_index2 = ((key1 * index2) % num_sub_pic + key2) % num_sub_pic
                if map_index1 not in wrong_index:
                    message = code_list[map_index1]
                    used_message = message[:32]
                    recover_msg = ''
                    if cnt % 2 == 0:
                        recover_msg = used_message[:16]
                    else:
                        recover_msg = used_message[16:]
                    recover_img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32, :] = fix_pic(recover_msg)
                elif map_index2 not in wrong_index:
                    message = code_list[map_index2]
                    used_message = message[:32]
                    recover_msg = ''
                    if cnt % 2 == 0:
                        recover_msg = used_message[:16]
                    else:
                        recover_msg = used_message[16:]
                    recover_img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32, :] = fix_pic(recover_msg)
                else:
                    recover_img[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32, :] = img_list[cnt]
            cnt += 1
    return result, recover_img


import imageio
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # img = imageio.imread(r'G:\DLData\Flicker1024\test\damaged.bmp')
    # img = imageio.imread(r'G:\DLData\Flicker1024\selected\031_L.png')
    img = imageio.imread(r'E:\Secure Project\REST\REST\Test\test1_emb.bmp')
    res, rec = Fix_Picture(img)
    ax = plt.subplot(1, 2, 1)
    plt.imshow(rec)
    ax.axis('off')

    ax = plt.subplot(1, 2, 2)
    plt.imshow(res)
    ax.axis('off')

    plt.show()
