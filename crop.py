import nibabel as nib
import numpy as np

# 加载CT图像和对应的Mask图像
ct_image_path = "/root/autodl-tmp/zuoyougu/output_input/dukemei.nii.gz"  # 替换为CT图像文件路径
mask_image_path = "/root/autodl-tmp/zuoyougu/output_data.nii.gz"  # 替换为Mask图像文件路径

# 读取CT图像和Mask图像
ct_img = nib.load(ct_image_path)
mask_img = nib.load(mask_image_path)

# 获取CT图像的数据数组
ct_data = ct_img.get_fdata()

# 获取Mask图像的数据数组
mask_data = mask_img.get_fdata()

# 创建一个新的CT图像，只保留胫骨部分
# 将所有非胫骨区域（mask值不为100）置为0
ct_data_tibia_only = np.where(mask_data == 5, ct_data, ct_data.min())

# 创建新的Mask图像，只保留胫骨部分s
# 将所有非胫骨区域（mask值不为100）置为0
mask_data_tibia_only = np.where(mask_data == 5, mask_data, 0)

# 创建新的NIfTI图像，保留CT图像的头信息和仿射矩阵
new_ct_img = nib.Nifti1Image(ct_data_tibia_only, ct_img.affine, ct_img.header)

# 创建新的Mask图像，保留原Mask图像的头信息和仿射矩阵
new_mask_img = nib.Nifti1Image(mask_data_tibia_only, mask_img.affine, mask_img.header)

# 保存新的CT图像
new_ct_image_path = "/root/autodl-tmp/output/cropped_ct_lingyice.nii.gz"  # 保存路径
nib.save(new_ct_img, new_ct_image_path)

# 保存新的Mask图像
new_mask_image_path =  "/root/autodl-tmp/output/cropped_mask_lingyice.nii.gz"  # 保存路径
nib.save(new_mask_img, new_mask_image_path)

print(f"处理后的CT图像已保存为: {new_ct_image_path}")
print(f"处理后的Mask图像已保存为: {new_mask_image_path}")