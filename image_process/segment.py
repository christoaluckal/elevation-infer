import cv2
import sys
import matplotlib.pyplot as plt
sys.path.append("../")
import driver_files.dem_point_proc as dr

good_range = (11289,12027,11814,12312)
partial_range = (11243,10689,11747,11220)
multi_range = (13492,5884,14988,8004)
none_range = (13312,8164,13964,8884)
diag_range = (9360,6852,10030,8194)

# og_img = cv2.imread('/home/caluckal/Desktop/Github/elevation-infer/929_offset_ortho.jpg')

# good_img = og_img[good_range[0]:good_range[2],good_range[1]:good_range[3]]
# partial_img = og_img[partial_range[0]:partial_range[2],partial_range[1]:partial_range[3]]
# multi_img = og_img[multi_range[0]:multi_range[2],multi_range[1]:multi_range[3]]
# none_img = og_img[none_range[0]:none_range[2],none_range[1]:none_range[3]]
# diag_img = og_img[diag_range[0]:diag_range[2],diag_range[1]:diag_range[3]]


area = dr.process_area('/home/caluckal/Desktop/Github/elevation-infer/DBCA_DEM.tif','/home/caluckal/Desktop/Github/elevation-infer/DBCA_DTM.tif',13492,5884,14988,8004)
import numpy as np
area = np.array(area)

cv2.imwrite('bin_good.png',area)

from PIL import Image
import numpy as np

formatted = (area * 255 / np.max(area)).astype('uint8')
img = Image.fromarray(formatted)
img.save('bin_good.png')

image = cv2.imread("bin_good.png")

# convert to RGB
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

# create a binary thresholded image
_, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)
# show it
plt.imshow(binary, cmap="gray")
plt.show()

# find the contours from the thresholded image
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# draw all contours


# image = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
sorted_contours= sorted(contours, key=cv2.contourArea, reverse= True)


largest_item= sorted_contours[0]
# print(largest_item)

def get_contour_areas(contours):

    all_areas= []

    for cnt in contours:
        area= cv2.contourArea(cnt)
        if area > 1000:
            all_areas.append(cnt)

    return all_areas


# print(get_contour_areas(contours))
image = cv2.drawContours(image, get_contour_areas(contours), -1, (0, 255, 0), 2)

plt.imshow(image)
plt.show()

# cv2.imshow('a',area)
# cv2.waitKey(0)

# area = dr.process_area('/home/caluckal/Desktop/Github/elevation-infer/DBCA_DEM.tif','/home/caluckal/Desktop/Github/elevation-infer/DBCA_DTM.tif',11243,10689,11747,11220)
# area = np.array(area)

# cv2.imshow('a',area)
# cv2.waitKey(0)

# area = dr.process_area('/home/caluckal/Desktop/Github/elevation-infer/DBCA_DEM.tif','/home/caluckal/Desktop/Github/elevation-infer/DBCA_DTM.tif',13492,5884,14988,8004)
# area = np.array(area)

# cv2.imshow('a',area)
# cv2.waitKey(0)

# area = dr.process_area('/home/caluckal/Desktop/Github/elevation-infer/DBCA_DEM.tif','/home/caluckal/Desktop/Github/elevation-infer/DBCA_DTM.tif',13312,8164,13964,8884)
# area = np.array(area)

# cv2.imshow('a',area)
# cv2.waitKey(0)

# area = dr.process_area('/home/caluckal/Desktop/Github/elevation-infer/DBCA_DEM.tif','/home/caluckal/Desktop/Github/elevation-infer/DBCA_DTM.tif',9360,6852,10030,8194)
# area = np.array(area)

# cv2.imshow('a',area)
# cv2.waitKey(0)
