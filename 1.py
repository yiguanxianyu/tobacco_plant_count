# 方向包围盒切割法
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
from math import sin, cos, radians, asin, sqrt


def HAV(p1, p2):
    """
    半正矢公式，用于计算一对以经纬度坐标表示的点之间的距离
    p[0]为经度, p[1]为纬度，均以度数表示
    """
    lam1, lam2 = radians(p1[0]), radians(p2[0])
    phi1, phi2 = radians(p1[1]), radians(p2[1])
    arg1 = sin((phi1 - phi2) / 2)
    arg2 = sin((lam1 - lam2) / 2)
    arg3 = cos(phi1) * cos(phi2)

    return 2 * 6371000 * asin(sqrt(arg1 * arg1 + arg3 * arg2 * arg2))


def cut_obb(obb, num1, num2):
    """
    将方向包围盒切分为 num1*num2 的格网，具体情况如下图所示
    方向包围盒由 geom.minimum_rotated_rectangle.exterior.coords 方法生成
              num1
    p4 +----------------+ p3
       |                |
       |                | num2
       |                |
    p1 +----------------+ P2
    """
    p1, p2, p3, p4 = Point(obb[0]), Point(obb[1]), Point(obb[2]), Point(obb[3])
    line1, line2 = LineString([p1, p2]), LineString([p4, p3])

    points = []
    # 生成格网中间的点
    for i in range(num1 + 1):
        # 以线性插值的方式获取，normalized=True意味着总长度被视为1
        pointA = line1.interpolate(i / num1, normalized=True)
        pointB = line2.interpolate(i / num1, normalized=True)
        curr_line = LineString([pointA, pointB])
        curr_row = [curr_line.interpolate(i / num2, normalized=True) for i in range(num2 + 1)]
        points.append(curr_row)

    polygons = []
    # 将格网点连接成格网，即为每个烟苗植株所在的格网
    for i in range(num1):
        row1, row2 = points[i], points[i + 1]
        polygons.extend(Polygon([row1[j], row2[j], row2[j + 1], row1[j + 1]]) for j in range(num2))

    return polygons


# 输入的识别文件，注意此文件应当预先由栅格格式转为面矢量格式
input_path = './input/P061308_result.shp'
# 用于参考的划分的距离间隔，在本示例中为0.7m左右
interval = 0.7
half_interval = interval * 0.5
input_file = gpd.GeoSeries.from_file(input_path)

lst = []
for geom in input_file:
    # 获取方向包围盒
    obb = geom.minimum_rotated_rectangle.exterior
    p1, p2, p3, p4, _ = list(obb.coords)

    edge1, edge2 = HAV(p1, p2), HAV(p2, p3)
    # 判断要划分的格网数量
    cut_num_1 = round(edge1 / interval) + int(edge1 < half_interval)
    cut_num_2 = round(edge2 / interval) + int(edge2 < half_interval)

    lst.append(gpd.GeoSeries(cut_obb(obb.coords, cut_num_1, cut_num_2)))

# 收集生成的所有格网
recs = pd.concat(lst)
recs.to_file(f'./output/cut_rec_{interval}m.shp')
# 生成格网的中心点作为烟苗植株的位置
recs.centroid.to_file(f'./output/cut_rec_{interval}m_centroid.shp')