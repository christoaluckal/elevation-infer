import numpy as np
import cv2

image_map = {} # This data structure is used to store coordinates of each sub-part
# The format of image_map is: for (ij)th part [(y1,x1),(y2,x2)] ie standard image format where (y1,x1) are top left and (y2,x2) are bottom right coordinates

# Calculate the percent of white pixels in the image and reject if over threshold
def sampleImage(img):
    height,width,channels = img.shape
    n_white_pix = np.sum(img == 255)
    n_white_pix = n_white_pix //3
    total_pixels = height*width
    if(n_white_pix/total_pixels > 0.96):
        return False
    else:
        return True

# Since images need to be in a defined standard, we pad the image till it achieves the desired size. default_pad is the desired crop dimensions
def padImage(img,default_pad):
    height,width,channels = img.shape
    # print(height,width)
    aspect_ratio = float(width/height)
    if aspect_ratio > 2.0 or aspect_ratio < 0.5:
        print("Image is not close to standard aspect ratio\n")
        exit()
    else:
        # Calculate the padding pixel number required for height and width
        temp_width = width
        width_pad = 0
        temp_height = height
        height_pad = 0
        if width%default_pad[1] !=0:
            # print("Padding width")
            while(temp_width%default_pad[1]!=0):
                temp_width+=1
                width_pad+=1
        if height%default_pad[0] !=0:
            # print("Padding height")
            while(temp_height%default_pad[0]!=0):
                temp_height+=1
                height_pad+=1

        # print(height_pad,width_pad)
        final_width = width+width_pad
        final_height = height+height_pad
        print("Original Image Resolution to :"+str(height)+"x"+str(width))
        print("Image Padded to :"+str(final_height)+"x"+str(final_width))
        color = (255,255,255)
        result = np.full((final_height,final_width,channels), color, dtype=np.uint8)

        # compute center offset
        # xx = (final_width - width) // 2
        # yy = (final_height - height) // 2

        # copy img image into center of result image
        # result[yy:yy+height, xx:xx+width] = img

        # Bottom-Right Offset
        result[:height,:width] = img
        # save result
        return result
        
# This function reads the image array, number of horizontal and vertical splits and the output directory
def cropImage(img,h_split_num,v_split_num,op):
    white = 0 # Total number of white pixels
    sum_total = 0 # Total number of pixels
    height,width,channel = img.shape
    fin_img_list = [] # Final list that contains the names of the cropped images with a unique row-column identifying number
    # print(height,v_split_num,width,h_split_num)
    # print(height//v_split_num)
    # print(width//h_split_num)
    total = str((height//v_split_num)*(width//h_split_num))
    print("Splitting image into "+total+" parts")
    for i in range(0,height//v_split_num):
        for j in range(0,width//h_split_num):
            # print(i,j)
            x_min,y_min = image_map["_"+str(i)+"_"+str(j)+"_"][0][1],image_map["_"+str(i)+"_"+str(j)+"_"][0][0]
            x_max,y_max = image_map["_"+str(i)+"_"+str(j)+"_"][1][1],image_map["_"+str(i)+"_"+str(j)+"_"][1][0]
            # print([i,j],image_map[(i,j)],x_min,y_min,x_max,y_min) #IMPORTANT  image_map stores into standard image format while XY min/max prints as human readable ie row first then column
            temp_img = img[y_min:y_max,x_min:x_max]
            # Sample the images and reject the mostly empty/white image parts
            if sampleImage(temp_img):
            # print("images/"+str(j)+str(i)+".jpg")
                img_name = op+"_"+str(i)+"_"+str(j)+"_"+".jpg"
                cv2.imwrite(img_name,temp_img)
                fin_img_list.append(img_name)
            else:
                white+=1
                # print("Popping",(i,j))
                image_map.pop("_"+str(i)+"_"+str(j)+"_")
            # print("End") 
            sum_total+=1
    print("Total white percentage:",str((white/sum_total)*100))
    # print(image_map)
    return fin_img_list

# This function reads the padded image and the inputted default size to create an image map which maps the ij th element to the top left and bottom right coordinates
def splitImage(img,default_size,op): # Notice the inversion of notations
    height,width = img.shape[0],img.shape[1]
    v_split_num = default_size[0] # The height of the cropped output
    h_split_num = default_size[1] # The width of the cropped output
    for i in range(0,height//v_split_num): # i is the row iterator ie ith row of a particular column
        for j in range(0,width//h_split_num): # j is the column iterator ie jth row of a particular IMAGE
            # image_map[j,i] = [[j*h_split_num,i*v_split_num],[(j+1)*h_split_num,(i+1)*v_split_num]]
            image_map["_"+str(i)+"_"+str(j)+"_"] = [[i*v_split_num,j*h_split_num],[(i+1)*v_split_num,(j+1)*h_split_num]]
            # print([i,j],image_map[i,j])
        # print(image_map)
    # print(image_map)
    img_name = cropImage(img,h_split_num,v_split_num,op)
    # sampleImage(img)
    return img_name


# Main driver function that takes the image path and output path and splits the image returning the split names, map and size  
def breakImage(img_name,op):
    img = cv2.imread(img_name)
    print("Standard image height and width?")
    default_size = int(input()),int(input())
    if default_size[0] > img.shape[0] or default_size[1] > img.shape[1]:
        print("Cannot break image into smaller parts. Inputted size is bigger than image width or height")
        exit()
    # We pad the image to the desired size so that the output is uniform
    padded_img = padImage(img,default_size)
    # Split the image and retain the coordinates of the split image as a row,col pair
    img_name_list = splitImage(padded_img,default_size,op)
    return img_name_list,image_map,default_size



breakImage('/home/caluckal/Desktop/Github/elevation-infer/color_ortho.jpg','color_ortho')