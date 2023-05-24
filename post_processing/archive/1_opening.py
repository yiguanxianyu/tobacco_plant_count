import json
from multiprocessing import Pool
from pathlib import Path

import cv2 as cv
import numpy as np
from osgeo import gdal


def morph_open(img, kernel_size):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    open_m = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
    return open_m


def mp_wrapper(source_path: Path, output_path: Path):
    target_path = output_path / f'{source_path.name[:-4]}_opened.tif'
    source = gdal.Open(str(source_path))
    target = source.GetDriver().CreateCopy(str(target_path), source)
    band = target.GetRasterBand(1)
    result = morph_open(band.ReadAsArray(), 3)
    band.WriteArray(result)
    band.FlushCache()
    band.SetNoDataValue(0)


if __name__ == '__main__':
    env = json.load(open('C:/Users/xianyu/GraduationProject/env.json'))
    input_path = Path(env['base_dir']) / '3_predict_result'
    output_path = Path(env['output_dir']) / '1_opening'

    pool = Pool(16)  # 创建进程池

    for source_path in input_path.rglob('*.tif'):
        args = (source_path, output_path)
        pool.apply_async(func=mp_wrapper, args=args)

    pool.close()
    pool.join()

    # for source_path in input_path.rglob('*.tif'):
    #     filename = source_path.name
    #     filename_without_ext = filename[:-4]
    #     target_path = output_path / f'{source_path.name[:-4]}_opened.tif'

    #     source = gdal.Open(str(source_path))
    #     target = source.GetDriver().CreateCopy(str(target_path), source)
    #     band = target.GetRasterBand(1)
    #     result = morph_open(band.ReadAsArray(), 3)
    #     band.WriteArray(result)
    #     band.FlushCache()
    #     band.SetNoDataValue(0)
