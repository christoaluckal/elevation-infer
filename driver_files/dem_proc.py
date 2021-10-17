from matplotlib.pyplot import contour
from osgeo import gdal
import numpy as np
import affine
import sys
import cv2
from time import time
from PIL import Image
import matplotlib.pyplot as plt
sys.path.append('.')
# from image_process.segment import draw_contours
# This function takes an (X,Y) coordinate with the affine transform matrix and returns latitude and longitude
def get_lon_at(affine_transform,x_coord,y_coord):
    lon, lat = affine_transform * (x_coord,y_coord)
    # print("LAT LON:",lon,lat)
    return lon,lat

def process_area(dem_file,dtm_file,y1,x1,y2,x2,greens):
    demdata = gdal.Open(str(dem_file))
    dem_band = demdata.GetRasterBand(1)
    dem_area = dem_band.ReadAsArray(x1,y1,x2-x1,y2-y1)
    del dem_band
    dtmdata = gdal.Open(str(dtm_file))
    dtm_band = dtmdata.GetRasterBand(1)
    dtm_area = dtm_band.ReadAsArray(x1,y1,x2-x1,y2-y1)
    del dtm_band
    area_diff = []
    # counter_x,counter_y = 0,0
    for height in range(y2-y1):
        temp = []
        # counter_x = 0
        for width in range(x2-x1):
            if np.all(greens[height][width]):
                height_val = dem_area[height][width]-dtm_area[height][width]
                if height_val > 1:
                    temp.append(dem_area[height][width]-dtm_area[height][width])
                    # temp.append(1)
                else:
                    temp.append(0)
            else:
                temp.append(0)
            # counter_x+=1
        area_diff.append(temp)
        # print(counter_y,counter_x)
        # counter_y+=1
    return area_diff

def reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) < m * np.std(data)]

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
def process_dem_quantile(affine_transform,x_min,y_min,array,threshold_x,threshold_y,percentile_1,percentile_2):
    # start = time()
    # lon,lat = get_lon_at(affine_transform,x_min,y_min) # TODO CHANGE THIS TO GET THE coordinates
    # print(x_min,y_min,threshold_x,threshold_y)
    height_vals = []
    array = np.array(array)
    for i in range(threshold_x):
        for j in range(threshold_y):
            height_vals.append(array[j][i])

    height_vals = reject_outliers(np.array(sorted(height_vals)),2)
    q1 = np.percentile(height_vals,percentile_1)
    q3 = np.percentile(height_vals,percentile_2)
    # height_vals = np.array(height_vals)

    mask = ((height_vals > q1) & (height_vals<q3))
    height_val = np.average(np.array(height_vals[mask]))
    height_vals = height_vals[mask]
    # height_check = height_vals[len(height_vals)//2]
    height_check = np.max(height_vals)
    positions = np.where(array == height_check)
    # print(q1,q3,height_check,positions)
    # print(positions,x_min+positions[1][0],y_min+positions[0][0])
    lon,lat = get_lon_at(affine_transform,x_min+positions[1][0],y_min+positions[0][0])
    return height_check,(lon,lat),(x_min+positions[1][0],y_min+positions[0][0])
    
# Same as DEM, we process dtm to get the terrain height
def process_dtm(dtm_file,x_min,y_min):
    dtmdata = gdal.Open(str(dtm_file))
    dtm_band = dtmdata.GetRasterBand(1)
    dtm_area = dtm_band.ReadAsArray(x_min,y_min,1,1)
    return dtm_area[0][0]


def get_trees(image_array,y1,x1,y2,x2):
    # start = time()
    low_green = np.array([25, 20, 20])
    high_green = np.array([100, 255,255])
    # greent_test = np.array([[[197,200,147]]],np.uint8)
    # greent_test = cv2.cvtColor(greent_test,cv2.COLOR_BGR2HSV)
    # print(greent_test)
    imgHSV = cv2.cvtColor(image_array, cv2.COLOR_BGR2HSV)
    # create the Mask
    mask = cv2.inRange(imgHSV, low_green, high_green)
    # inverse mask
    mask = 255-mask
    # print(mask)
    mask = cv2.bitwise_and(image_array, image_array, mask=mask)
    # cv2.imshow('a',res)
    # cv2.waitKey(0)
    # end = time()
    # print("GET TREES:",end-start)
    return mask

