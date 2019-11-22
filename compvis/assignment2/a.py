import cv2
import numpy as np

import os
import random
import sys

    
def display_img_opencv_full_size(img_name, img):
# basically copy and pasted from lecture notes, Professor Stewart's code

    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    

if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("hey. enter an image name, then an output name")
        sys.exit()


        
    img_name = sys.argv[1]# getting arguments
    img = cv2.imread(img_name)
    out_name = (sys.argv[2])

    dimy = img.shape[0]
    dimx = img.shape[1]

    smx = 0
    smy = 0
    count = 0
    
    while (dimx >= 20): # find dimensions of new image
        
        smx = smx + dimx
        count = count + 1
        dimx = dimx//2
    
    new_img = np.zeros((dimy,smx,3)) # preallocates image space

    #initializing points
    lt  = 0
    rt  = lt + img.shape[1] 
    top = 0
    bot = img.shape[0]
    mid = img.shape[0]//2
    
    for x in range(count):
        
        new_img[top:bot,lt:rt,:] = img
        print("Copy starts at (" + str(top) + ", " + str(lt) + ") image shape " + str(img.shape))
        
        img = cv2.resize(img, (img.shape[1]//2,img.shape[0]//2))#resize image

        top = mid - (img.shape[0]//2)#half the height added to midpoint
        bot = top + img.shape[0]# whole height added to the top index
        lt  = rt #new left point is the previous right most point
        rt  = lt + img.shape[1] # new right point is the previous rightmost point plus the image length

    print("Final shape " + str(new_img.shape))
    cv2.imwrite(out_name,new_img.astype(np.uint8))
