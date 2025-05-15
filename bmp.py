# import os
# import SimpleITK as sitk
# from PIL import Image
# import numpy as np
# #从.bmp格式转成.nii.gz格式
# # 设置 .bmp 文件所在目录
# bmp_dir = "/root/autodl-tmp/zuoyougu/mask/a"

# # 设置输出保存目录
# save_folder = "/root/autodl-tmp/zuoyougu"

# # 用于存储 RGB 到体素值的映射
# color_map = {}

# # 用于处理 RGB 值的容差
# tolerance = 5

# # 判断 RGB 值是否是黑白灰色
# def is_gray_or_black_white(rgb):
#     r, g, b = rgb
#     return abs(r - g) < tolerance and abs(g - b) < tolerance

# # 判断 RGB 值是否已经在字典中
# def get_or_add_color(rgb):
#     # 如果该颜色已经在字典中，直接返回对应的体素值
#     if rgb in color_map:
#         return color_map[rgb]
#     else:
#         # 如果该颜色不在字典中，分配一个新的体素值
#         new_value = len(color_map) + 1  # 给新的颜色分配一个新的体素值
#         color_map[rgb] = new_value
#         return new_value

# # 获取所有 .bmp 文件路径，并按顺序排序（假设文件名有顺序）
# bmp_files = sorted([f for f in os.listdir(bmp_dir) if f.endswith('.bmp')])

# # 确保目录下有 .bmp 文件
# if len(bmp_files) == 0:
#     raise FileNotFoundError(f"没有找到 BMP 文件，请检查目录: {bmp_dir}")

# # 读取第一张 .bmp 图像，确定宽度和高度
# first_image_path = os.path.join(bmp_dir, bmp_files[0])
# first_image = Image.open(first_image_path).convert('RGB')
# width, height = first_image.size

# # 创建一个 3D 体素矩阵，形状为 (层数, 高度, 宽度)
# # 每个 .bmp 图像就是体素矩阵的一层
# voxel_matrix = np.zeros((len(bmp_files), height, width), dtype=np.uint8)

# # 遍历所有 .bmp 文件，将其转换为体素数据
# for z, file_name in enumerate(bmp_files):
#     bmp_path = os.path.join(bmp_dir, file_name)
#     bmp_image = Image.open(bmp_path).convert('RGB')

#     for y in range(height):
#         for x in range(width):
#             rgb = bmp_image.getpixel((x, y))
            
#             # 如果是黑白灰色，认为是背景，值设为 0
#             if is_gray_or_black_white(rgb):
#                 voxel_matrix[z, y, x] = 0
#             else:
#                 # 如果是彩色，查询字典，如果没有则加入
#                 voxel_matrix[z, y, x] = get_or_add_color(rgb)

# # 将 numpy 数组转换为 SimpleITK 图像
# image_sitk = sitk.GetImageFromArray(voxel_matrix)

# # 保存为 .nii.gz 格式
# nii_output_path = os.path.join(save_folder, "output_data.nii.gz")
# sitk.WriteImage(image_sitk, nii_output_path, True)

# print(f"3D NIfTI 数据已保存为: {nii_output_path}")
# 将标注好的mask的数据在mimics中将背景（窗宽窗位都调整黑色）保存为.bmp格式。用照片查看器，取出每个颜色。然后分别映射为1，2，3等标签

import os
import SimpleITK as sitk
from PIL import Image
import numpy as np

# 设置 .bmp 文件所在目录
bmp_dir = "/root/autodl-tmp/zuoyougu/mask/a"
# 设置输出保存目录
save_folder = "/root/autodl-tmp/zuoyougu"

# 定义颜色到标签的映射
color_to_label = {
    (0, 127, 254): 1,           # RGB (0, 254, 0) -> 标签 1
    (4, 72, 4): 2,         # RGB (0, 127, 254) -> 标签 2
    (254, 127, 0): 3,         # RGB (254, 254, 0) -> 标签 3
    (254, 254, 0): 4,     # RGB (254, 127, 127) -> 标签 4
    (96,17,56):5,
}

# 判断 RGB 值是否是背景（即不属于上述颜色映射）
def get_label_for_rgb(rgb):
    if rgb in color_to_label:
        return color_to_label[rgb]  # 返回对应的标签
    else:
        return 0  # 背景为标签 0

# 获取所有 .bmp 文件路径，并按顺序排序（假设文件名有顺序）
bmp_files = sorted([f for f in os.listdir(bmp_dir) if f.endswith('.bmp')])

# 确保目录下有 .bmp 文件
if len(bmp_files) == 0:
    raise FileNotFoundError(f"没有找到 BMP 文件，请检查目录: {bmp_dir}")

# 读取第一张 .bmp 图像，确定宽度和高度
first_image_path = os.path.join(bmp_dir, bmp_files[0])
first_image = Image.open(first_image_path).convert('RGB')
width, height = first_image.size

# 创建一个 3D 体素矩阵，形状为 (层数, 高度, 宽度)
# 每个 .bmp 图像就是体素矩阵的一层
voxel_matrix = np.zeros((len(bmp_files), height, width), dtype=np.uint8)

# 遍历所有 .bmp 文件，将其转换为体素数据
for z, file_name in enumerate(bmp_files):
    bmp_path = os.path.join(bmp_dir, file_name)
    bmp_image = Image.open(bmp_path).convert('RGB')
    
    for y in range(height):
        for x in range(width):
            rgb = bmp_image.getpixel((x, y))
            # 获取颜色对应的标签
            voxel_matrix[z, y, x] = get_label_for_rgb(rgb)

# 将 numpy 数组转换为 SimpleITK 图像
image_sitk = sitk.GetImageFromArray(voxel_matrix)

# 保存为 .nii.gz 格式
nii_output_path = os.path.join(save_folder, "output_data.nii.gz")
sitk.WriteImage(image_sitk, nii_output_path, True)

print(f"3D NIfTI 数据已保存为: {nii_output_path}")