def get_contour_areas(contours,tot_pixel,contour_1,contour_2):
    # start = time()
    all_areas= []
    points = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # print(len(cnt))
        if area > tot_pixel*contour_1 and area < tot_pixel*contour_2:
            # print(area)
            # epsilon = 0.1*cv2.arcLength(cnt,True)
            # approx = cv2.approxPolyDP(cnt,epsilon,True)
            # print(approx)
            x,y,w,h = cv2.boundingRect(cnt)
            all_areas.append(cnt)
            points.append([x,y,w,h])
    # end = time()
    # print("GET CONTOUR AREA:",end-start)
    return all_areas,points
    # print(len(all_areas))
    # return all_areas


def draw_contours(image_array,dem_file,dtm_file,y1,x1,y2,x2,contour_1,contour_2):
    # start = time()
    # get green colors here
    greens = get_trees(image_array,y1,x1,y2,x2)
    area = process_area(dem_file,dtm_file,y1,x1,y2,x2,greens)
    # print(y1,x1,y2,x2)
    area = np.array(area)

    formatted = (area * 255 / np.max(area)).astype('uint8')
    img = Image.fromarray(formatted)
    image = np.array(img)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    image_pixel_count = image.shape[0]*image.shape[1]
    sorted_contours= sorted(contours, key=cv2.contourArea, reverse= True)
    contour_list,points_list = get_contour_areas(sorted_contours,image_pixel_count,contour_1,contour_2)
    # contour_list = get_contour_areas(sorted_contours,image_pixel_count)
    # image = cv2.drawContours(image, get_contour_areas(contours), -1, (0, 255, 0), 2)
    # print(contour_list)
    # end = time()
    # print("DRAW CONTOURS:",end-start)
    image = cv2.drawContours(image,contour_list , -1, (0, 255, 0), 2)
    areas = []
    for points in points_list:
        cv2.rectangle(image,(points[0],points[1]),(points[0]+points[2],points[1]+points[3]),(0,255,0),2)
        areas.append(area[points[1]:points[1]+points[3],points[0]:points[0]+points[2]])
    plt.imshow(image)
    plt.show()
    return len(contour_list),areas,points_list

# This function takes the DEM,DTM, point list and the mode of height selection and returns a dictionary with the (X,Y)(X+1,Y+1) as key and (Lat,Lon),Relative height as values
def process_model(image_array,dem_file,dtm_file,bounding_list,mode,contour_1,contour_2,percentile_1,percentile_2):
    # start = time()
    contour_1 = float(contour_1/100)
    contour_2 = float(contour_2/100)
    loc_data = {}
    demdata = gdal.Open(str(dem_file))
    # dtmdata = gdal.Open(str(dtm_file))
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())
    dem_band = demdata.GetRasterBand(1)
    for points in bounding_list:
        # print('\n\n\n')
        start1 = time()

        x_min,y_min,x_max,y_max = int(points[0]),int(points[1]),int(points[2]),int(points[3])
        small_img = image_array[y_min:y_max,x_min:x_max]
        contour_length,area,points_list = draw_contours(small_img,dem_file,dtm_file,y_min,x_min,y_max,x_max,contour_1,contour_2)
        print("There are {} buildings".format(contour_length))
        for contours in range(contour_length):
            start2 = time()
            x,y,w,h = points_list[contours]
            if mode == 'quantile':
                # dem_area = dem_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)
                # print(w,h,len(area[contours]),len(area[contours][0]))
                dem_height,lat_lon,positions = process_dem_quantile(dem_affine_transform,x_min+x,y_min+y,area[contours],w,h,percentile_1,percentile_2)
                # x_dtm = int(positions[0])
                # y_dtm = int(positions[1])
            else:
                dem_area = dem_band.ReadAsArray(x_min,y_min,1,1) # Band is (X,Y), # GetLonLat is (X,Y)
                dem_height,lat_lon = process_dem_point(dem_affine_transform,x_min,y_min,dem_area)
            # dtm_height = process_dtm(dtm_file,x_dtm,y_dtm)
            loc_data["{},{},{},{}".format(x_min+x,y_min+y,x_min+w,y_min+h)] = [lat_lon,dem_height]
            end2 = time()
            # print((x_max-x_min)*(y_max-y_min),':{}'.format(end2-start2))
        end1 = time()
        print("{}".format(end1-start1),'\n\n')
    # end = time()
    # print("PROCESS MODEL:",end-start)
    print("ENDED")
    return loc_data


