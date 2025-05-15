import SimpleITK as sitk
import vtk
import numpy as np
import open3d as o3d
from vtk.util import numpy_support
#该代码用于将镜像后的对侧图像和掩码与当前侧的图像和掩码进行匹配
def mirror_ct_and_mask(ct_path, mask_path, output_ct, output_mask):
    """镜像处理CT和掩膜"""
    # 镜像CT
    ct = sitk.ReadImage(ct_path)
    mirror_ct = sitk.Flip(ct, [True, False, False])  # 水平翻转
    sitk.WriteImage(mirror_ct, output_ct)
    
    # 镜像Mask
    mask = sitk.ReadImage(mask_path)
    mirror_mask = sitk.Flip(mask, [True, False, False])
    sitk.WriteImage(mirror_mask, output_mask)

def create_bone_mesh(ct_path, mask_path, output_stl):
    """创建带Mask约束的三维骨骼模型"""
    # 读取CT和Mask
    ct = sitk.ReadImage(ct_path)
    mask = sitk.ReadImage(mask_path)
    
    # 将数据转换为VTK格式
    vtk_ct = sitk_to_vtk(ct)
    vtk_mask = sitk_to_vtk(mask)
    
    # 应用Mask
    masked_ct = vtk.vtkImageMask()
    masked_ct.SetMaskInputData(vtk_mask)
    masked_ct.SetImageInputData(vtk_ct)
    masked_ct.NotMaskOn()
    masked_ct.Update()
    
    # 三维重建（Marching Cubes优化版）
    mc = vtk.vtkDiscreteMarchingCubes()
    mc.SetInputConnection(masked_ct.GetOutputPort())
    mc.GenerateValues(1, 1, 1)  # 仅提取mask=1的区域
    mc.Update()
    
    # 简化网格
    decimate = vtk.vtkDecimatePro()
    decimate.SetInputConnection(mc.GetOutputPort())
    decimate.SetTargetReduction(0.7)
    decimate.Update()
    
    # 保存STL
    writer = vtk.vtkSTLWriter()
    writer.SetFileName(output_stl)
    writer.SetInputConnection(decimate.GetOutputPort())
    writer.Write()

def sitk_to_vtk(sitk_image):
    """将SimpleITK图像转换为VTK图像"""
    np_array = sitk.GetArrayFromImage(sitk_image).transpose(2,1,0)
    vtk_data = numpy_support.numpy_to_vtk(np_array.ravel(), deep=1)
    
    vtk_image = vtk.vtkImageData()
    vtk_image.SetDimensions(sitk_image.GetSize())
    vtk_image.SetSpacing(sitk_image.GetSpacing())
    vtk_image.SetOrigin(sitk_image.GetOrigin())
    vtk_image.GetPointData().SetScalars(vtk_data)
    return vtk_image

def enhanced_icp_registration(source_stl, target_stl):
    """改进的ICP配准算法：加入NMS和动态离群点剔除"""
    # 加载模型
    source = o3d.io.read_triangle_mesh(source_stl)
    target = o3d.io.read_triangle_mesh(target_stl)
    
    # 预处理：法线估计和特征提取
    source.compute_vertex_normals()
    target.compute_vertex_normals()
    
    # 使用FPFH特征进行粗配准
    source_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        source, o3d.geometry.KDTreeSearchParamHybrid(radius=5.0, max_nn=100))
    target_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        target, o3d.geometry.KDTreeSearchParamHybrid(radius=5.0, max_nn=100))
    
    # RANSAC粗配准（更严格的内点筛选）
    result_ransac = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source, target, source_fpfh, target_fpfh, 
        mutual_filter=True,
        max_correspondence_distance=3.0,  # 更小的初始距离阈值
        estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        ransac_n=4,  # 增加采样点数
        checkers=[
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.8),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(2.0)
        ],
        criteria=o3d.pipelines.registration.RANSACConvergenceCriteria(50000, 0.99)
    )
    
    # 动态离群点剔除的ICP
    def dynamic_outlier_rejection(transformation):
        # 获取当前对应点距离
        source_points = np.asarray(source.vertices)
        target_points = np.asarray(target.vertices)
        transformed_points = (transformation[:3, :3] @ source_points.T + transformation[:3, 3]).T
        
        # 建立KDTree快速查询最近点
        target_tree = o3d.geometry.KDTreeFlann(target)
        distances = []
        for pt in transformed_points:
            _, idx, _ = target_tree.search_knn_vector_3d(pt, 1)
            distances.append(np.linalg.norm(pt - target_points[idx[0]]))
        distances = np.array(distances)
        
        # 动态阈值：基于中位数和标准差
        median_dist = np.median(distances)
        std_dist = np.std(distances)
        valid_mask = distances < (median_dist + 3 * std_dist)  # 剔除超过3σ的点
        
        # 非极大值抑制：仅保留前80%的最近点
        sorted_indices = np.argsort(distances)
        valid_mask[sorted_indices[int(0.8*len(sorted_indices)):]] = False
        
        return valid_mask

    # 自定义ICP循环（带离群点剔除）
    current_trans = result_ransac.transformation
    for _ in range(5):  # 迭代5次
        valid_mask = dynamic_outlier_rejection(current_trans)
        valid_source = source.select_by_mask(valid_mask)
        
        # 执行ICP（仅使用有效点）
        result_icp = o3d.pipelines.registration.registration_icp(
            valid_source, target, 
            max_correspondence_distance=2.0,
            init=current_trans,
            estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPlane(),
            criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=50)
        )
        current_trans = result_icp.transformation
    
    return current_trans

