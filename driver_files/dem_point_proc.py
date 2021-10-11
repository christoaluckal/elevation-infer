from cv2 import threshold
from osgeo import gdal
import numpy as np
import affine
import sys

# This function takes an (X,Y) coordinate with the affine transform matrix and returns latitude and longitude
def get_lon_at(affine_transform,x_coord,y_coord):
    lon, lat = affine_transform * (x_coord,y_coord)
    # print("LAT LON:",lon,lat)
    return lon,lat

# This is the inverse of getLonLat
def get_xy(affine_transform,lat,lon):
    inverse_transform = ~affine_transform
    x_coord, y_coord = [ round(f) for f in inverse_transform * (lon, lat) ]
    # print("GETXT:",x_coord,y_coord,lon,lat)
    return (x_coord,y_coord)

# Returns height,latitude and longtitude of the selected point only
def process_dem_point(affine_transform,x_min,y_min,array):
    lon,lat = get_lon_at(affine_transform,x_min,y_min)
    height_val = array[0][0]
    return height_val,(lon,lat)

# This function process the point along with its neighbouring pixels in each direction and averages the values that lie between 25% and 75%
# This function ONLY computes the average height and not the location where that average exists, so the selected point and the point at which
# the average exists are different
def process_dem_quantile(affine_transform,x_min,y_min,array,threshold):
    lon,lat = get_lon_at(affine_transform,x_min,y_min)
    height_vals = []
    for i in range(2*threshold):
        for j in range(2*threshold):
            height_vals.append(array[i][j])

    import numpy as np
    q1 = np.percentile(height_vals,25)
    q3 = np.percentile(height_vals,75)

    height_vals = np.array(height_vals)
    mask = np.where((height_vals > q1) & (height_vals<q3))
    # height_val = np.average(np.array(height_vals[mask]))
    height_val = np.average(np.array(height_vals[mask]))
    return height_val,(lon,lat)

# Same as DEM, we process dtm to get the terrain height
def process_dtm(dtm_file,x_min,y_min):
    dtmdata = gdal.Open(str(dtm_file))
    dtm_band = dtmdata.GetRasterBand(1)
    dtm_area = dtm_band.ReadAsArray(x_min,y_min,1,1)
    return dtm_area[0][0]

# This function takes the DEM,DTM, point list and the mode of height selection and returns a dictionary with the (X,Y)(X+1,Y+1) as key and (Lat,Lon),Relative height as values
def process_model(dem_file,dtm_file,bounding_list,mode):
    loc_data = {}
    demdata = gdal.Open(str(dem_file))
    # dtmdata = gdal.Open(str(dtm_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)
    for x in bounding_list:
        x_min,y_min = int(x[0]),int(x[1])
        if mode == 'quantile':
            threshold = 50
            dem_area = dem_band.ReadAsArray(x_min-threshold,y_min-threshold,2*threshold,2*threshold)
            dem_height,lat_lon = process_dem_quantile(dem_affine_transform,x_min,y_min,dem_area,threshold)
        else:
            dem_area = dem_band.ReadAsArray(x_min,y_min,1,1) # Band is (X,Y), # GetLonLat is (X,Y)
            dem_height,lat_lon = process_dem_point(dem_affine_transform,x_min,y_min,dem_area)
        dtm_height = process_dtm(dtm_file,x_min,y_min)
        loc_data["{},{},{},{}".format(x_min,y_min,x_min+1,y_min+1)] = [lat_lon,dem_height-dtm_height]

    return loc_data


