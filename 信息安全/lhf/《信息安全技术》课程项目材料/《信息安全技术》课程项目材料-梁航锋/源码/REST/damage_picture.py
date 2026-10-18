import cv2
import numpy as np
import argparse


def damage(inpath, outpath, num):
    img = cv2.imread(inpath)
    num_row = int(img.shape[0] / 32)
    num_col = int(img.shape[1] / 32)
    damage_index = np.random.randint(0, num_row * num_col - 2, size=num)  # 随机索引
    result = img
    cnt = 0
    for i in range(num_row):
        for j in range(num_col):
            if cnt in damage_index:
                tmp = np.random.randint(0, 255, size=(32, 32))  # 随机值
                result[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32:, 0] = tmp
                tmp = np.random.randint(0, 255, size=(32, 32))  # 随机值
                result[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32:, 1] = tmp
                tmp = np.random.randint(0, 255, size=(32, 32))  # 随机值
                result[i * 32:(i + 1) * 32, j * 32:(j + 1) * 32:, 2] = tmp
            cnt += 1
    cv2.imwrite(outpath, result)


import matplotlib.pyplot as plt

if __name__ == "__main__":
    # 随机产生噪声于图形并输出
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--inpath', help='input_path')
    # parser.add_argument('--outpath', help='output_path')
    # parser.add_argument('--num', help='number of damaged blocks')
    # args = parser.parse_args()

    # in_path = args.inpath
    # out_path = args.outpath
    # damage_num = int(args.num)

    in_path = r'G:\DLData\Flicker1024\Test Picture\Test_4\emb_4.bmp'
    out_path = r'G:\DLData\Flicker1024\Test Picture\Test_4\damage_4.bmp'
    damage_num = 10

    damage(in_path, out_path, damage_num)

    img = cv2.imread(in_path)
    ax = plt.subplot(1, 2, 1)
    plt.imshow(img)
    ax.axis('off')

    img = cv2.imread(out_path)
    ax = plt.subplot(1, 2, 2)
    plt.imshow(img)
    ax.axis('off')

    plt.show()
