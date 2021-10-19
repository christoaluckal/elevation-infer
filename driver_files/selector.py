import cv2
box_list_sel = []

def draw_rectangle_with_drag(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        box_list_sel.append((4*x,4*y))
        print("Clicked on {},{}".format(4*x,4*y))

def selector(image_og):
# Pixel location variables
    img_og_shape = image_og.shape
# We downscale the original image to be able to show it in a window. This definitely leads to a ~5% error in pixel calculations
    img_disp = cv2.resize(image_og,(img_og_shape[1]//4,img_og_shape[0]//4))
    # Pixel location storage    
    cv2.namedWindow(winname = "Title of Popup Window")
    cv2.setMouseCallback("Title of Popup Window", 
                        draw_rectangle_with_drag)
    img_disp = cv2.cvtColor(img_disp,cv2.COLOR_BGR2RGB)
    #cv2.imwrite('contour_op_selection.jpg',img_disp)
    while True:
        cv2.imshow("Title of Popup Window", img_disp)
        
        if cv2.waitKey(10) == 27:
            break

    cv2.destroyAllWindows()

    return box_list_sel

