import SimpleITK as sitk
import numpy as np
import os
#该代码应该是汤业的代码
def crop_ct_vert(img_path, mask_path, crop_vert_path=None, crop_vert_seg_path=None):
    """
    对原始锥体CT进行裁剪，裁剪出待配准的椎骨CT，并得到偏移量
    Args:
    img_path: 原始锥体CT路径
    mask_path: 待配准椎骨CT的mask路径
    crop_vert_path: 裁剪后的待配准椎骨CT的保存路径
    crop_vert_seg_path: 裁剪后的mask保存路径
    """
    # 读取原始锥体CT图像
    img = sitk.ReadImage(img_path)
    ct_arr = sitk.GetArrayFromImage(img)
    
    # 读取待配准椎骨CT的mask图像
    mask = sitk.ReadImage(mask_path)
    mask_arr = sitk.GetArrayFromImage(mask)
    
    # 保留mask值为1的区域，其他区域用最小值填充
    normalized_arr = np.where(mask_arr == 100, ct_arr, ct_arr.min())
    
    # 创建处理后的CT图像
    processed_img = sitk.GetImageFromArray(normalized_arr)
    processed_img.CopyInformation(img)

    # 获取mask的形状统计信息
    lesion_filter = sitk.LabelShapeStatisticsImageFilter()
    lesion_filter.Execute(mask)
    
    # 获取标签为1的区域的边界框信息
    lesion_boxing = lesion_filter.GetBoundingBox(1)
    boxing_size = (lesion_boxing[3], lesion_boxing[4], lesion_boxing[5])
    start_boxing = (lesion_boxing[0], lesion_boxing[1], lesion_boxing[2])
    
    # 获取CT图像的体积像素间距
    spacing = img.GetSpacing()
    
    # 计算图像的偏移量
    ct_center = np.array(img.GetSize()) / 2
    ver_center = np.array([start_boxing[0] + boxing_size[0] / 2,
                           start_boxing[1] + boxing_size[1] / 2,
                           start_boxing[2] + boxing_size[2] / 2])
    bx, by, bz = (ct_center - ver_center) * spacing
    
    # 裁剪图像和mask
    cropped_img = sitk.RegionOfInterest(processed_img, boxing_size, start_boxing)
    cropped_mask = sitk.RegionOfInterest(mask, boxing_size, start_boxing)
    
    # 保持原始图像的空间信息
    cropped_img.SetSpacing(img.GetSpacing())
    cropped_img.SetOrigin(img.GetOrigin())
    cropped_img.SetDirection(img.GetDirection())
    cropped_mask.SetSpacing(mask.GetSpacing())
    cropped_mask.SetOrigin(mask.GetOrigin())
    cropped_mask.SetDirection(mask.GetDirection())
    
    # 保存裁剪后的图像和mask
    if crop_vert_path:
        os.makedirs(os.path.dirname(crop_vert_path), exist_ok=True)
        sitk.WriteImage(cropped_img, crop_vert_path)
    if crop_vert_seg_path:
        os.makedirs(os.path.dirname(crop_vert_seg_path), exist_ok=True)
        sitk.WriteImage(cropped_mask, crop_vert_seg_path)
    
    return bx, by, bz

# 设置文件路径
img_path = "/root/autodl-tmp/4_t1_img.nii.gz"
mask_path = "/root/autodl-tmp/4_t1_gt.nii.gz"
crop_vert_path = "/root/autodl-tmp/output/cropped_ct.nii.gz"
crop_vert_seg_path = "/root/autodl-tmp/output/cropped_mask.nii.gz"

# 调用函数并打印偏移量
bx, by, bz = crop_ct_vert(img_path, mask_path, crop_vert_path, crop_vert_seg_path)
print(f"偏移量: bx={bx}, by={by}, bz={bz}")
