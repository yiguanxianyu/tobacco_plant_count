import json
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Polygon


def genrate_obb(source_path, target_path):
    input_file = gpd.GeoSeries.from_file(source_path)
    result = gpd.GeoSeries([Polygon(geom.minimum_rotated_rectangle.exterior) for geom in input_file])
    result.to_file(target_path, driver='ESRI Shapefile')


def mp_wrapper(source_path: Path, output_path: Path):
    target_path = output_path / f'{source_path.name[:-4]}_obb.shp'
    genrate_obb(source_path, target_path)


if __name__ == '__main__':
    env = json.load(open(r'C:/Users/xianyu/GraduationProject/env.json'))
    input_path = Path(env['output_dir']) / '2_polygonize'
    output_path = Path(env['output_dir']) / '3_obb'

    pool = Pool(16)  # 创建进程池

    for source_path in input_path.rglob('*.shp'):
        args = (source_path, output_path)
        pool.apply_async(func=mp_wrapper, args=args)

    pool.close()
    pool.join()
