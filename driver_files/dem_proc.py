from osgeo import gdal
import numpy as np
import affine
import sys
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import selector
sys.path.append('.')

# This function takes an (X,Y) coordinate with the affine transform matrix and returns latitude and longitude
def get_lon_lat(affine_transform,x_coord,y_coord):
    '''
    This function is responsible for converting the (X,Y) coordinate to a Longitude,Latitude pair

    Params
    affine_transform: An affine transform matrix to determine the Latitude and Longitude of a given pixel coordinate
    x_coord,y_coord: Coordinates whose Longitude and Latitude need to be determined

    Returns
    lon,lat: Longitude and Latitude of the given (X,Y) coordinate
    '''
    lon, lat = affine_transform * (x_coord,y_coord)
    # print("LAT LON:",lon,lat)
    return lon,lat

def process_area(dem_file,dtm_file,y_min,x_min,y_max,x_max,nongreens):
    '''
    This function is responsible for processing the DEM and DTM and create an array where invalid locations are black
    and valid locations have values equal to their relative heights.

    Params
    dem_file: The path to the DEM file
    dtm_file: The path to the DTM file
    y_min,x_min: Top left coordinates of the ROI
    y_max,x_max: Bottom right coordinates of the ROI
    nongreens: Image with trees removed

    Returns
    area_diff: An array where valid locations have valid elevations and invalid locations are 0
    '''

    # Read the DEM file to get the DEM data
    demdata = gdal.Open(str(dem_file))

    # Since the DEM data may have other bands, we take only the height band
    dem_band = demdata.GetRasterBand(1)

    # The DEM band contains the entire DEM region, hence we extract only a specific location using the top-left coordinates and the width and height of the region
    dem_area = dem_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)

    # Delete the unnecessary value
    del dem_band

    # Repeat for DTM
    dtmdata = gdal.Open(str(dtm_file))
    dtm_band = dtmdata.GetRasterBand(1)
    dtm_area = dtm_band.ReadAsArray(x_min,y_min,x_max-x_min,y_max-y_min)
    del dtm_band

    # This is a 2D array that holds the relative height of valid locations and 0 otherwise
    area_diff = []
    for height in range(y_max-y_min):
        row_vals = []
        for width in range(x_max-x_min):
            # The condition is only true when it processes a [0 0 0] aka black pixel value. This is the invalid location
            if ~(nongreens[height][width][0] == 0 and nongreens[height][width][1] == 0 and nongreens[height][width][2] == 0):
                height_val = dem_area[height][width]-dtm_area[height][width]
                if height_val > 1:
                    # We append just the height value therefore this array when converted to image will have only intensity
                    # Meaning this array will become a grayscale image
                    row_vals.append(height_val)
                else:
                    row_vals.append(0)
            else:
                row_vals.append(0)
        area_diff.append(row_vals)
    return area_diff


def reject_outliers(data, m=2):
    '''
    Function to remove values that lie outside the specified standard deviation

    Params
    data: 1D array with values

    Returns
    data: 1D array with invalid values removed
    '''
    return data[abs(data - np.mean(data)) < m * np.std(data)]

# This is the inverse of getLonLat
def get_xy(affine_transform,lat,lon):
    inverse_transform = ~affine_transform
    x_coord, y_coord = [ round(f) for f in inverse_transform * (lon, lat) ]
    # print("GETXT:",x_coord,y_coord,lon,lat)
    return (x_coord,y_coord)


def process_dem_quantile(affine_transform,x_min,y_min,building_region,width,height,min_cutoff_percent,max_cutoff_percent):
    '''
    This function is responsible for processing an array of relative heights are find the optimum point

    Params
    affine_transform: An affine transform matrix to determine the Latitude and Longitude of a given pixel coordinate
    x_min,y_min: Top-left coordinates of the building wrt the original Orthomosaic Image
    building_region: Array with the relative heights of the building only
    width,height: Width and Height of the building bounding box
    min_cutoff_percent: Percentage value below which height values are invalid
    max_cutoff_percent: Percentage value above which height values are invalid

    Returns
    max_height: Maximum height after filtering
    (lon,lat): Longitude and Latitude of the location with max_height
    '''

    # 1D list to store all relative heights
    height_vals = []

    # Since its a python list, we convert it into a Numpy array
    building_region = np.array(building_region)

    for i in range(width):
        for j in range(height):
            # Add all heights in the list
            height_vals.append(building_region[j][i])

    # Remove values lying outside SD=2
    height_vals = reject_outliers(np.array(sorted(height_vals)),2)

    # Values that determine the percentile of heights
    p1 = np.percentile(height_vals,min_cutoff_percent)
    p2 = np.percentile(height_vals,max_cutoff_percent)

    # Mask of values that lie between the specified percentiles
    mask = ((height_vals > p1) & (height_vals<p2))

    # height_vals is reduced in size to only contain valid heights
    height_vals = height_vals[mask]

    # Find the point with the maximum height
    max_height = np.max(height_vals)

    # Get index of the point with the maximum height
    positions = np.where(building_region == max_height)

    # Consider only the first point incase there are multiple
    lon,lat = get_lon_lat(affine_transform,x_min+positions[1][0],y_min+positions[0][0])
    return max_height,(lon,lat)
    
