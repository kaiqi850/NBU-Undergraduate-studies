from 未修改的 import Net, transform, classes
import torch
from PIL import Image
import os

# 加载网络模型
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
net = Net()
net.load_state_dict(torch.load('藏起来的权重文件/weights(改层次50e).tar')['model_state_dict'])
net = net.to(device)
net.eval()

# 指定包含测试图片的文件夹路径
folder_path = 'test_images'
output_file = 'results.txt'  # 保存识别结果的文件

# 获取文件夹中所有图片的文件名
image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png'))]

# 打开输出文件以保存结果
with open(output_file, 'w') as f:
    for image_file in image_files:
        # 构建图像的完整路径
        image_path = os.path.join(folder_path, image_file)

        # 加载并预处理图像
        image = Image.open(image_path)
        image = image.resize((32, 32))
        image = transform(image).unsqueeze(0)
        image = image.to(device)

        # 进行图像识别
        with torch.no_grad():
            outputs = net(image)
            _, predicted = torch.max(outputs.data, 1)
            class_name = classes[predicted.item()]

        # 将结果写入输出文件
        f.write(f"图片文件：{image_file}, 识别结果：{class_name}\n")

print("测试完成，结果保存在", output_file)
