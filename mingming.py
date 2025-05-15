import os
import glob
import shutil

def rename_and_move_bmp_files(source_folder, target_folder):

    # 确保目标文件夹存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    # 获取所有符合命名模式的 .bmp 文件
    bmp_files = sorted(glob.glob(os.path.join(source_folder, 'zhang lin_Axial+000***-000.bmp')))
    print(bmp_files)
    # 遍历文件，按序重命名并移动
    for index, bmp_file in enumerate(bmp_files):
        # 提取原文件名
        old_name = os.path.basename(bmp_file)

        # 生成新的文件名，确保编号为3位数格式（如 000, 001, 002）
        new_name = f"zhang_{index:03d}.bmp"

        # 构造目标文件路径
        new_file_path = os.path.join(target_folder, new_name)

        # 复制文件到目标文件夹并重命名
        shutil.copy2(bmp_file, new_file_path)

        print(f"已重命名并移动: {bmp_file} -> {new_file_path}")

# 设置源文件夹和目标文件夹路径
source_folder = "/root/autodl-tmp/zuoyougu/mask"  # 请替换为实际的源文件夹路径
target_folder = os.path.join(source_folder, "a")  # 目标文件夹为 "a"

# 执行重命名和移动操作
rename_and_move_bmp_files(source_folder, target_folder)


