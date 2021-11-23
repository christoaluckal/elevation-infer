'''
When this code runs, it checks for the input files. If the files are present then it asks the user to drag and select the regions 
where processing needs to take place. Once all the regions are marked, press ESC and the code will run. Once processing is done another window
is displayed to the user. This window shows the buildings present. The user then clicks on the buildings whose heights need to be determined and
then press ESC. The output of the code shows a dictionary with the coordinates of buildings as keys and the Lat-Lon and relative height of the buildings present
'''
import cv2
from matplotlib.pyplot import contour
import dem_proc,dem_proc_inverse
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
    try:
        contour_flag = args[3]
        if contour_flag == "custom":
            min_contour_area = float(input('Enter the min. contour area percentage:'))
            max_contour_area = float(input('Enter the max. contour area percentage:'))
            min_cutoff_percent = float(input('Enter the min quantile cutoff:'))
            max_cutoff_percent = float(input('Enter the max. quantile cutoff:'))
        else:
            raise Exception
    except:
        print("Keeping default")
        min_contour_area = 0.6
        max_contour_area = 95
        min_cutoff_percent = 25
        max_cutoff_percent = 95
        

original_ortho_array = cv2.imread(ortho_file)
ortho_shape = original_ortho_array.shape

# We downscale the original image to be able to show it in a window. This leads to a ~5% error in pixel calculations
downscaled_ortho = cv2.resize(original_ortho_array,(ortho_shape[1]//16,ortho_shape[0]//16))

# Dummy image array for saving purposes
dummy_img = original_ortho_array

# Pixel location variables
ix = -1
iy = -1
fx = -1
fy = -1

# Pixel location storage
box_list = []


ix = -1
iy = -1
fx = -1
fy = -1
drawing = False

box_list = []
loc_data = {}

# def write_on_image(image,loc_data):
#     for points,vals in loc_data.items():
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         cv2.putText(image, str(vals[-1]), ((ix+fx)//2,(iy+fy)//2), font, 3, (0, 255, 0), 2, cv2.LINE_AA)
#         # print(ix,iy,fx,fy,(vals[-3],vals[-2]))
#         cv2.circle(image, (vals[-3],vals[-2]), 10, (255,0,0),thickness=-1)
#     cv2.imwrite("DBCA_marked.jpg",image)


# Since we need a precise location on the downscaled image, we normalize the pixel location using the downscaled resolution
def normalizebb(box_list_val,shape):
    '''
    Function to normalize the coordinates

    Params
    box_list_val: 2D array with each element having the top-left and bottom-right coordinates of the downscaled ROI
    shape: The value bounds that will be used for normalization

    Returns
    norm_box_list: 2D array with each element being normalized
    '''
    norm_box_list = []
    for x in box_list_val:
        # print(x,shape)
        norm_box_list.append((x[0]/shape[1],x[1]/shape[0],x[2]/shape[1],x[3]/shape[0]))
    
    return norm_box_list

# When we process the DEM we need the actual pixel locations and not the downscaled one. So we reverse the normalization using the original image resolution
def reversenomarlize(box_list_val,shape):
    '''
    Function to upscale the coordinates to match the original Orthomosaic resolution

    Params
    box_list_val: 2D array with each element having the top-left and bottom-right coordinates of the downscaled ROI
    shape: The resolution to which the values need to be upscaled

    Returns
    upscaled_box_list: 2D array with each element having the top-left and bottom-right coordinates of the upscaled ROI
    '''
    upscaled_box_list = []
    for x in box_list_val:
        # print(x,shape)
        x1 = int(x[0]*shape[1])
        y1 = int(x[1]*shape[0])
        x2 = int(x[2]*shape[1])
        y2 = int(x[3]*shape[0])
        upscaled_box_list.append((x1,y1,x2,y2))
    
    return upscaled_box_list

'''
This function is called which lets the user define the ROI for further processing. Simply click the top-left of the ROI and then hold and drag
the mouse to the bottom-right of the ROI.
'''
def draw_rectangle_with_drag(event, x, y, flags, param):
      
    global ix, iy, drawing, downscaled_ortho,fx,fy
      
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y            

    elif event == cv2.EVENT_MOUSEMOVE:
        fx = x
        fy = y

    elif event == cv2.EVENT_MOUSEWHEEL:
        pass

    elif event == cv2.EVENT_MBUTTONDOWN:
        pass
            
    else:
        cv2.line(downscaled_ortho, pt1 =(ix, iy),
                          pt2 =(ix, fy),
                          color =(0, 255, 255),
                          thickness =1)
        cv2.line(downscaled_ortho, pt1 =(ix, iy),
                          pt2 =(fx, iy),
                          color =(0, 255, 255),
                          thickness =1)
        cv2.line(downscaled_ortho, pt1 =(ix, fy),
                          pt2 =(fx, fy),
                          color =(0, 255, 255),
                          thickness =1)
        cv2.line(downscaled_ortho, pt1 =(fx, iy),
                          pt2 =(fx, fy),
                          color =(0, 255, 255),
                          thickness =1)

        box_list.append((ix,iy,fx,fy))

          
cv2.namedWindow(winname = "Downscaled Orthomosaic")
cv2.setMouseCallback("Downscaled Orthomosaic", 
                     draw_rectangle_with_drag)
# coords = open('coords_new.txt','a')
while True:
    cv2.imshow("Downscaled Orthomosaic", downscaled_ortho)
    
    if cv2.waitKey(10) == 27:
        normalized = normalizebb(box_list,downscaled_ortho.shape)
        upscaled_coords = reversenomarlize(normalized,original_ortho_array.shape)
        loc_data = dem_proc_inverse.process_model(original_ortho_array,dem_file,dtm_file,upscaled_coords,min_contour_area,max_contour_area,min_cutoff_percent,max_cutoff_percent)
        print("\nElevations are\n")
        for x,y in loc_data.items():
            print('Coords:',x,'| Value:',y)
        break
  
cv2.destroyAllWindows()