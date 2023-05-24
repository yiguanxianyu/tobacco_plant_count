import json
from multiprocessing import Pool
from pathlib import Path

import rasterio
from skimage.morphology import skeletonize


def skeletonize_raster(source_path: Path | str, target_path: Path | str) -> None:
    with rasterio.open(source_path) as src:
        band_count = src.count
        new_dataset = rasterio.open(target_path,
                                    "w",
                                    driver='GTiff',
                                    width=src.width,
                                    height=src.height,
                                    count=band_count,
                                    crs=src.crs,
                                    transform=src.transform,
                                    dtype=rasterio.uint8)

        for band in range(1, 1 + band_count):
            data = src.read(band)
            output = skeletonize(data)
            new_dataset.write(output, band)

        new_dataset.write(output, 1)
        new_dataset.close()


def mp_wrapper(source_path: Path, output_path: Path) -> None:
    target_path = output_path / f'{source_path.name[:-4]}_skeleton.tif'
    skeletonize_raster(source_path, target_path)


if __name__ == '__main__':
    env = json.load(open(r'C:/Users/xianyu/GraduationProject/env.json'))
    base_dir = Path(env['output_dir'])
    input_path = Path(base_dir) / '1_erosion'
    output_path = Path(base_dir) / '2_skeleton'

    pool = Pool(16)  # 创建进程池

    for source_path in input_path.rglob('*.tif'):
        pool.apply_async(func=mp_wrapper, args=(source_path, output_path))

    pool.close()
    pool.join()
