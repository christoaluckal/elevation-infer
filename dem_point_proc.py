from osgeo import gdal
import numpy as np
import affine
import sys

def getLonLat(affine_transform,x_coord,y_coord):
    lon, lat = affine_transform * (x_coord,y_coord)
    # print("LAT LON:",lon,lat)
    return lon,lat


def getXY(affine_transform,lat,lon):
    inverse_transform = ~affine_transform
    x_coord, y_coord = [ round(f) for f in inverse_transform * (lon, lat) ]
    print("GETXT:",x_coord,y_coord,lon,lat)
    return (x_coord,y_coord)


def process_dem(affine_transform,x_min,y_min,array):
    lon,lat = getLonLat(affine_transform,x_min,y_min)
    height_val = array[0][0]
    return height_val,(lon,lat)

def process_dtm(dtm_file,x_min,y_min):
    dtmdata = gdal.Open(str(dtm_file))
    dtm_band = dtmdata.GetRasterBand(1)
    dtm_area = dtm_band.ReadAsArray(x_min,y_min,1,1)
    return dtm_area[0][0]

def process_model(dem_file,dtm_file,bounding_list):
    loc_data = {}
    demdata = gdal.Open(str(dem_file))
    # dtmdata = gdal.Open(str(dtm_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)
    for x in bounding_list:
        x_min,y_min = int(x[0]),int(x[1])
        dem_area = dem_band.ReadAsArray(x_min,y_min,1,1) # Band is (X,Y), # GetLonLat is (X,Y)
        dem_height,lat_lon = process_dem(dem_affine_transform,x_min,y_min,dem_area)
        dtm_height = process_dtm(dtm_file,x_min,y_min)
        loc_data["{},{},{},{}".format(x_min,y_min,x_min+1,y_min+1)] = [lat_lon,dem_height-dtm_height]

    return loc_data


