"""
3D网格重建模块
从医学影像数据重建3D肿瘤模型
"""

import os
import cv2
import json
import numpy as np
import nibabel as nib
from scipy import ndimage
from skimage import measure
import base64


def refine_segmentation_smooth(mask_volume, connectivity_kernel_size=3, sigma=1.0):
    """
    温和的后处理：保留脑肿瘤的连贯形状（与demo完全一致）
    
    Args:
        mask_volume: 3D掩码体积
        connectivity_kernel_size: 连接性核大小（更小=更温和）
        sigma: 高斯平滑参数
    
    Returns:
        refined: 细化后的掩码
    """
    refined = mask_volume.copy()
    
    # 1. 轻微的高斯平滑（保留边界清晰度）
    refined = ndimage.gaussian_filter(refined, sigma=sigma)
    
    # 2. 二值化
    refined_binary = refined > 0.5
    
    # 3. 轻微的闭运算（填补小孔）
    refined_binary = ndimage.binary_closing(refined_binary, iterations=1)
    
    # 4. 轻微的膨胀（修复断开的连接）
    refined_binary = ndimage.binary_dilation(refined_binary, iterations=1)
    
    # 5. 只保留最大的连通区域（去除所有离散小块）
    labeled = measure.label(refined_binary)
    if labeled.max() > 0:
        regions = measure.regionprops(labeled)
        # 找到体积最大的区域
        largest_region = max(regions, key=lambda r: r.area)
        
        cleaned = np.zeros_like(refined_binary, dtype=bool)
        cleaned[labeled == largest_region.label] = True
        refined_binary = cleaned
    
    # 6. 再次平滑（使边界光滑）
    refined = ndimage.gaussian_filter(
        refined_binary.astype(np.float32), 
        sigma=sigma
    )
    
    return refined


def reconstruct_3d_from_slices(mask_slices, spacing=(1.0, 1.0, 1.0), smooth=True):
    """
    从2D掩码切片重建3D网格
    
    Args:
        mask_slices: List of 2D masks (0-255)
        spacing: 体素间距 (x, y, z)
        smooth: 是否进行平滑处理
        
    Returns:
        vertices: 顶点数组 (N, 3)
        faces: 面数组 (M, 3)
        normals: 法向量数组 (N, 3)
        volume: 肿瘤体积 (立方毫米)
    """
    # 构建3D体积
    mask_3d = np.stack(mask_slices, axis=2).astype(np.float32) / 255.0
    
    # 后处理
    if smooth:
        mask_3d = refine_segmentation_smooth(mask_3d)
    
    # 检查数据范围
    data_min, data_max = float(mask_3d.min()), float(mask_3d.max())
    print(f"肿瘤掩码数据范围: min={data_min:.4f}, max={data_max:.4f}")
    
    # 确保有足够的前景体素
    foreground_voxels = int(np.sum(mask_3d > 0.5))
    print(f"前景体素数 (>0.5): {foreground_voxels}")
    
    if foreground_voxels < 100:
        print(f"[错误] 前景体素太少 ({foreground_voxels} < 100)，无法重建网格")
        return None, None, None, 0
    
    # Marching cubes重建
    try:
        # 确保level在数据范围内
        level = 0.5
        if data_max < level:
            level = data_max * 0.5
            print(f"[警告] 调整level为 {level:.4f}")
        
        vertices, faces, normals, values = measure.marching_cubes(
            mask_3d,
            level=level,
            spacing=spacing
        )
        
        # 计算体积
        volume = np.sum(mask_3d > 0.5) * np.prod(spacing)
        
        return vertices, faces, normals, volume
    except Exception as e:
        print(f"Marching cubes失败: {e}")
        return None, None, None, 0


