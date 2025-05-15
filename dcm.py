# import SimpleITK as sitk
# import os

# #dcm转nii.gz格式
# def dcm2nii():
#     # data_path = 'F:/natong/SpineData/case1/Spine3DImage(1)/Spine3DImage/0403103718'
#     data_path = 'zuoyougu/input'
#     save_fold = 'zuoyougu/output_input'
#     series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_path)
#     print(len(series_IDs))
#     series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_path, series_IDs[0])
#     series_reader = sitk.ImageSeriesReader()
#     series_reader.SetFileNames(series_file_names)
#     image = series_reader.Execute()
#     # print(os.path.join(save_path, fold + '.nii'))
#     # print(os.path.split(data_path))
#     sitk.WriteImage(image, os.path.join(save_fold, 'dukemei.nii.gz'))

# if __name__ == '__main__':
#     dcm2nii()


import SimpleITK as sitk
import os

# dcm转nii.gz格式
def dcm2nii():
    # 设置输入和输出文件夹路径
    data_path = 'zuoyougu/input'
    save_fold = 'zuoyougu/output_input'
    
    # 获取 DICOM 文件系列的 ID
    series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_path)
    print(len(series_IDs))
    
    # 获取该系列的文件名
    series_file_names = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_path, series_IDs[0])
    
    # 创建图像读取器并读取图像
    series_reader = sitk.ImageSeriesReader()
    series_reader.SetFileNames(series_file_names)
    image = series_reader.Execute()

    # 设置 spacing 为 (1, 1, 1)
    image.SetSpacing((1.0, 1.0, 1.0))

    # 设置 origin 为 (0, 0, 0)
    image.SetOrigin((0.0, 0.0, 0.0))

    # 将修改后的图像保存为 nii.gz 格式
    sitk.WriteImage(image, os.path.join(save_fold, 'dukemei.nii.gz'))

if __name__ == '__main__':
    dcm2nii()

    
