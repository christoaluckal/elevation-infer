from osgeo import gdal
import numpy as np
import affine
import sys

def getLonLat(affine_transform,x_coord,y_coord):
    lon, lat = affine_transform * (x_coord, y_coord)
    return (lon,lat)


def getXY(affine_transform,lat,lon):
    inverse_transform = ~affine_transform
    x_coord, y_coord = [ round(f) for f in inverse_transform * (lon, lat) ]
    # return (x_coord,y_coord)


def process_dem(affine_transform,x_min,y_min,array):
    lon,lat = getLonLat(affine_transform,y_min,x_min)
    height_val = array[0][0]
    return height_val,x_min,y_min,(lon,lat),x_min+1,y_min+1


def process_model(dem_file,dtm_file,bounding_list):
    loc_data = {}
    demdata = gdal.Open(str(dem_file))
    # dtmdata = gdal.Open(str(dtm_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)
    for x in bounding_list:
        x_min,y_min = int(x[1]),int(x[0])
        dem_area = dem_band.ReadAsArray(x_min,y_min,1,1)
        dem_height,x_loc,y_loc,lat_lon,x_val,y_val = process_dem(dem_affine_transform,x_min,y_min,dem_area)
        loc_data["{},{},{},{}".format(x_min,y_min,x_min+1,y_min+1)] = [lat_lon,dem_height,x_val,y_val]

    return loc_data


