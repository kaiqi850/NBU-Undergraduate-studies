import numpy as np
import cv2


def calculate_mse(image1, image2):
    # 确保两个输入图像具有相同的维度
    err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
    err /= float(image1.shape[0] * image1.shape[1])
    return err


def calculate_psnr(image1, image2, max_pixel=255.0):
    mse = calculate_mse(image1, image2)
    if mse == 0:
        return float('inf')
    return 20 * np.log10(max_pixel / np.sqrt(mse))

def work(pic):
    # 读取两个图像，这里假设它们是灰度图像
    img1 = cv2.imread(r'G:\DLData\Flicker1024\Test Picture\Test_{}\emb_{}.bmp'.format(pic, pic), cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(r'G:\DLData\Flicker1024\Test Picture\Test_{}\fix_{}.bmp'.format(pic, pic), cv2.IMREAD_GRAYSCALE)

    # 确保两个图像具有相同的尺寸
    if img1.shape != img2.shape:
        print("Error: Images have different dimensions.")
        exit()

    # 计算PSNR
    psnr = calculate_psnr(img1, img2)
    print(f"PSNR: {psnr:.2f} dB")

if __name__ == '__main__':
    work(1)
    work(2)
    work(3)
    work(4)
    work(5)