# Same as DEM, we process dtm to get the terrain height
def process_dtm(dtm_file,x_min,y_min):
    dtmdata = gdal.Open(str(dtm_file))
    dtm_band = dtmdata.GetRasterBand(1)
    dtm_area = dtm_band.ReadAsArray(x_min,y_min,1,1)
    return dtm_area[0][0]


def remove_trees(sub_image):
    '''
    This function is responsible for processing the image and remove non-bulding entities such as trees

    Params
    sub_image: Image from which trees must be removed

    Returns
    mask: An Image where the tree pixels are removed
    '''

    # HSV value of the minimum green value
    low_green = np.array([25, 20, 20])

    # HSV value of the maximum green value
    high_green = np.array([100, 255,255])

    # greent_test = np.array([[[197,200,147]]],np.uint8)
    # greent_test = cv2.cvtColor(greent_test,cv2.COLOR_BGR2HSV)

    # Convert image to HSV
    imgHSV = cv2.cvtColor(sub_image, cv2.COLOR_BGR2HSV)

    #cv2.imwrite('image_hsv.jpg',imgHSV)

    # create the Mask
    mask = cv2.inRange(imgHSV, low_green, high_green)

    #cv2.imwrite('init_mask.jpg',mask)

    # invert the mask
    mask = 255-mask

    #cv2.imwrite('invert_mask.jpg',mask)

    # Perform bitwise AND operation on image and mask to get the image without trees
    mask = cv2.bitwise_and(sub_image, sub_image, mask=mask)
    #cv2.imwrite('image_with_mask.jpg',mask)

    return mask


def get_contour_areas(contour_list,total_pixel_count,min_contour_area,max_contour_area):
    '''
    This function is responsible for processing the contour list to determine valid contours

    Params
    contour_list: List of every contour found in the image
    total_pixel_count: Total number of pixels in the image. Metric of comparison
    min_contour_area: Percentage of the area below which contours are invalid
    max_contour_area: Percentage of the area above which contours are invalid

    Returns
    valid_contour_list: List of contours that are filtered and deemed to be valid
    bounding_rectangle_params: A list of list where the inner list is a 1D array having the top-left coordinates of the bounding rectangle and the width and 
    height of each rectangle: (x,y,w,h).
    '''
    valid_contour_list= []
    bounding_rectangle_params = []
    for cnt in contour_list:
        area = cv2.contourArea(cnt)
        if area > total_pixel_count*min_contour_area and area < total_pixel_count*max_contour_area:
            x,y,w,h = cv2.boundingRect(cnt)
            valid_contour_list.append(cnt)
            bounding_rectangle_params.append([x,y,w,h])

    return valid_contour_list,bounding_rectangle_params


