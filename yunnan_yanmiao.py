#!/.conda/envs/learn python
# -*- coding: utf-8 -*-

"""
统计烟苗的个数
~~~~~~~~~~~~~~~~
code by wHy
Aerospace Information Research Institute, Chinese Academy of Sciences
751984964@qq.com
"""

from osgeo import gdal
import os
from osgeo import ogr
from pathlib import Path

# os.environ['GDAL_DATA'] = r'C:\Users\75198\.conda\envs\learn\Lib\site-packages\GDAL-2.4.1-py3.6-win-amd64.egg-info\gata-data' #防止报error4错误

gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
gdal.SetConfigOption("SHAPE_ENCODING", "GBK")

yanmiao_ori = r'./yunnan_test/UAV_yunnan_first_15_label.shp'
yanmiao_output = r'./yunnan_test/UAV_yunnan_first_15_label_point'

ogr.RegisterAll()# 注册所有的驱动

driver = ogr.GetDriverByName('ESRI Shapefile')

shp_yanmiao_ori = ogr.Open(yanmiao_ori, 1) # 0只读模式，1读写模式
if shp_yanmiao_ori is None:
    print('Failed to open shp_yanmiao_ori')
print(shp_yanmiao_ori.GetLayerCount())

ly_yanmiao = shp_yanmiao_ori.GetLayer() # 读取图层
print(ly_yanmiao.GetFeatureCount()) # 统计要素个数

'''新建烟苗统计点矢量'''
if Path(yanmiao_output).exists():
    driver.DeleteDataSource(yanmiao_output)
out_ds = driver.CreateDataSource(yanmiao_output)
print(out_ds)

#
# out_lyr = out_ds.CreateLayer(yanmiao_output, ly_yanmiao.GetSpatialRef(), ogr.wkbPoint)
# def_out_feature = out_lyr.GetLayerDefn() # 读取feature类型
#
# '''遍历烟苗多边形'''
# for i in range((ly_yanmiao.GetFeatureCount())):
#     feat = ly_yanmiao.GetFeature(i)
#     outfeat = ogr.Feature(def_out_feature)
#     geom = feat.GetGeometryRef() # 几何
#     centroids = geom.Centroid() # 中心点
#     outfeat.SetGeometry(centroids)
#     out_lyr.CreateFeature(outfeat)
#     outfeat = None