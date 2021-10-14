import cv2
import sys
import numpy as np
sys.path.append('.')
from osgeo import gdal
from image_process.segment import get_contour_areas
from PIL import Image
import matplotlib.pyplot as plt

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
    for height in range(y2-y1):
        temp = []
        for width in range(x2-x1):
            if np.all(greens[height][width]!=0):
                height_val = dem_area[height][width]-dtm_area[height][width]
                if height_val > 1:
                    temp.append(dem_area[height][width]-dtm_area[height][width])
                else:
                    temp.append(0)
            else:
                temp.append(0)
        area_diff.append(temp)

    return area_diff

def draw_contours(image_array,dem_file,dtm_file,y1,x1,y2,x2):
    # get green colors here
    greens = get_trees(image_array,y1,x1,y2,x2)
    area = process_area(dem_file,dtm_file,y1,x1,y2,x2,greens)
    area = np.array(area,np.uint8)
    formatted = (area * 255 / np.max(area)).astype('uint8')
    img = Image.fromarray(formatted)
    image = np.array(img)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    image_pixel_count = image.shape[0]*image.shape[1]
    # sorted_contours= sorted(contours, key=cv2.contourArea, reverse= True)
    contour_list = get_contour_areas(contours,image_pixel_count)
    # image = cv2.drawContours(image, get_contour_areas(contours), -1, (0, 255, 0), 2)
    # print(contour_list)
    image = cv2.drawContours(image,contour_list , -1, (0, 255, 0), 2)
    plt.imshow(image)
    plt.show()
    return len(contour_list)

def get_trees(image_array,y1,x1,y2,x2):
    low_green = np.array([36, 20, 20])
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
    return mask

image_array = cv2.imread('/home/caluckal/Desktop/Github/elevation-infer/good_color.png',cv2.IMREAD_UNCHANGED)
y1,x1,y2,x2 = 11289,12027,11814,12312

draw_contours(image_array,'/home/caluckal/Desktop/Github/elevation-infer/DBCA_DEM.tif','/home/caluckal/Desktop/Github/elevation-infer/DBCA_DTM.tif',y1,x1,y2,x2)

