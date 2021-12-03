og_dem = '/home/caluckal/Desktop/Github/elevation-infer/validation/original_DEM.tif'
altered_dem = '/home/caluckal/Desktop/Github/elevation-infer/validation/downscaled_upscaled_DEM.tif'

from osgeo import gdal
import numpy as np
import cv2
from sklearn.preprocessing import normalize

def getdata(path):
    og_height,og_width= cv2.imread(path,-1).shape
    dem_file = gdal.Open(str(path))
    dem_band = dem_file.GetRasterBand(1)
    dem_data = dem_band.ReadAsArray(0,0,og_width,og_height)
    return dem_data,og_height,og_width
    # cv2.imwrite('/home/caluckal/Desktop/Github/elevation-infer/validation/test.png',dem_data)

def getfirstvalid(array,height,width):
    try:
        for x in range(height):
            for y in range(width):
                if array[x][y] == -32767.0:
                    print(array[x][y])
                    raise Exception
    except Exception:
        return (x,y)

og_data,og_height,og_width = getdata(og_dem)
alt_data,alt_height,alt_width = getdata(altered_dem)

# og_data = np.array(og_data)
# alpha = np.array([og_data != -32767]).astype(np.int8)
# alpha = alpha[0]
# print(alpha[1000][1000])
# result = np.dstack((og_data,alpha))

# cv2.imwrite('validation/og.png',og_data)
# cv2.imwrite('validation/alt.png',alt_data)


# norm_b = 32768//16*normalize(og_data,norm='l2',axis=0)
# norm_b = np.array(og_data,dtype=np.int32)


box_list_sel = []

def draw_rectangle_with_drag(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        box_list_sel.append((4*x,4*y))
        print("Clicked on {},{} which is {},{} in original sub-image".format(x,y,4*x,4*y))

def selector(image_og):
    '''
    Function to display the image with contours and select and normalize the clicked coordinates

    Params
    image_og: Image to be displayed

    Returns
    box_list_sel: 2D array with the coordinates (X,Y) of the clicked location
    '''
    # Pixel location variables
    img_og_shape = image_og.shape
    # We downscale the original image to be able to show it in a window. This definitely leads to a ~5% error in pixel calculations
    img_disp = cv2.resize(image_og,(img_og_shape[1]//4,img_og_shape[0]//4))
    # Pixel location storage    
    cv2.namedWindow(winname = "Downscaled Sub-Image")
    cv2.setMouseCallback("Downscaled Sub-Image", 
                        draw_rectangle_with_drag)
    img_disp = cv2.cvtColor(img_disp,cv2.COLOR_BGR2RGB)
    #cv2.imwrite('contour_op_selection.jpg',img_disp)
    while True:
        cv2.imshow("Downscaled Sub-Image", img_disp)
        
        if cv2.waitKey(10) == 27:
            break

    cv2.destroyAllWindows()

    return box_list_sel

# x:8 y:24
# og_img = cv2.imread('validation/og.png')
# alt_img = cv2.imread('validation/alt.png')

# og = og_img.shape
# alt = alt_img.shape


# selector(og_img)
# selector(alt_img)

# x_dash = box_list_sel[1][0]-box_list_sel[0][0]
# y_dash = box_list_sel[1][1]-box_list_sel[0][1]

# dummy = np.zeros((alt[0],alt[1],3))
# print(x_dash,y_dash)

# for y in range(y_dash,og[0]):
#     for x in range(x_dash,og[1]):
#         dummy[y][x] = og_img[y-y_dash][x-x_dash]


# cv2.imwrite('validation/test_new.png',dummy)


dummy = np.zeros((alt_height,alt_width))-32767

for y in range(og_height):
    for x in range(og_width):
        dummy[y+24][x+8] = og_data[y][x]


diff = dummy-alt_data
from sklearn.metrics import mean_squared_error as mse
for x in diff:
    zero = np.zeros((len(x)))
    print(mse(zero,x))

# diff = np.array(255*diff).astype(np.int8)
# mses = ((diff)**2).mean(axis=1)
# cv2.imwrite('validation/proper_testing.jpg',diff)


