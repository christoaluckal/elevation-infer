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


def get_contour_areas(contours,tot_pixel):

    all_areas= []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > tot_pixel*0.17 and area < tot_pixel*0.95:
            print(area)
            all_areas.append(cnt)

    return all_areas

def draw_contours(y1,x1,y2,x2):
    area = dr.process_area('/home/caluckal/Desktop/Github/elevation-infer/DBCA_DEM.tif','/home/caluckal/Desktop/Github/elevation-infer/DBCA_DTM.tif',y1,x1,y2,x2)
    import numpy as np
    area = np.array(area)
    from PIL import Image
    import numpy as np

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
    image = cv2.drawContours(image,contour_list , -1, (0, 255, 0), 2)
    print(contour_list)
    plt.imshow(image)
    plt.show()


draw_contours(11289,12027,11814,12312)
# draw_contours(11243,10689,11747,11220)
# draw_contours(13492,5884,14988,8004)
# draw_contours(13312,8164,13964,8884)
# draw_contours(9360,6852,10030,8194)

