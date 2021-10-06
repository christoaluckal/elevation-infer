import cv2
  
  
img_og = cv2.imread("DBCA_Ortho.tif")
# img_og = cv2.imread("kaido.png")

img_og_shape = img_og.shape
# cv2.namedWindow("output", cv2.WINDOW_NORMAL)  
img_disp = cv2.resize(img_og,(img_og_shape[0]//16,img_og_shape[0]//16))
# img_disp = cv2.resize(img_og,(img_og_shape[0]//2,img_og_shape[0]//2))

# cv2.imshow("output", img_disp)                            # Show image
# cv2.waitKey(0)
# variables
ix = -1
iy = -1
fx = -1
fy = -1
drawing = False

box_list = []

def normalizebb(box_list_val,shape):
    norm_box_list = []
    for x in box_list_val:
        norm_box_list.append((x[0]/shape[0],x[1]/shape[1],x[2]/shape[0],x[3]/shape[1]))
    
    return norm_box_list


def reversenomarlize(box_list_val,shape):
    revnorm_box_list = []
    for x in box_list_val:
        x1 = int(x[0]*shape[0])
        y1 = int(x[1]*shape[1])
        x2 = int(x[2]*shape[0])
        y2 = int(x[3]*shape[1])
        revnorm_box_list.append((x1,y1,x2,y2))
    
    return revnorm_box_list

def draw_rectangle_with_drag(event, x, y, flags, param):
      
    global ix, iy, drawing, img_disp,fx,fy
      
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix = x
        iy = y            

    elif event == cv2.EVENT_MOUSEMOVE:
        fx = x
        fy = y
            
    else:
        cv2.line(img_disp, pt1 =(ix, iy),
                          pt2 =(ix, fy),
                          color =(0, 255, 255),
                          thickness =1)
        cv2.line(img_disp, pt1 =(ix, iy),
                          pt2 =(fx, iy),
                          color =(0, 255, 255),
                          thickness =1)
        cv2.line(img_disp, pt1 =(ix, fy),
                          pt2 =(fx, fy),
                          color =(0, 255, 255),
                          thickness =1)
        cv2.line(img_disp, pt1 =(fx, iy),
                          pt2 =(fx, fy),
                          color =(0, 255, 255),
                          thickness =1)

        box_list.append((ix,iy,fx,fy))

          
cv2.namedWindow(winname = "Title of Popup Window")
cv2.setMouseCallback("Title of Popup Window", 
                     draw_rectangle_with_drag)
  
while True:
    cv2.imshow("Title of Popup Window", img_disp)
      
    if cv2.waitKey(10) == 27:
        normalized = normalizebb(box_list,img_disp.shape)
        reversed = reversenomarlize(normalized,img_og.shape)
        with open('bb.txt','w+') as bb:
            for x in reversed:
                string = str(x[1])+'\t'+str(x[0])+'\t'+str(x[3])+'\t'+str(x[2])+'\t'+'\n'
                bb.write(string)
        break
  
cv2.destroyAllWindows()