def apply_transformation_matrix(ct_path, matrix, reference_ct, output_path):
    """应用变换矩阵到CT图像"""
    # 创建仿射变换
    affine = sitk.AffineTransform(3)
    affine.SetMatrix(matrix[:3, :3].flatten().tolist())
    affine.SetTranslation(matrix[:3, 3].tolist())
    
    # 设置重采样参数
    resampler = sitk.ResampleImageFilter()
    resampler.SetReferenceImage(sitk.ReadImage(reference_ct))
    resampler.SetInterpolator(sitk.sitkLinear)
    resampler.SetDefaultPixelValue(-1000)  # CT空气值
    resampler.SetTransform(affine)
    
    # 执行重采样
    moving_ct = sitk.ReadImage(ct_path)
    resampled_ct = resampler.Execute(moving_ct)
    sitk.WriteImage(resampled_ct, output_path)

def main():
    # 输入文件
    left_ct = "/root/autodl-tmp/output/cropped_ct_good.nii.gz"
    left_mask = "/root/autodl-tmp/output/cropped_mask_good.nii.gz"
    right_ct = "/root/autodl-tmp/output/cropped_ct_bad.nii.gz"
    right_mask = "/root/autodl-tmp/output/cropped_mask_bad.nii.gz"
    
    # Step 1: 生成镜像CT和Mask
    mirrored_ct = "/root/autodl-tmp/peizhun/mirrored_good_ct.nii.gz"
    mirrored_mask = "/root/autodl-tmp/peizhun/mirrored_good_mask.nii.gz"
    mirror_ct_and_mask(left_ct, left_mask, mirrored_ct, mirrored_mask)
    
    # Step 2: 创建三维模型
    create_bone_mesh(mirrored_ct, mirrored_mask, "/root/autodl-tmp/peizhun/mirrored_good.stl")
    create_bone_mesh(right_ct, right_mask, "/root/autodl-tmp/peizhun/original_bad.stl")
    
    # Step 3: 改进的ICP配准
    transform_matrix = enhanced_icp_registration("/root/autodl-tmp/peizhun/mirrored_good.stl", "/root/autodl-tmp/peizhun/original_bad.stl")
    print(f"Optimized Transformation Matrix:\n{transform_matrix}")
    
    # Step 4: 应用变换矩阵
    apply_transformation_matrix(mirrored_ct, transform_matrix, right_ct, "/root/autodl-tmp/peizhun/aligned_mirrored_ct.nii.gz")
    apply_transformation_matrix(right_ct, np.linalg.inv(transform_matrix), mirrored_ct, "/root/autodl-tmp/peizhun/aligned_original_ct.nii.gz")
    
    # 结果验证
    print("配准完成，结果保存在：")
    print("- aligned_mirrored_ct.nii.gz")
    print("- aligned_original_ct.nii.gz")

if __name__ == "__main__":
    main()
