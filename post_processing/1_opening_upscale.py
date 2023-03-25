import cv2 as cv
import numpy as np
from osgeo import gdal
import json
from pathlib import Path
from multiprocessing import Pool


def GdalReprojectImage(srcFilePath, resampleFactor, saveFolderPath):
    """
	栅格重采样,最近邻(gdal.gdalconst.GRA_NearestNeighbour)，
	采样方法自选。
	:param srcFilePath:
	:param saveFolderPath:
	:return:
	"""
    # 载入原始栅格
    dataset = gdal.Open(srcFilePath, gdal.GA_ReadOnly)
    srcProjection = dataset.GetProjection()
    srcGeoTransform = dataset.GetGeoTransform()
    srcWidth = dataset.RasterXSize
    srcHeight = dataset.RasterYSize
    srcBandCount = dataset.RasterCount
    srcNoDatas = [dataset.GetRasterBand(bandIndex).GetNoDataValue() for bandIndex in range(1, srcBandCount + 1)]
    srcBandDataType = dataset.GetRasterBand(1).DataType
    srcFileName = os.path.basename(srcFilePath)
    name = os.path.splitext(srcFileName)[0]
    # 创建重采样后的栅格
    outFileName = name + ".tif"
    outFilePath = os.path.join(saveFolderPath, outFileName)
    driver = gdal.GetDriverByName('GTiff')
    outWidth = int(srcWidth * resampleFactor)
    outHeight = int(srcHeight * resampleFactor)
    outDataset = driver.Create(outFilePath, outWidth, outHeight, srcBandCount, srcBandDataType)
    geoTransforms = list(srcGeoTransform)
    geoTransforms[1] = geoTransforms[1] / resampleFactor
    geoTransforms[5] = geoTransforms[5] / resampleFactor
    outGeoTransform = tuple(geoTransforms)
    outDataset.SetGeoTransform(outGeoTransform)
    outDataset.SetProjection(srcProjection)
    for bandIndex in range(1, srcBandCount + 1):
        band = outDataset.GetRasterBand(bandIndex)
        band.SetNoDataValue(srcNoDatas[bandIndex - 1])
    gdal.ReprojectImage(
        dataset,
        outDataset,
        srcProjection,
        srcProjection,
        gdal.gdalconst.GRA_NearestNeighbour,
        0.0,
        0.0,
    )
    return


def morph_open(img, kernel_size):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    open_m = cv.morphologyEx(img, cv.MORPH_OPEN, kernel)
    return open_m


def mp_wrapper(source_path: Path, output_path: Path):
    resampleFactor = 2
    target_path = output_path / f'{source_path.name[:-4]}_opened.tif'
    source = gdal.Open(str(source_path))
    target = source.GetDriver().CreateCopy(str(target_path), source)
    band = target.GetRasterBand(1)

    srcProjection = target.GetProjection()
    srcGeoTransform = target.GetGeoTransform()
    srcWidth = target.RasterXSize
    srcHeight = target.RasterYSize
    srcBandDataType = target.GetRasterBand(1).DataType
    srcNoDatas = band.GetNoDataValue()

    outWidth = int(srcWidth * resampleFactor)
    outHeight = int(srcHeight * resampleFactor)

    geoTransforms = list(srcGeoTransform)
    geoTransforms[1] = geoTransforms[1] / resampleFactor
    geoTransforms[5] = geoTransforms[5] / resampleFactor
    outGeoTransform = tuple(geoTransforms)
    target.SetGeoTransform(outGeoTransform)
    target.SetProjection(srcProjection)

    gdal.ReprojectImage(
        target,
        target,
        srcProjection,
        srcProjection,
        gdal.gdalconst.GRA_NearestNeighbour,
        0.0,
        0.0,
    )

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
