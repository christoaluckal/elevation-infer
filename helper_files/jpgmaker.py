import cv2
import numpy as np

# 21342 21426 24220 22935

# dem_file = cv2.imread('DBCA_DEM.tif',cv2.IMREAD_UNCHANGED)
# dem_h,dem_w = dem_file.shape
# # 929,8973, (h,w)
# x = 0
# y=0
# try:
#     for height_val in range(dem_h):
#         for width_val in range(dem_w):
#             if dem_file[height_val][width_val] != -32767:
#                 raise Exception
# except Exception as e:
#     print(height_val,width_val)
#     pass

# del dem_file

ortho_file = cv2.imread('DBCA_Ortho.tif',cv2.IMREAD_UNCHANGED)
ortho_h,ortho_w,_ = ortho_file.shape
# 0 8973
# print(type(ortho_file[2277][13068]))
# try:
#     for height_val in range(ortho_h):
#         for width_val in range(ortho_w):
#             if ortho_file[height_val][width_val][0] != 0 and ortho_file[height_val][width_val][1] != 0 and ortho_file[height_val][width_val][2] != 0 and ortho_file[height_val][width_val][3] != 0:
#                 raise Exception
# except Exception as e:
#     print(height_val,width_val)
#     pass

blank_image = np.zeros((24220,22935,4), np.uint8)
print(ortho_file[12000][12000])
for x in range(ortho_h):
    for y in range(ortho_w):
        # print(ortho_file[x],ortho_file[x][y],ortho_file[x][y][0])
        blank_image[929+x][y] = ortho_file[x][y]

del ortho_file

cv2.imwrite('color_ortho.jpg',blank_image)

# print(ortho_h,ortho_w,dem_h,dem_w)