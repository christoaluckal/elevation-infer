from cv2 import sort
import numpy as np
from osgeo import gdal
import affine
dem_file = 'DBCA_DEM.tif'
dtm_file = 'DBCA_DTM.tif'

def get_lon_at(affine_transform,x_coord,y_coord):
    lon, lat = affine_transform * (x_coord,y_coord)
    # print("LAT LON:",lon,lat)
    return lon,lat


def process_dem_quantile(affine_transform,x_min,y_min,array,threshold_x,threshold_y):
    # start = time()
    # lon,lat = get_lon_at(affine_transform,x_min,y_min) # TODO CHANGE THIS TO GET THE coordinates
    # print(x_min,y_min,threshold_x,threshold_y)
    height_vals = []
    array = np.array(array)
    for i in range(threshold_x):
        for j in range(threshold_y):
            height_vals.append(array[j][i])

    height_vals = sorted(height_vals)
    q1 = np.percentile(height_vals,25)
    q3 = np.percentile(height_vals,75)

    height_vals = np.array(height_vals)

    mask = ((height_vals > q1) & (height_vals<q3))
    # height_val = np.average(np.array(height_vals[mask]))
    height_vals = height_vals[mask]
    height_check = height_vals[len(height_vals)//2]
    positions = np.where(array == height_check)
    print(x_min+positions[0][2],y_min+positions[1][2])
    lon,lat = get_lon_at(affine_transform,x_min+positions[1][2],y_min+positions[0][2]) # TODO CHANGE THIS TO GET THE coordinates
    return height_check,(lon,lat)

loc_data = {}
demdata = gdal.Open(str(dem_file))
# dtmdata = gdal.Open(str(dtm_file))
dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
dem_band = demdata.GetRasterBand(1)
y_min,x_min,y_max,x_max = 9360,6852,10030,8194

dem_area = dem_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)
dem_height,lat_lon = process_dem_quantile(dem_affine_transform,x_min,y_min,dem_area,x_max-x_min,y_max-y_min)

print(dem_height,lat_lon)