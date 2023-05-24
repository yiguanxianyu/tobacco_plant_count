import json
from multiprocessing import Pool
from pathlib import Path

from osgeo import gdal, ogr, osr


def polygonize(source_path: Path | str, target_path: Path | str) -> None:
    """
    Polygonize a raster image and save the result as a shapefile.

    :param source_path: A string or Path object pointing to the input raster image
    :param target_path: A string or Path object pointing to the output shapefile
    :return: None
    """

    sp_ref = osr.SpatialReference()
    sp_ref.SetFromUserInput('EPSG:4326')

    source = gdal.Open(str(source_path))
    source_band = source.GetRasterBand(1)
    mask_band_nodata = source_band.GetMaskBand()

    driver = ogr.GetDriverByName('ESRI Shapefile')
    dst_ds = driver.CreateDataSource(str(target_path))
    dst_layer = dst_ds.CreateLayer('pol_morphed', srs=sp_ref)

    fd = ogr.FieldDefn('DN', ogr.OFTInteger)
    dst_layer.CreateField(fd)
    dst_field = 0

    # 参数  输入栅格图像波段\掩码图像波段、矢量化后的矢量图层、需要将DN值写入矢量字段的索引、算法选项、进度条回调函数、进度条参数
    gdal.Polygonize(source_band, mask_band_nodata, dst_layer, dst_field, [], callback=None)


def mp_wrapper(source_path: Path, output_path: Path) -> None:
    target_path = output_path / f'{source_path.name[:-4]}_polygonized.shp'
    polygonize(source_path, target_path)


if __name__ == '__main__':
    env = json.load(open(r'C:/Users/xianyu/GraduationProject/env.json'))
    base_dir = Path(env['output_dir'])
    input_path = Path(base_dir) / '1_opening'
    output_path = Path(base_dir) / '2_polygonize'

    pool = Pool(16)  # 创建进程池

    for source_path in input_path.rglob('*.tif'):
        pool.apply_async(func=mp_wrapper, args=(source_path, output_path))

    pool.close()
    pool.join()
