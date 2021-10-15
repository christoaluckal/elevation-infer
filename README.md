# elevation-infer

`python3 driver_files/driver_point.py <image> <DEM> <DTM>` to execute <br>
<br>
Steps:
  1.  The image is loaded and downscaled to 1/16 the size to allow viewing
  2.  A window pops up allowing you to click on the downscaled image. Press `ESC` when you're done
  3.  The code normalizes the point and scales it up to the original image size
  4.  It calculates the Height, Latitude and Longitude of the clicked point using the DEM and computes the terrain height from the DTM
  5.  It then returns a dictionary with (X_coord,Y_coord,X_coord+1,Y_coord+1):\[ Longitude, Latitude, relative height in m\]

### TODO
1. Fine-tune the green hsv mask
2. Try using a tree-detector
3. Make the performance a little better
4. [x] Learn how to use contour

### CAUTION
This code assumes that there is a relatively high overlap between the image and the DEM/DTM pair. Make sure that the coordinates match as there are cases where the size of the DEM/DTM is larger than the image so the clicked coordinates on the image **DO NOT** reflect the points on the DEM/DTM
