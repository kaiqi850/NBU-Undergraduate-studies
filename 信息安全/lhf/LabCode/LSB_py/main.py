import numpy as np
import cv2


def encode_lsb(image, message):
    message = message + '&'
    binary_message = ''.join(format(ord(char), '08b') for char in message)  # 将消息转换为二进制
    height, width, channel = image.shape
    if len(binary_message) > height * width * channel:  # 检查消息是否过长
        raise ValueError("Message is too long to be embedded in the image")

    data_index = 0
    encoded_image = np.copy(image)
    for i in range(height):
        for j in range(width):
            for k in range(channel):  # 对RGB三个通道进行操作
                if data_index < len(binary_message):
                    # 使用位操作将信息嵌入到最后一位
                    encoded_image[i, j, k] = image[i, j, k] & 0b11111110 | int(binary_message[data_index])
                    data_index += 1
                else:
                    break
            if data_index >= len(binary_message):
                break
        if data_index >= len(binary_message):
            break
    return encoded_image


def decode_lsb(image):
    binary_message = ''
    height, width, channel = image.shape
    for i in range(height):
        for j in range(width):
            for k in range(channel):  # 对RGB三个通道进行操作
                binary_message += str(image[i, j, k] & 1)  # 提取最低位信息

    message = ''
    for i in range(0, len(binary_message), 8):
        byte = binary_message[i:i + 8]
        if chr(int(byte, 2)) == '&':
            break
        message += chr(int(byte, 2))  # 将二进制转换为字符

    return message


def show_image(image, image_name):
    cv2.namedWindow(image_name)  # 创建一个image的窗口
    cv2.imshow(image_name, image)  # 显示图像
    cv2.waitKey()  # 默认为0，无限等待
    cv2.destroyAllWindows()
    return


if __name__ == '__main__':
    # 读取图像
    image_path = './Test.jpg'
    image = cv2.imread(image_path)

    print(image.shape)
    show_image(image, 'original image')

    secret_message = 'Liang Hangfeng 216001912 Learns Steganography'

    emb_image = encode_lsb(image, secret_message) # 信息嵌入

    show_image(emb_image, 'emb_image')

    ex_message = decode_lsb(emb_image) # 信息提取

    print(ex_message) # 输出信息

