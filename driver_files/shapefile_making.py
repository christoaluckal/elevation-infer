file = open('/home/caluckal/Desktop/Github/elevation-infer/coords_new.txt')
poly = []
full_polys = []
heights = []
for x in file.readlines():
    vals = x[:-2]
    vals = vals.split(' ')
    poly.append([float(vals[0]),float(vals[1])])

import geopandas as gpd
from shapely.geometry import Polygon

lat_point_list = [x[1] for x in poly]
lon_point_list = [x[0] for x in poly]
# print(lat_point_list)
heights.append(56.66)
polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
full_polys.append(polygon_geom)

file = open('/home/caluckal/Desktop/Github/elevation-infer/coords.txt')
poly = []
for x in file.readlines():
    vals = x[:-2]
    vals = vals.split(' ')
    poly.append([float(vals[0]),float(vals[1])])

import geopandas as gpd
from shapely.geometry import Polygon

lat_point_list = [x[1] for x in poly]
lon_point_list = [x[0] for x in poly]
# print(lat_point_list)
heights.append(116.66)
polygon_geom = Polygon(zip(lon_point_list, lat_point_list))
full_polys.append(polygon_geom)

crs = {'init': 'epsg:4326'}
polygon = gpd.GeoDataFrame(crs=crs, geometry=full_polys)
polygon.insert(1,'height',0.0)
polygon['height'] = heights
print(polygon)
polygon.to_file(filename='/home/caluckal/Desktop/Github/elevation-infer/shapefile_testing/writing/polygon_new.shp', driver="ESRI Shapefile")