def extract_brain_outline(volume, spacing=(1.0, 1.0, 1.0)):
    """
    提取脑部轮廓作为背景参考（基于demo实现）
    
    Args:
        volume: 3D MRI体积数据
        spacing: 体素间距 (x, y, z)
        
    Returns:
        brain_data: 包含vertices和faces的字典，失败返回None
    """
    import sys
    try:
        print(f"[信息] 开始提取脑部轮廓，体积尺寸: {volume.shape}")
        sys.stdout.flush()
        
        # 检查体积数据范围
        vol_min, vol_max = float(volume.min()), float(volume.max())
        vol_mean = float(volume.mean())
        print(f"   体积数据范围: min={vol_min:.2f}, max={vol_max:.2f}, mean={vol_mean:.2f}")
        
        # 1. 简单的阈值处理（使用10%百分位，与demo一致）
        threshold_value = np.percentile(volume, 10)
        
        # 自适应调整：如果阈值太低，使用均值的10%
        if threshold_value < vol_mean * 0.05:
            threshold_value = vol_mean * 0.1
            print(f"   [警告] 10%百分位过低，使用均值的10%作为阈值")
        
        brain_mask = (volume > threshold_value).astype(np.float32)
        brain_voxels = int(np.sum(brain_mask))
        print(f"   阈值: {threshold_value:.2f}, 脑组织体素数: {brain_voxels}")
        
        # 检查是否有足够的体素
        if brain_voxels < 1000:
            print(f"   [错误] 脑组织体素数太少 ({brain_voxels} < 1000)，尝试降低阈值")
            threshold_value = np.percentile(volume, 5)
            brain_mask = (volume > threshold_value).astype(np.float32)
            brain_voxels = int(np.sum(brain_mask))
            print(f"   使用5%百分位: 阈值={threshold_value:.2f}, 体素数={brain_voxels}")
        
        # 2. 清除边缘（防止出现方形外框）
        brain_mask[0:2, :, :] = 0
        brain_mask[-2:, :, :] = 0
        brain_mask[:, 0:2, :] = 0
        brain_mask[:, -2:, :] = 0
        brain_mask[:, :, 0:2] = 0
        brain_mask[:, :, -2:] = 0
        
        # 3. 平滑处理
        brain_mask = ndimage.gaussian_filter(brain_mask, sigma=1.5)
        print(f"   平滑处理完成，非零体素数: {int(np.sum(brain_mask > 0.1))}")
        
        # 检查平滑后是否还有数据
        if np.sum(brain_mask > 0.1) < 100:
            print(f"   [错误] 平滑后数据太少，无法生成网格")
            return None
        
        # 检查平滑后的数据范围
        smooth_min, smooth_max = float(brain_mask.min()), float(brain_mask.max())
        print(f"   平滑后数据范围: min={smooth_min:.4f}, max={smooth_max:.4f}")
        
        # 动态选择level - 确保在数据范围内
        if smooth_max < 0.1:
            # 如果最大值小于0.1，使用最大值的50%
            level = smooth_max * 0.5
            print(f"   [警告] 数据范围较小，使用自适应level={level:.4f}")
        else:
            # 使用0.1或数据的10%，取较小值
            level = min(0.1, smooth_max * 0.1)
            print(f"   使用level={level:.4f}")
        
        # Marching cubes提取脑壳轮廓
        print(f"   开始Marching cubes (level={level:.4f}, spacing={spacing})...")
        b_verts, b_faces, _, _ = measure.marching_cubes(brain_mask, level=level, spacing=spacing)
        
        # 验证数据有效性
        if len(b_verts) == 0 or len(b_faces) == 0:
            print(f"[错误] Marching cubes返回空数据: 顶点={len(b_verts)}, 面={len(b_faces)}")
            return None
        
        print(f"[成功] 脑部轮廓提取完成: 顶点数={len(b_verts)}, 面数={len(b_faces)}")
        print(f"   顶点范围: min={b_verts.min(axis=0)}, max={b_verts.max(axis=0)}")
        
        return {
            'vertices': b_verts.tolist(),
            'faces': b_faces.tolist()
        }
    except Exception as e:
        print(f"[错误] 提取脑部轮廓失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return None


def reconstruct_3d_from_nii(nii_path, predictor, spacing=(1.0, 1.0, 1.0), include_brain_outline=True):
    """
    从NII文件重建3D模型（使用UNet逐切片预测）
    
    Args:
        nii_path: NII文件路径
        predictor: UNet预测器实例 (BrainTumorPredictor)
        spacing: 体素间距 (x, y, z)
        include_brain_outline: 是否包含脑部轮廓
        
    Returns:
        reconstruction_data: 包含vertices, faces等的字典，失败返回None
    """
    try:
        # 加载NII文件
        nii = nib.load(nii_path)
        volume = nii.get_fdata()
        H, W, D = volume.shape
        
        print(f"NII文件尺寸: {H} x {W} x {D}")
        
        # 逐切片预测
        masks = []
        for i in range(D):
            slice_img = volume[:, :, i]
            
            # 归一化到0-255
            slice_img = cv2.normalize(
                slice_img, None, 0, 255, cv2.NORM_MINMAX
            ).astype(np.uint8)
            
            # UNet预测
            mask, _ = predictor.predict_array(slice_img)
            masks.append(mask)
            
            # 进度日志
            if (i + 1) % max(1, D // 10) == 0:
                print(f"  UNet预测进度: {i+1}/{D}")
        
        # 3D重建肿瘤
        vertices, faces, normals, tumor_volume = reconstruct_3d_from_slices(
            masks, spacing=spacing, smooth=True
        )
        
        if vertices is None or len(vertices) == 0:
            print("警告: Marching cubes未生成有效网格")
            return None
        
        print(f"肿瘤3D重建完成: 顶点数={len(vertices)}, 面数={len(faces)}, 体积={tumor_volume:.2f}mm³")
        
        result = {
            'vertices': vertices.tolist(),
            'faces': faces.tolist(),
            'normals': normals.tolist(),
            'volume': float(tumor_volume),
            'dimensions': {'height': H, 'width': W, 'depth': D},
            'voxel_count': int(np.sum(np.stack(masks, axis=2) > 127)),
            'spacing': list(spacing)
        }
        
        # 提取脑部轮廓
        if include_brain_outline:
            print("[信息] 准备提取脑部轮廓...")
            try:
                brain_data = extract_brain_outline(volume, spacing)
                if brain_data:
                    result['brain_outline'] = brain_data
                    print(f"[成功] 脑部轮廓已添加到结果中")
                else:
                    print("[警告] 脑部轮廓提取返回None")
            except Exception as brain_error:
                print(f"[错误] 脑部轮廓提取异常: {brain_error}")
                import traceback
                traceback.print_exc()
        else:
            print("[跳过] 跳过脑部轮廓提取（include_brain_outline=False）")
        
        return result
        
    except Exception as e:
        print(f"reconstruct_3d_from_nii失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def export_to_stl(vertices, faces, output_path):
    """
    导出为STL文件格式
    
    Args:
        vertices: 顶点数组
        faces: 面数组
        output_path: 输出路径
    """
    with open(output_path, 'w') as f:
        f.write('solid tumor\n')
        
        for face in faces:
            # 计算法向量
            v0, v1, v2 = vertices[face]
            normal = np.cross(v1 - v0, v2 - v0)
            normal = normal / (np.linalg.norm(normal) + 1e-8)
            
            f.write(f'  facet normal {normal[0]} {normal[1]} {normal[2]}\n')
            f.write('    outer loop\n')
            f.write(f'      vertex {v0[0]} {v0[1]} {v0[2]}\n')
            f.write(f'      vertex {v1[0]} {v1[1]} {v1[2]}\n')
            f.write(f'      vertex {v2[0]} {v2[1]} {v2[2]}\n')
            f.write('    endloop\n')
            f.write('  endfacet\n')
        
        f.write('endsolid tumor\n')


def mesh_to_json(vertices, faces, normals):
    """
    将mesh数据转换为JSON格式（用于前端Three.js）
    
    Returns:
        json_str: JSON字符串
    """
    data = {
        'vertices': vertices.tolist() if isinstance(vertices, np.ndarray) else vertices,
        'faces': faces.tolist() if isinstance(faces, np.ndarray) else faces,
        'normals': normals.tolist() if isinstance(normals, np.ndarray) else normals,
    }
    return json.dumps(data)
