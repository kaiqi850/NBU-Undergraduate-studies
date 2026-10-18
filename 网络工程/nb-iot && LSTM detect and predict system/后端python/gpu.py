import torch


import torch
print(torch.__version__)  #注意是双下划线
print(torch.version.cuda)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name())