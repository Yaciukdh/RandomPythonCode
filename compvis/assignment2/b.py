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

def tdd(num): #three decimal display
    a = str((round(num*1000)/1000))
    a =format(num, '.3f')
    return a    

def min_max_axis(x,y ): #finds min and max axis via eigval decomp

    cov = np.cov(x,y,bias=True)    
    val,ei = np.linalg.eig(cov)
    val = np.sqrt(val)
    
    if(val[1]<val[0]):
        print("min axis: (" + tdd(ei[0,1]) + "," + tdd(ei[0,0]) + "), sd " + tdd(val[1]) )
        print("max axis: (" + tdd(ei[1,1]) + "," + tdd(ei[1,0]) + "), sd " + tdd(val[0]) )
        min_axis = np.asarray([ei[0,1], ei[0,0] , val[1], val[0]])
    else:
        print("min axis: (" + tdd(ei[1,1]) + "," + tdd(ei[1,0]) + "), sd " + tdd(val[0]) )
        print("max axis: (" + tdd(ei[0,1]) + "," + tdd(ei[0,0]) + "), sd " + tdd(val[1]) )
        min_axis = np.asarray([ei[1,1], ei[1,0], val[0] , val[1] ])


#    print(min_axis.shape)
    return min_axis
        
if __name__ == "__main__":

    if len(sys.argv) != 4:
        print("hey. enter a .txt, a tau, and an output name")
        sys.exit()


    text_file_name = (sys.argv[1])
    tau = float(sys.argv[2])
    outfig = sys.argv[3]
    
    f = open(text_file_name, "r" )
    
    if f.mode == 'r':
        text =f.read()
    else:
        sys.exit()

        
    text = text.split()
    num_arr = np.asarray(text)
    x = num_arr[0:num_arr.size:2].astype(np.float32)
    y = num_arr[1:num_arr.size:2].astype(np.float32)

    # numpy functions to get elements
    mini_x = np.min(x)
    mini_y = np.min(y)
    max_x  = np.max(x)
    max_y  = np.max(y)
    ave_x  = np.mean(x)
    ave_y  = np.mean(y)
    

    print("min: (" + (tdd(mini_x)) + "," + tdd(mini_y) + ")")
    print("max: (" + (tdd(max_x)) + "," + tdd(max_y) + ")")
    print("com: (" + (tdd(ave_x)) + "," + tdd(ave_y) + ")")
    

    min_axis = min_max_axis(x,y)# gets axis and std

    a = min_axis[0]
    b = min_axis[1]
    theta = np.arccos(a)
    ux = np.sum(x)/x.size
    uy = np.sum(y)/y.size 
    rho = ux*np.cos(theta)+uy*np.sin(theta) #finds rho via method described in notes
    
    
    print("closest point: rho " + tdd(rho) + ", theta " + tdd(theta) )
    print("implicit: a " + tdd(a) + ", b " + tdd(b) + ", c " + tdd(-rho))
    
    if min_axis[2] < (min_axis[3]*tau):
        print("best as line")
        
    else:
        print("best as ellipse")

