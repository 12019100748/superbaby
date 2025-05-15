# from PIL import Image

# # 打开 BMP 图像文件
# def get_unique_colors(image_path):
#     # 打开图像
#     image = Image.open(image_path)
    
#     # 将图像转换为 RGB 模式（即使它是其他模式，也能确保处理每个像素的颜色信息）
#     image = image.convert("RGB")
    
#     # 获取图像中的所有像素颜色
#     pixels = image.getdata()
    
#     # 使用集合来去重（集合中的元素是唯一的）
#     unique_colors = set(pixels)
    
#     # 输出不同颜色的数量
#     print(f"图像中共有 {len(unique_colors)} 种不同的颜色。")
    
#     return unique_colors

# # 示例：读取一个 .bmp 文件并统计颜色
# image_path = '/root/autodl-tmp/zuoyougu/caise/zhang_447.bmp'  # 替换成你的 BMP 图像路径
# unique_colors = get_unique_colors(image_path)

# # 如果你想查看这些颜色，可以打印出来
# print(f"不同的颜色有：{unique_colors}")

#遍历文件夹
import os
from PIL import Image

# 获取单个图像的唯一颜色
def get_unique_colors(image_path):
    # 打开图像
    image = Image.open(image_path)
    # 将图像转换为 RGB 模式（即使它是其他模式，也能确保处理每个像素的颜色信息）
    image = image.convert("RGB")
    # 获取图像中的所有像素颜色
    pixels = image.getdata()
    # 使用集合来去重（集合中的元素是唯一的）
    unique_colors = set(pixels)
    return unique_colors

# 遍历文件夹中的所有 .bmp 文件，统计每个文件的颜色
def process_folder(folder_path):
    all_unique_colors = set()
    
    for filename in os.listdir(folder_path):
        # 只处理 .bmp 文件
        if filename.lower().endswith('.bmp'):
            image_path = os.path.join(folder_path, filename)
            unique_colors = get_unique_colors(image_path)
            print(f"图像 {filename} 有 {len(unique_colors)} 种不同的颜色。")
            all_unique_colors.update(unique_colors)  # 将每个图像的颜色添加到总集合中

    print(f"\n文件夹中所有图像的总共有 {len(all_unique_colors)} 种不同的颜色。")
    print("不同颜色的颜色值如下：")
    for color in all_unique_colors:
        print(color)  # 逐行打印颜色值 (R, G, B)
    
    return all_unique_colors

# 示例：指定你的文件夹路径
folder_path = '/root/autodl-tmp/zuoyougu/mask/a'  # 替换为你的文件夹路径
all_unique_colors = process_folder(folder_path)



