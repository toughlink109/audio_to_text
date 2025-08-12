import torch
print("是否检测到GPU：",torch.cuda.is_available())
print("GPU型号为：",torch.cuda.get_device_name(0))
