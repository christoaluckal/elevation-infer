import cv2
import dem_point_proc
import sys

# Invocation is python3 driver_point.py <JPG for clicking> <DEM file> <DTM file>
args = sys.argv[1:]

if len(args) < 3:
    print("Missing files")
    exit()
else:
    ortho_file = args[0]
    dem_file = args[1]
    dtm_file = args[2]

img_og = cv2.imread(ortho_file)
img_og_shape = img_og.shape

# We downscale the original image to be able to show it in a window. This definitely leads to a ~5% error in pixel calculations
img_disp = cv2.resize(img_og,(img_og_shape[0]//16,img_og_shape[1]//16))

# Dummy image array for saving purposes
dummy_img = img_og

# Pixel location variables
ix = -1
iy = -1
fx = -1
fy = -1

# Pixel location storage
box_list = []

# Function to draw a circle at the selected pixel locaion along with the computed height
def draw_point_on_image(image,loc_data,method):
    for points,vals in loc_data.items():
        # print(points)
        points_vals = points.split(',')
        # print(points_vals)
        ix,iy,fx,fy = int(points_vals[0]),int(points_vals[1]),int(points_vals[2]),int(points_vals[3])
        font = cv2.FONT_HERSHEY_SIMPLEX
        if method!='default':
            cv2.putText(image, "Quantile:"+str(vals[-1]), (ix+100,iy+100), font, 3, (0, 0, 255), 2, cv2.LINE_AA)
            # print(ix,iy,fx,fy,(vals[-3],vals[-2]))
            cv2.circle(image, (ix,iy), 10, (0, 0, 255),thickness=-1)
        else:
            cv2.putText(image, "Default:"+str(vals[-1]), (ix+100,iy+100), font, 3, (255, 0, 0), 2, cv2.LINE_AA)
            # print(ix,iy,fx,fy,(vals[-3],vals[-2]))
            cv2.circle(image, (ix,iy), 10, (255, 0, 0),thickness=-1)           

# Since we need a precise location on the downscaled image, we normalize the pixel location using the downscaled resolution
def normalizebb(box_list_val,shape):
    norm_box_list = []
    for x in box_list_val:
        # print(x,shape)
        norm_box_list.append((x[0]/shape[1],x[1]/shape[0]))
    
    return norm_box_list

# When we process the DEM we need the actual pixel locations and not the downscaled one. So we reverse the normalization using the original image resolution
def reversenomarlize(box_list_val,shape):
    revnorm_box_list = []
    for x in box_list_val:
        # print(x,shape)
        x1 = int(x[0]*shape[1])
        y1 = int(x[1]*shape[0])
        revnorm_box_list.append((x1,y1))
    
    return revnorm_box_list

# Function to capture point click
def point_on_image(event,x,y,flags,param):
    global ix,iy,box_list
    if event == cv2.EVENT_LBUTTONDOWN:
        ix = x
        iy = y
        box_list.append((ix,iy))
          
cv2.namedWindow(winname = "Title of Popup Window")
# cv2.setMouseCallback("Title of Popup Window", 
#                      draw_rectangle_with_drag)
cv2.setMouseCallback("Title of Popup Window", point_on_image)
  
while True:
    cv2.imshow("Title of Popup Window", img_disp)
    if cv2.waitKey(10) == 27:
        normalized = normalizebb(box_list,img_disp.shape)
        reversed = reversenomarlize(normalized,img_og.shape)


        print("DEFAULT")
        loc_data = dem_point_proc.process_model(dem_file,dtm_file,reversed,'default')
        for x,y in loc_data.items():
            print(x,y)
        # draw_point_on_image(dummy_img,loc_data,'default')


        print("\n\nQUANTILE")
        loc_data = dem_point_proc.process_model(dem_file,dtm_file,reversed,'quantile')
        for x,y in loc_data.items():
            print(x,y)
        # draw_point_on_image(dummy_img,loc_data,'quantile')


        # cv2.imwrite("DBCA_marked.jpg",dummy_img)
        break
  
cv2.destroyAllWindows()