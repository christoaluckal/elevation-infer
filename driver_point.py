import cv2
import dem_point_proc
import tif_to_jpg

img_og = cv2.imread("DBCA_Ortho.tif")

img_og_shape = img_og.shape
print("BIG SHAPE:",img_og_shape)
# cv2.namedWindow("output", cv2.WINDOW_NORMAL)  
img_disp = cv2.resize(img_og,(img_og_shape[0]//16,img_og_shape[1]//16))
# img_disp = cv2.resize(img_og,(img_og_shape[0]//2,img_og_shape[1]//2))
# tif_to_jpg.converttiftojpg("DBCA_Ortho.tif","DBCA.jpg")
# dummy_img = cv2.imread('DBCA.jpg')
# cv2.imshow("output", img_disp)                            # Show image
# cv2.waitKey(0)
# variables
ix = -1
iy = -1
fx = -1
fy = -1
drawing = False

box_list = []

def draw_on_image(image,loc_data):
    for points,vals in loc_data.items():
        # print(points)
        points_vals = points.split(',')
        # print(points_vals)
        ix,iy,fx,fy = int(points_vals[0]),int(points_vals[1]),int(points_vals[2]),int(points_vals[3])
        cv2.line(image, pt1 =(ix, iy),
                          pt2 =(ix, fy),
                          color =(0, 0, 255),
                          thickness =50)
        cv2.line(image, pt1 =(ix, iy),
                          pt2 =(fx, iy),
                          color =(0, 0, 255),
                          thickness =50)
        cv2.line(image, pt1 =(ix, fy),
                          pt2 =(fx, fy),
                          color =(0, 0, 255),
                          thickness =50)
        cv2.line(image, pt1 =(fx, iy),
                          pt2 =(fx, fy),
                          color =(0, 0, 255),
                          thickness =50)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(image, str(vals[-1]), ((ix+fx)//2,(iy+fy)//2), font, 3, (0, 255, 0), 2, cv2.LINE_AA)
        # print(ix,iy,fx,fy,(vals[-3],vals[-2]))
        cv2.circle(image, (vals[-3],vals[-2]), 10, (255,0,0),thickness=-1)
    cv2.imwrite("DBCA_marked.jpg",image)


def normalizebb(box_list_val,shape):
    norm_box_list = []
    print("OG BOXLIST",box_list)
    for x in box_list_val:
        # print(x,shape)
        norm_box_list.append((x[0]/shape[1],x[1]/shape[0]))
    
    print("NORMALIZED BOXLIST",norm_box_list)
    return norm_box_list


def reversenomarlize(box_list_val,shape):
    revnorm_box_list = []

    for x in box_list_val:
        # print(x,shape)
        x1 = int(x[0]*shape[1])
        y1 = int(x[1]*shape[0])
        revnorm_box_list.append((x1,y1))
    
    print("RE-NORMALIZED BOXLIST",revnorm_box_list)
    return revnorm_box_list

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
        loc_data = dem_point_proc.process_model("DBCA_DEM.tif","DBCA_DTM.tif",reversed)
        # draw_on_image(dummy_img,loc_data)
        # for x,y in loc_data.items():
        #     print(x,y)
        break
  
cv2.destroyAllWindows()