def draw_contours(sub_image,dem_file,dtm_file,y_min,x_min,y_max,x_max,min_contour_area,max_contour_area):
    '''
    This function is responsible for processing the image to determine the number of buildings and the relative height of the buildings.

    Params
    sub_image: The small ROI image taken from the user
    dem_file: The path to the DEM file
    dtm_file: The path to the DTM file
    y_min,x_min: Top left coordinates of the ROI
    y_max,x_max: Bottom right coordinates of the ROI
    min_contour_area: Percentage of the area below which contours are invalid
    max_contour_area: Percentage of the area above which contours are invalid

    Returns
    len(contour_list): The number of buildings determined
    contour_bounding_region: A list of list where the inner list is the relative height array of each bounding box region, therefore this list holds
    2D arrays equal to the number of buildings
    bounding_rectangle_params: A list of list where the inner list is a 1D array having the top-left coordinates of the bounding rectangle and the width and 
    height of each rectangle: (x,y,w,h). Therefore bounding_rectangle_params[i] are the parameters of contour_bounding_region[i]
    sub_image_contour: The sub-image with contours and bounding rectangles overlayed
    '''

    # This is an image with invalid locations as black
    nongreens = remove_trees(sub_image)

    # We generate a 2D array with values either as the relative height or 0
    segmented_height_array = process_area(dem_file,dtm_file,y_min,x_min,y_max,x_max,nongreens)

    # Convert array to Numpy array
    segmented_height_array = np.array(segmented_height_array)

    # Normalize the array to hold integer values. We scale it up to 255 to process the array as an integer image
    segmented_height_int_array = (segmented_height_array * 255 / np.max(segmented_height_array)).astype('uint8')

    #cv2.imwrite('formatted.jpg',formatted)
    
    # Make the image into RGB
    segmented_height_int_image = cv2.cvtColor(segmented_height_int_array, cv2.COLOR_BGR2RGB)

    # Save the image to another array before further processing
    image_rgb = cv2.cvtColor(sub_image,cv2.COLOR_BGR2RGB)

    # The contour algorithm works on binarized iamges, we first convert the image to a grayscaled image.
    gray = cv2.cvtColor(segmented_height_int_image, cv2.COLOR_RGB2GRAY)

    #cv2.imwrite('gray_scaled.jpg',gray)

    # Use thresholding to generate a binarized image where every pixel having intensity > 1 are ceiled to 255 or white
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)

    # Detect contours in the binarized image
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Get the total number of pixels in the image as a metric of comparison
    image_pixel_count = segmented_height_int_image.shape[0]*segmented_height_int_image.shape[1]

    # Sort the contours according to their areas
    sorted_contours= sorted(contours, key=cv2.contourArea, reverse= True)

    # Process the contour list to determine the valid contours
    contour_list,bounding_rectangle_params = get_contour_areas(sorted_contours,image_pixel_count,min_contour_area,max_contour_area)

    # Draw contours on the original sub-image
    sub_image_contour = cv2.drawContours(image_rgb,contour_list , -1, (255, 0, 0), 2)

    #cv2.imwrite('bin_contour.jpg',image)

    # Draw the bounding rectangles on the sub-image and save the valid regions to the array
    contour_bounding_region = []
    for rectangle_params in bounding_rectangle_params:
        top_left_X,top_left_y = rectangle_params[0],rectangle_params[1]
        rect_width,rect_height = rectangle_params[2],rectangle_params[3]
        cv2.rectangle(sub_image_contour,(top_left_X,top_left_y),(top_left_X+rect_width,top_left_y+rect_height),(255,0,0),2)
        contour_bounding_region.append(segmented_height_array[top_left_y:top_left_y+rect_height,top_left_X:top_left_X+rect_width])
    # plt.imshow(sub_image_contour)
    # plt.show()
    return len(contour_list),contour_bounding_region,bounding_rectangle_params,sub_image_contour


def process_model(original_ortho,dem_file,dtm_file,bounding_list,min_contour_area,max_contour_area,min_cutoff_percent,max_cutoff_percent):
    '''
    This function takes the DEM,DTM, point list and returns a dictionary with the (X1,Y1)(X2,Y2) of each building as key and (Lat,Lon),Relative height as values
    Params
    original_ortho: Original Orthomosaic Image array
    dem_file: The path to the DEM file
    dtm_file: The path to the DTM file
    bounding_list: List containing the coordinates of each ROI
    y_max,x_max: Bottom right coordinates of the ROI
    min_contour_area: Percentage of the area below which contours are invalid
    max_contour_area: Percentage of the area above which contours are invalid
    min_cutoff_percent: Percentage value below which height values are invalid
    max_cutoff_percent: Percentage value above which height values are invalid

    Returns
    loc_data: A dictionary holding the coordinates of each building as key along with their longitude,latitude and relative height
    '''

    # Convert the input parameters to percentile values
    min_contour_area = float(min_contour_area/100)
    max_contour_area = float(max_contour_area/100)

    # Dictionary to save the value
    loc_data = {}

    # Open the DEM file to get the attributes 
    demdata = gdal.Open(str(dem_file))

    # Retrieve the affine transform matrix
    dem_affine_transform = affine.Affine.from_gdal(*demdata.GetGeoTransform())

    # Iterate through all the ROIs
    for points in bounding_list:

        # Coordinates of the ROI
        x_min,y_min,x_max,y_max = int(points[0]),int(points[1]),int(points[2]),int(points[3])

        # Image of the ROI
        sub_image = original_ortho[y_min:y_max,x_min:x_max]
        #cv2.imwrite('small_image.jpg',sub_image)

        # Get the number of buildings, contour list, bounding rectangles and the image with contour overlay
        contour_count,contour_rectangle_region,points_list,image_rgb = draw_contours(sub_image,dem_file,dtm_file,y_min,x_min,y_max,x_max,min_contour_area,max_contour_area)
        print("There are {} building(s) in the region".format(contour_count))

        # Select the buildings whose elevation needs to be found
        selected_coords = selector.selector(image_rgb)
        for contours_num in range(contour_count):
            for coords in selected_coords:
                x,y,w,h = points_list[contours_num]
                # If the clicked building lies inside a bounding rectangle then process the building region
                if coords[0] > x and coords[0] < x+w and coords[1] > y and coords[1] < y+h:
                    dem_height,lon_lat = process_dem_quantile(dem_affine_transform,x_min+x,y_min+y,contour_rectangle_region[contours_num],w,h,min_cutoff_percent,max_cutoff_percent)
                    loc_data["{},{},{},{}".format(x_min+x,y_min+y,x_min+w,y_min+h)] = [lon_lat,dem_height]

    return loc_data


