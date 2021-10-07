import cv2, os

def converttiftojpg(tiff_,jpg_):
    read = cv2.imread(tiff_)
    outfile = tiff_.split('.')[0] + '.jpg'
    cv2.imwrite(jpg_,read,[int(cv2.IMWRITE_JPEG_QUALITY), 200])