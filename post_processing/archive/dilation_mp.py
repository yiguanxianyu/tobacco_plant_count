from multiprocessing import Pool
from pathlib import Path

import numpy as np
import rasterio
from rasterio.crs import CRS
from rasterio.warp import calculate_default_transform, reproject
from skan import Skeleton, summarize
from skimage import morphology


def run(input_raster, output_raster):
    print(f'{input_raster.name} start')
    src = rasterio.open(input_raster)
    # 创建一个rasterio.crs.CRS对象来表示目标坐标系
    output_crs = CRS.from_epsg(32647)
    # 使用rasterio.warp.calculate_default_transform函数进行转换
    dst_transform, dst_width, dst_height = calculate_default_transform(src.crs, output_crs, src.width, src.height,
                                                                       *src.bounds)

    profile = src.meta.copy()
    profile.update({
        'crs': output_crs,
        'transform': dst_transform,
        'width': dst_width,
        'height': dst_height,
        'nodata': 0
    })
    src_img = np.zeros((dst_height, dst_width), dtype=profile['dtype'])
    # 重投影
    reproject(source=src.read(1),
              destination=src_img,
              src_crs=src.crs,
              src_transform=src.transform,
              dst_transform=dst_transform,
              dst_crs=output_crs,
              num_threads=4)

    src.close()
    # 连通组件分析
    kernel = morphology.square(3)  # 3*3的正方形腐蚀核
    img_eroded = morphology.erosion(src_img, kernel)  # 先腐蚀
    img_dilated = morphology.dilation(img_eroded, kernel)  # 再膨胀
    edge_dilated = img_dilated - img_eroded  # 膨胀后的图像减去腐蚀后的图像，得到边缘
    skeleton = morphology.skeletonize(edge_dilated)  # 骨架化
    sk_obj = Skeleton(skeleton)  # 骨架化对象

    branch_data = summarize(sk_obj).drop(
        columns=['coord-src-0', 'coord-src-1', 'coord-dst-0', 'coord-dst-1', 'mean-pixel-value', 'stdev-pixel-value'])

    # j2e = branch_data.loc[branch_data['branch-type'] == 1] # j2e主要是被截掉的，通常不需要考虑
    j2j = branch_data.loc[branch_data['branch-type'] == 2]  # 交合点到交合点的枝干 junction to junction
    j2j = j2j[j2j['branch-distance'] < 4]  # 寻找那些处于交点上的通路

    all_points = [sk_obj.path_coordinates(index) for index in j2j.index]
    intersected_points = np.unique(np.vstack(all_points), axis=0)
    img_dilated[intersected_points[:, 0], intersected_points[:, 1]] = 0

    with rasterio.open(output_raster, 'w', **profile) as dst:
        dst.write(img_dilated, 1)

    print(f'{input_raster.name} finished')


if __name__ == '__main__':
    pool = Pool(4)  # 创建进程池
    # 设置目录路径和文件后缀
    dir_path = Path(r'D:\UAV_DATA_NEW\3_predict_result')
    output_path = Path(r'D:\UAV_DATA_NEW\output\1_dilated_reproj')

    # 循环处理每个文件
    for input_raster in dir_path.glob(f'*.tif'):
        # 获取文件名和后缀
        file_name = input_raster.stem[0:6]
        output_raster = output_path / f'{file_name}_dilated_UTM47N.tif'

        args = (input_raster, output_raster)
        pool.apply_async(func=run, args=args)

    pool.close()
    pool.join()

# # 设置目录路径和文件后缀
# dir_path = Path(r'D:\UAV_DATA_NEW\3_predict_result')
# output_path = Path(r'D:\UAV_DATA_NEW\output\1_dilated_reproj')
# # 循环处理每个文件
# for input_raster in dir_path.glob(f'*.tif'):
#     # 获取文件名和后缀
#     file_name = input_raster.stem[0:6]
#     output_raster = output_path / f'{file_name}_dilated_UTM47N.tif'
#     run(input_raster, output_raster)
#     print(file_name)

# input_raster = r'D:\UAV_DATA_NEW\3_predict_result\000001.tif'
# output_raster = r'D:\UAV_DATA_NEW\output\dilated\000001_dilated_UTM47N.tif'

# with rasterio.open(input_raster) as src:
#     # 创建一个rasterio.crs.CRS对象来表示目标坐标系
#     output_crs = CRS.from_epsg(32647)
#     # 使用rasterio.warp.calculate_default_transform函数进行转换
#     dst_transform, dst_width, dst_height = calculate_default_transform(src.crs, output_crs, src.width, src.height,
#                                                                        *src.bounds)
#     img_raw = src.read(1)

#     profile = src.meta.copy()
#     profile.update({
#         'crs': output_crs,
#         'transform': dst_transform,
#         'width': dst_width,
#         'height': dst_height,
#         'nodata': 0
#     })
#     src_img = np.zeros((dst_height, dst_width), dtype=profile['dtype'])
#     # 重投影
#     reproject(source=src.read(1),
#               destination=src_img,
#               src_crs=src.crs,
#               src_transform=src.transform,
#               dst_transform=dst_transform,
#               dst_crs=output_crs,
#               num_threads=4)

# # 连通组件分析
# kernel = morphology.square(3)

# img_eroded = morphology.erosion(src_img, kernel)
# img_dilated = morphology.dilation(img_eroded, kernel)

# edge_dilated = img_dilated - img_eroded

# skeleton = morphology.skeletonize(edge_dilated)

# sk_obj = Skeleton(skeleton)

# branch_data = summarize(sk_obj).drop(
#     columns=['coord-src-0', 'coord-src-1', 'coord-dst-0', 'coord-dst-1', 'mean-pixel-value', 'stdev-pixel-value'])

# # j2e = branch_data.loc[branch_data['branch-type'] == 1] # j2e主要是被截掉的，通常不需要考虑
# j2j = branch_data.loc[branch_data['branch-type'] == 2]  # 交合点到交合点的枝干 junction to junction
# j2j = j2j[j2j['branch-distance'] < 4]  # 寻找那些处于交点上的通路

# all_points = [sk_obj.path_coordinates(index) for index in j2j.index]
# intersected_points = np.unique(np.vstack(all_points), axis=0)
# img_dilated[intersected_points[:, 0], intersected_points[:, 1]] = 0

# with rasterio.open(output_raster, 'w', **profile) as dst:
#     dst.write(img_dilated, 1)
