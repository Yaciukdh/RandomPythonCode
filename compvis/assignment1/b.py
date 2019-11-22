import cv2
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
import matplotlib
import time as tm
from math import ceil

import os
import random
import sys



def display_img_opencv_full_size(img_name, img):
    """
    We can display images directly through OpenCV.  You will notice
    that this generates a huge window.
    """
    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def tdd(num): #three decimal display
    a = str((round(num*1000)/1000))
    a =format(num, '.3f')
    return a
    
def excellent_shading(img, shader, name):
         
        img_a = img[:,:,0]*shader
        img_b = img[:,:,1]*shader
        img_c = img[:,:,2]*shader
        
        img_f = np.concatenate((img_a[...,np.newaxis],img_b[...,np.newaxis],img_c[...,np.newaxis]),axis = 2)
        img_f = np.swapaxes(img_f,0,1)
#        display_img_opencv_full_size(img_name, img_f.astype(np.uint8))
        
        xdim = img_f.shape[0]
        ydim = img_f.shape[1]
        cv2.imwrite(name,img_f.astype(np.uint8))


#        img_f = np.swapaxes(img_f,0,1)

        shader = np.swapaxes(shader,0,1)

        print("(0,0)) " +tdd(shader[0,0]))
        print("(0," + str(ydim//2) + ") " + tdd(shader[0,ydim//2]))
        print("(0," + str(ydim-1) + ") " + tdd(shader[xdim-1,ydim-1]))
        print("(" + str(xdim//2) +",0) " + tdd(shader[xdim//2,0]))
        print("(" + str(xdim//2) + "," + str(ydim//2) + ") " + tdd(shader[xdim//2,ydim//2])) # center
        print("(" + str(xdim//2)+","+ str(ydim-1) +") " + tdd(shader[xdim//2,ydim-1]))
        print("(" +str(xdim-1) +",0) "  + tdd(shader[xdim-1,0]))
        print("(" + str(xdim-1) +","+ str(ydim//2) +") " + tdd(shader[xdim-1,ydim//2]))
        print("(" + str(xdim-1) +","+ str(ydim-1) +") " + tdd(shader[xdim-1,ydim-1]))

        


if __name__ == "__main__":

    
    if len(sys.argv) != 4:
        print("hey. enter an image name, a name for the output image, and a direction")
        sys.exit()
    
    img_name = sys.argv[1]
    out_name = sys.argv[2]
    direct = sys.argv[3]
    img = cv2.imread(img_name)
    xaxis = img.shape[0]
    yaxis = img.shape[1]
    img = np.swapaxes(img,0,1)
    
    
    if(direct == 'left'):


        y = np.linspace(0,1,num = yaxis )
        x = np.zeros(xaxis)
        xg,yg = np.meshgrid(x,y)
        excellent_shading(img,yg,out_name)
    
    elif(direct == 'top'):

        x = np.linspace(0,1,num = xaxis )
        y = np.zeros(yaxis)
        xg,yg = np.meshgrid(x,y)
        excellent_shading(img,xg,out_name)

        
    elif(direct == 'right'):

        y = np.linspace(1,0,num = yaxis )
        x = np.zeros(xaxis)
        xg,yg = np.meshgrid(x,y)
        excellent_shading(img,yg,out_name)

    elif(direct == 'bottom'):

        x = np.linspace(1,0,num = xaxis )
        y = np.zeros(yaxis)
        xg,yg = np.meshgrid(x,y)
        excellent_shading(img,xg,out_name)

    elif(direct == 'center'):
        
        y = np.linspace(0,yaxis-1,num = yaxis)
        x = np.linspace(0,xaxis-1,num = xaxis)
        xg,yg = np.meshgrid(x,y)
        xmid = (xaxis)//2
        ymid = (yaxis)//2
        notnorm = np.sqrt(((xg-xmid)*(xg-xmid))+((yg-ymid)*(yg-ymid)))
        norm = notnorm/np.amax(notnorm)
        actual = 1-norm
        excellent_shading(img,actual,out_name)

    else:
        print("why.")
