from osgeo import gdal
import numpy as np
import affine
import sys

def getLonLat(affine_transform,x_coord,y_coord):
    # print("X:{},Y:{}".format(x_coord,y_coord))
    lon, lat = affine_transform * (x_coord, y_coord)
    return (lon,lat)


def getXY(affine_transform,lat,lon):
    inverse_transform = ~affine_transform
    x_coord, y_coord = [ round(f) for f in inverse_transform * (lon, lat) ]
    return (x_coord,y_coord)


def process_dem(affine_transform,x_min,y_min,array):
    index_of_highest = list(np.unravel_index(np.argmax(array, axis=None), array.shape))
    x_highest,y_highest = index_of_highest[0],index_of_highest[1]
    # height = open(bounding_file,'a')
    lat_lon = getLonLat(affine_transform,x_min+x_highest,y_min+y_highest)
    height_val = array[x_highest][y_highest]
    return height_val,x_highest,y_highest,lat_lon,x_min+x_highest,y_min+y_highest

def process_dtm(x_val,y_val,array):
    # height = open(bounding_file,'a')
    height_val = array[x_val][y_val]
    return height_val


def process_model(dem_file,dtm_file,bounding_file,bounding_list):
    loc_data = {}
    demdata = gdal.Open(str(dem_file))
    dtmdata = gdal.Open(str(dtm_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)
    dtm_affine_transform = affine.Affine.from_gdal(*dtmdata.GetGeoTransform())
    dtm_band = dtmdata.GetRasterBand(1)
    # bounding_file = bounding_file # File with the bounding box list as (ymin,xmin,ymax,xmax) 
    coords = open(bounding_file,'a')
    for x in bounding_list:
        li = x
        y_min,x_min,y_max,x_max = int(li[1]),int(li[0]),int(li[3]),int(li[2])
        dem_area = dem_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)
        dem_height,x_loc,y_loc,lat_lon,x_val,y_val = process_dem(dem_affine_transform,x_min,y_min,dem_area)
        dtm_area = dtm_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)
        dtm_height = process_dtm(x_loc,y_loc,dtm_area)
        # print([lat_lon,dem_height,dtm_height,x_val,y_val,dem_height-dtm_height])
        loc_data["{},{},{},{}".format(x_min,y_min,x_max,y_max)] = [lat_lon,dem_height,dtm_height,x_val,y_val,dem_height-dtm_height]

    return loc_data


