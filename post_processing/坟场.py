# # 4. 对筛选后的矢量转回栅格
# reference_srs = source.GetProjection()
# reference_transform = source.GetGeoTransform()
# reference_cols = source.RasterXSize
# reference_rows = source.RasterYSize

# vector_ds = ogr.Open(output_vector_filtered)

# driver = gdal.GetDriverByName('GTiff')
# output_raster_ds = driver.Create(output_raster_filtered, reference_cols, reference_rows, 1, gdal.GDT_Byte)
# output_raster_ds.SetProjection(reference_srs)
# output_raster_ds.SetGeoTransform(reference_transform)

# band = output_raster_ds.GetRasterBand(1)
# band.SetNoDataValue(0)

# gdal.RasterizeLayer(output_raster_ds, [1], vector_ds.GetLayer(), burn_values=[1])

# # 5. 对栅格求骨架线
# value = output_raster_ds.GetRasterBand(1).ReadAsArray()
# sk = morphology.skeletonize(value)

# output_skeleton_ds = driver.Create(output_raster_filtered_skeleton, reference_cols, reference_rows, 1, gdal.GDT_Byte)
# output_skeleton_ds.SetProjection(reference_srs)
# output_skeleton_ds.SetGeoTransform(reference_transform)

# band = output_skeleton_ds.GetRasterBand(1)
# band.WriteArray(sk)
# band.SetNoDataValue(0)

# output_skeleton_ds = None
# output_raster_ds = None

# plt.imshow(sk, cmap="gray")


# def side_of_line(point, line):
#     u = np.array(line.coords[1]) - np.array(line.coords[0])
#     v = np.array(point.coords[0]) - np.array(line.coords[0])
#     # True=left, False=right
#     return u[0] * v[1] - u[1] * v[0] > 0


# def cut_polygon(geom, interval):
#     """
#     Cut OBB rectangle into grids
#     """
#     obb = geom.minimum_rotated_rectangle.exterior.coords
#     p1, p2, p3, p4 = Point(obb[0]), Point(obb[1]), Point(obb[2]), Point(obb[3])
#     dist1, dist2 = p1.distance(p2), p2.distance(p3)

#     if dist1 > dist2:
#         long_edge_1 = LineString([p1, p2])
#         long_edge_2 = LineString([p4, p3])
#         num = int(round(dist1 / interval) + int(dist1 * 2 < interval))
#     else:
#         long_edge_1 = LineString([p2, p3])
#         long_edge_2 = LineString([p1, p4])
#         num = int(round(dist2 / interval) + int(dist2 * 2 < interval))
#     # p1 will always on rhe left side

#     cut_geoms = []
#     geom_to_cut = geom
#     dont_cut = False
#     for i in range(1, num):
#         pointA = long_edge_1.interpolate(i / num, normalized=True)
#         pointB = long_edge_2.interpolate(i / num, normalized=True)
#         curr_line = LineString([pointA, pointB])

#         split = list(ops.split(geom_to_cut, curr_line).geoms)
#         if len(split) != 2:
#             dont_cut = True
#             break

#         geom_split_1, geom_split_2 = split

#         at_left = side_of_line(geom_split_1.centroid, curr_line)
#         if at_left:
#             cut_geoms.append(geom_split_1)
#             geom_to_cut = geom_split_2
#         else:
#             cut_geoms.append(geom_split_2)
#             geom_to_cut = geom_split_1

#     cut_geoms.append(geom_to_cut)
#     if dont_cut:
#         return gpd.GeoSeries([])
#     else:
#         return gpd.GeoSeries(cut_geoms)


# interval = 0.62  # 1 meter
# l = [cut_polygon(geom, interval) for geom in gdf]
# result = gpd.GeoSeries(pd.concat(l))
# result.to_file(output_vector_cut)