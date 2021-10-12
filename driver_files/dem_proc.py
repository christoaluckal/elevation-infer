from osgeo import gdal
import numpy as np
import affine
import sys
sys.path.append('.')
from image_process.segment import draw_contours
# This function takes an (X,Y) coordinate with the affine transform matrix and returns latitude and longitude
def get_lon_at(affine_transform,x_coord,y_coord):
    lon, lat = affine_transform * (x_coord,y_coord)
    # print("LAT LON:",lon,lat)
    return lon,lat

def process_area(dem_file,dtm_file,y1,x1,y2,x2):
    demdata = gdal.Open(str(dem_file))
    dem_band = demdata.GetRasterBand(1)
    dem_area = dem_band.ReadAsArray(x1,y1,x2-x1,y2-y1)
    del dem_band
    dtmdata = gdal.Open(str(dtm_file))
    dtm_band = dtmdata.GetRasterBand(1)
    dtm_area = dtm_band.ReadAsArray(x1,y1,x2-x1,y2-y1)
    del dtm_band

    area_diff = []
    for height in range(y2-y1):
        temp = []
        for width in range(x2-x1):
            height_val = dem_area[height][width]-dtm_area[height][width]
            if height_val > 1:
                temp.append(dem_area[height][width]-dtm_area[height][width])
            else:
                temp.append(0)
        area_diff.append(temp)

    return area_diff

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
def process_dem_quantile(affine_transform,x_min,y_min,array,threshold_x,threshold_y):
    lon,lat = get_lon_at(affine_transform,x_min,y_min) # TODO CHANGE THIS TO GET THE coordinates
    height_vals = []
    for i in range(threshold_x):
        for j in range(threshold_y):
            height_vals.append(array[j][i])

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
        x_min,y_min,x_max,y_max = int(x[0]),int(x[1]),int(x[2]),int(x[3])
        if mode == 'quantile':
            dem_area = dem_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)
            contour_length = draw_contours(dem_file,dtm_file,y_min,x_min,y_max,x_max)
            print("CONTOURS:",contour_length)
            dem_height,lat_lon = process_dem_quantile(dem_affine_transform,x_min,y_min,dem_area,x_max-x_min,y_max-y_min)
        else:
            dem_area = dem_band.ReadAsArray(x_min,y_min,1,1) # Band is (X,Y), # GetLonLat is (X,Y)
            dem_height,lat_lon = process_dem_point(dem_affine_transform,x_min,y_min,dem_area)
        dtm_height = process_dtm(dtm_file,x_min,y_min)
        loc_data["{},{},{},{}".format(x_min,y_min,x_max,y_max)] = [lat_lon,dem_height,dtm_height,x_min,y_min]

    return loc_data


