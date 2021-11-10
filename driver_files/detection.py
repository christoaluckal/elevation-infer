import torch
import os
import cv2
def get_detection(image):
    temp_img = image
    path = os.getcwd()
    print(path)
    model = torch.hub.load('ultralytics/yolov5', 'custom',path+'/detector/weights/best.pt') 
    # predictions = model()
    results = model(temp_img)
    labels, cord = results.xyxyn[0][:, -1].cpu().numpy(), results.xyxyn[0][:, :-1].cpu().numpy()
    height,width,_ = temp_img.shape
    for row in cord:
        x1,y1,x2,y2 = int(row[0]*width),int(row[1]*height),int(row[2]*width),int(row[3]*height)
        cv2.rectangle(temp_img,(x1,y1),(x2,y2),(255,0,0),2)

    cv2.imshow('Test',temp_img)
    return image
