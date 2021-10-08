from osgeo import gdal
import numpy as np
import affine
import sys
import cv2

# ortho = cv2.imread("DBCA_Ortho.tif",cv2.IMREAD_UNCHANGED)
# dem = cv2.imread('DBCA_DEM.tif',cv2.IMREAD_UNCHANGED)
dtm = cv2.imread('DBCA_DTM.tif',cv2.IMREAD_UNCHANGED)

# print(ortho.shape)
# print(dem.shape)
print(dtm.shape)


def getLonLat(affine_transform,x_coord,y_coord):

    lon, lat = affine_transform * (y_coord, x_coord)
    print("LAT LON:",lat,lon)
    return (lon,lat)


def getXY(affine_transform,lat,lon):
    inverse_transform = ~affine_transform
    x_coord, y_coord = [ round(f) for f in inverse_transform * (lon, lat) ]
    print("GETXT:",x_coord,y_coord,lat,lon)
    # return (x_coord,y_coord)


def process_dem(affine_transform,x_min,y_min,array):
    index_of_highest = list(np.unravel_index(np.argmax(array, axis=None), array.shape))
    x_highest,y_highest = index_of_highest[0],index_of_highest[1]
    # height = open(bounding_file,'a')
    lat_lon = getLonLat(affine_transform,x_min+x_highest,y_min+y_highest)
    height_val = array[x_highest][y_highest]
    return height_val,x_highest,y_highest,lat_lon,x_min+x_highest,y_min+y_highest

def process_dtm(dtm_affine_transform,x_val,y_val,array,lat,lon):
    getXY(dtm_affine_transform,lat,lon)
    print(x_val,y_val)
    height_val = array[x_val][y_val]
    return height_val

def process_dem_point(affine_transform,x_min,y_min,array):
    lon,lat = getLonLat(affine_transform,x_min,y_min)
    height_val = array[0][0]
    print(height_val,(lon,lat))


def process_model(dem_file):
    demdata = gdal.Open(str(dem_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)

    dem_area = dem_band.ReadAsArray(10463,11925,1,1)
    # solutions = np.argwhere(dem_area == 64.18949)
    # print(solutions)
    # bounding_file = bounding_file # File with the bounding box list as (ymin,xmin,ymax,xmax) 
    process_dem_point(dem_affine_transform,10463,11925,dem_area)

    # dem_area = dem_band.ReadAsArray(10463,11925,1,1)
    # # bounding_file = bounding_file # File with the bounding box list as (ymin,xmin,ymax,xmax) 
    # process_dem_point(dem_affine_transform,11925,10463,dem_area)

    # dem_area = dem_band.ReadAsArray(11925,10463,1,1)
    # # bounding_file = bounding_file # File with the bounding box list as (ymin,xmin,ymax,xmax) 
    # process_dem_point(dem_affine_transform,10463,11925,dem_area)

    # dem_area = dem_band.ReadAsArray(11925,10463,1,1)
    # # bounding_file = bounding_file # File with the bounding box list as (ymin,xmin,ymax,xmax) 
    # process_dem_point(dem_affine_transform,11925,10463,dem_area)



# process_model('DBCA_DEM.tif')

