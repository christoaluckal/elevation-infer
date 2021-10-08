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
    print("LONLAT:",lon,lat,x_min,y_min)
    print(array)
    height_val = array[0][0]
    print(height_val)
    return height_val,x_min,y_min,(lon,lat),x_min+1,y_min+1

# def process_dtm(dtm_affine_transform,x_val,y_val,array,lat,lon):
#     getXY(dtm_affine_transform,lat,lon)
#     print(x_val,y_val)
#     height_val = array[x_val][y_val]
#     return height_val


def process_model(dem_file,dtm_file,bounding_list):
    print("PM:",bounding_list)
    loc_data = {}
    demdata = gdal.Open(str(dem_file))
    # dtmdata = gdal.Open(str(dtm_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)
    # dtm_affine_transform = affine.Affine.from_gdal(*dtmdata.GetGeoTransform())
    # dtm_band = dtmdata.GetRasterBand(1)
    # bounding_file = bounding_file # File with the bounding box list as (ymin,xmin,ymax,xmax) 
    for x in bounding_list:
        x_min,y_min = int(x[1]),int(x[0])
        dem_area = dem_band.ReadAsArray(x_min,y_min,1,1)
        dem_height,x_loc,y_loc,lat_lon,x_val,y_val = process_dem(dem_affine_transform,x_min,y_min,dem_area)
        # dtm_area = dtm_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)
        # dtm_height = process_dtm(dtm_affine_transform,x_loc,y_loc,dtm_area,lat_lon[1],lat_lon[0])
        # print([lat_lon,dem_height,dtm_height,x_val,y_val,dem_height-dtm_height])
        loc_data["{},{},{},{}".format(x_min,y_min,x_min+1,y_min+1)] = [lat_lon,dem_height,x_val,y_val]

    return loc_data


