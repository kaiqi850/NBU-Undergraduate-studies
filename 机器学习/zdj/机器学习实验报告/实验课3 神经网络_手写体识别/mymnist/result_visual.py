import torch
from torchvision import datasets, transforms
import matplotlib.pyplot as plt
import numpy as np
from models import LeNet  # 如果你的模型文件是models.py中定义的LeNet，请确保这个导入路径正确

# 定义数据转换
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# 加载验证集
val_dataset = datasets.MNIST(root='./mnist', train=False, download=False, transform=transform)
val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=1, shuffle=True)

# 加载模型
model = LeNet(num_classes=10)  # 注意：这里的模型定义和训练代码中的应该是一致的
model.load_state_dict(torch.load('./saved/LeNet.pth'))  # 加载保存的模型参数
model.eval()  # 设置为评估模式，确保dropout等层不起作用

# 定义标签映射
label_mapping = {
    0: '0', 1: '1', 2: '2', 3: '3', 4: '4',
    5: '5', 6: '6', 7: '7', 8: '8', 9: '9'
}

# 可视化预测结果
with torch.no_grad():
    for images, labels in val_loader:
        output = model(images)
        _, predicted = torch.max(output, 1)
        prediction = predicted.item()

        # 可视化输入图像
        plt.imshow(images.squeeze().numpy(), cmap='gray')
        plt.title(f'Prediction: {label_mapping[prediction]}, Actual: {label_mapping[labels.item()]}')
        plt.show()
        #break  # 仅显示一个样本以示例
