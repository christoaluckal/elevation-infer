# elevation-infer

This code uses an Orthomosaic Image, Digital Elevation Model and Digital Terrain Model to determine the height of buildings present in the Region of Interest determined by the user.

## Area processing
`python3 driver_files/driver.py <image> <DEM> <DTM>` to execute default<br>
`python3 driver_files/driver.py <image> <DEM> <DTM> custom` to execute with custom parameters<br>
<br>
Steps for area processing:
  1.  The image is loaded and downscaled to 1/16 the size to allow viewing
  2.  A window pops up allowing you to click areas on the downscaled image. Hold down the Left-Click and drag the area for processing. Press `ESC` when you're done
  3.  The code normalizes the point and scales it up to the original image size
  4.  Every ROI is made into a new image upon which Image Processing is applied to remove non-building entities and remove them
  5.  Once that is done, Contour Generation and Detection is done to determine all the buildings present in the small image using contour area as a filtering tool. You can change the values by running another flag 'custom' on the python3 command.
  6.  After building detection, another window pops up with the contour and the contour bounding box overlayed on the small image. The user can select the buildings to be processed
  7.  **Only the region within the contour rectangle** is processed by filtering out points that lie outside of a SD=2 and then values outside percentiles given by the user (Or 25,95 if default values) are filtered out.
  8.  The code then calculates the Height, Latitude and Longitude of the point with the maximum elevation that lies in the filtered region
  9.  It then returns a dictionary with (Top-Left X,Y of ROI),(Bottom-Right X,Y of ROI):\[ Longitude, Latitude, relative height in m\]

## Point Processing
`python3 driver_files/driver_point.py <image> <DEM> <DTM>` to execute <br>
<br>
Steps for point processing:
  1.  The image is loaded and downscaled to 1/16 the size to allow viewing
  2.  A window pops up allowing you to click on the downscaled image. Press `ESC` when you're done
  3.  The code normalizes the point and scales it up to the original image size
  4.  It calculates the Height, Latitude and Longitude of the clicked point using the DEM and computes the terrain height from the DTM
  5.  It then returns a dictionary with (X_coord,Y_coord,X_coord+1,Y_coord+1):\[ Longitude, Latitude, relative height in m\]

### TODO
1. Fine-tune the green hsv mask
2. Try using a tree-detector
3. [x] Make the performance a little better
4. [x] Learn how to use contour

### CAUTION
This code assumes that there is a relatively high overlap between the image and the DEM/DTM pair. Make sure that the coordinates match as there are cases where the size of the DEM/DTM is larger than the image so the clicked coordinates on the image **DO NOT** reflect the points on the DEM/DTM
