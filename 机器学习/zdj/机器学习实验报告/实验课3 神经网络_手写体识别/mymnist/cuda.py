import torch.cuda

import torch
print(torch.__version__)
print(torch.cuda.is_available())
import torch

# 检查CUDA是否可用
if torch.cuda.is_available():
    print(f"CUDA is available. GPU: {torch.cuda.get_device_name(0)}")
    # 创建一个随机的Tensor
    x = torch.rand(5, 3)
    print("Random Tensor:", x)
    # 尝试将Tensor移动到GPU上
    y = x.cuda()
    print("Tensor on GPU:", y)
else:
    print("CUDA is not available. Please check your installation.")
