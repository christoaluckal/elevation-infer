from osgeo import gdal
import numpy as np
import affine
import sys
import cv2

# ortho = cv2.imread("929_offset_ortho.jpg",cv2.IMREAD_UNCHANGED)
# dem = cv2.imread('DBCA_DEM.tif',cv2.IMREAD_UNCHANGED)
# dtm = cv2.imread('DBCA_DTM.tif',cv2.IMREAD_UNCHANGED)

# print(ortho.shape)
# print(dem.shape)
# print(dtm.shape)

# ORTHO: (21342, 21426, 4)
# DEM: (24220, 22935)
# DTM: (24220, 22935)
# width,height= dem.shape
# cv2.imwrite('new_dem.tif',cv2.resize(dem,(24220//4,22935//4),interpolation = cv2.INTER_AREA))


def getLonLat(affine_transform,x_coord,y_coord):
    lon, lat = affine_transform * (x_coord,y_coord)
    print("LAT LON:",lon,lat)
    return lon,lat


def getXY(affine_transform,lat,lon):
    inverse_transform = ~affine_transform
    x_coord, y_coord = [ round(f) for f in inverse_transform * (lon, lat) ]
    print("GETXT:",x_coord,y_coord,lon,lat)
    # return (x_coord,y_coord)


def process_dem(affine_transform,x_min,y_min,array):
    index_of_highest = list(np.unravel_index(np.argmax(array, axis=None), array.shape))
    x_highest,y_highest = index_of_highest[0],index_of_highest[1]
    # height = open(bounding_file,'a')
    lat_lon = getLonLat(affine_transform,x_min+x_highest,y_min+y_highest)
    height_val = array[y_highest][x_highest]
    return height_val,x_highest,y_highest,lat_lon,x_min+x_highest,y_min+y_highest


def process_dem_point(affine_transform,y_min,x_min,array):
    # lon,lat = getLonLat(affine_transform,x_min,y_min)
    # print("PM:",lon,lat)
    height_val = array[0][0]
    # print(height_val,(lon,lat))
    return height_val

# 8973,930

def process_model(dem_file):
    demdata = gdal.Open(str(dem_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)
    x_coord,y_coord = 3456,13115
    dem_area = dem_band.ReadAsArray(x_coord,y_coord,1,1) #(startx,starty,endx,endy)
    print(process_dem_point(dem_affine_transform,y_coord,x_coord,dem_area))
    clon,clat = getLonLat(dem_affine_transform,x_coord,y_coord)

process_model('DBCA_DEM.tif')

