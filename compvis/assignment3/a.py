import cv2
import numpy as np

import os
import random
import sys
import math


def odd(num): #one decimal display
    a = str((round(num*1000)/1000))
    a = format(num, '.1f')
    return a    


def tdd(num): #two decimal display
    a = format(num, '.2f')
    return a    

def print_M(M):
    print("Matrix M:")
    shape = M.shape
#    print(shape)
#    print(M)
    for x in range(shape[0]):
        print(tdd(M[x,0])+", "+tdd(M[x,1])+", "+tdd(M[x,2])+", "+tdd(M[x,3]))
    
    
def make_vec_string(ind, vec, result, in_or_out):
#    print(vec)
    string = (str(ind) + ": " + odd(vec[0]) + " " + odd(vec[1]) + " " + odd(vec[2]) + " => " + odd(result[0]) + " " + odd(result[1]) + " " + in_or_out)
    print(string)
    
    
    
def display_img_opencv_full_size(img_name, img): # display pic from notes

    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def deg_to_rad(deg): # degrees to radians for angles
    
    rad = (3.14159265*deg)/180
#    print(rad)
    return rad
    
    
def check_arr(): # used for testing
    var_arr = ['rx', 'ry' , 'rz' , 'tx', 'ty', 'tz', 'f', 'd', 'ic', 'jc']
    print(var_arr)
    
    
    
def convert_microns_to_mm(micron): # converts microns to millimeter
    mm = micron/1000
    return mm
    
    
    
def construct_R(rx,ry,rz): # creates the rotation matrix

    Rx=np.asarray([[1,0,0],[0,np.cos(rx),-np.sin(rx)],[0,np.sin(rx),np.cos(rx)]])
    Ry=np.asarray([[np.cos(ry),0,np.sin(ry)],[0,1,0],[-np.sin(ry),0,np.cos(ry)]])
    Rz=np.asarray([[np.cos(rz),-np.sin(rz),0],[np.sin(rz),np.cos(rz),0],[0,0,1]])
    Rxy  = np.matmul(Rx,Ry)
    Rxyz = np.matmul(Rxy,Rz)
    
#    print(Rxyz)
#    print(np.linalg.det(Rxyz)) # sanity check
    
    return Rxyz

def construct_t(tx,ty,tz): # creates translation vector
    t_vec = np.asarray([tx,ty,tz])
    return t_vec


def construct_Rt(R,t): # creates the concatenated R and t with appropriate operations
    
    r_temp = R.T
    new_t = np.matmul(r_temp,t)
    R_t =  np.column_stack((R.T,new_t))
    
    return R_t
   



def parse_text(text): # gets text into thier appropriate variables and types
    
    split_text = text.split()
#    print(split_text)
    
    # Rotation vector
    rx = deg_to_rad(float(split_text[0]))
    ry = deg_to_rad(float(split_text[1]))
    rz = deg_to_rad(float(split_text[2]))
    # Translation vector (milli)
    tx = float(split_text[3])
    ty = float(split_text[4])
    tz = float(split_text[5])
    # Focal length in millimeters
    f  = float(split_text[6])
    # Micron per pixel
    d  = float(split_text[7])
    # the optical axis pierces the image plane in row ic, column jc
    ic = int(split_text[8])
    jc = int(split_text[9])
    
    return rx, ry, rz, tx, ty, tz, f, d, ic, jc
    
    
def parse_points(point): # gets points into proper form
    
    points = point.split()
    num_arr = np.asarray(points)
    x = num_arr[0:num_arr.size:3].astype(np.float32)
    y = num_arr[1:num_arr.size:3].astype(np.float32)
    z = num_arr[2:num_arr.size:3].astype(np.float32)

    return x,y,z


def construct_points(x,y,z): # creates the points array
    
    points = np.asarray([x,y,z])
#    print(points.shape)
#    print(points)
    return points

def construct_K(f,d,ic,jc): # creates the K matrix
    
    dm = convert_microns_to_mm(d)
    sx = f/dm
    sy = f/dm
    
    K = np.asarray([[sx,0,ic],[0,sy,jc],[0,0,1]])
    return K

def compute_in_out(M,points_arr,y): # figure out projections, if they are in or out of image, if they are hidden, etc.
    
    proj      = np.zeros((len(y),3))
    vector    = np.zeros((len(y),4))
    in_or_out = []
    inside    = []
    outside   = []
    
    
    for yy in range(len(y)):
        vec = np.asarray([[float(points_arr[0,yy])],[float(points_arr[1,yy])],[float(points_arr[2,yy])],[float(1)]])
        vector[yy,0] = vec[0]
        vector[yy,1] = vec[1]
        vector[yy,2] = vec[2]
        vector[yy,3] = vec[3]

        result = np.matmul(M,vector[yy,:])
        proj[yy,1] = result[0]/result[2]
        proj[yy,0] = result[1]/result[2]
        proj[yy,2] = result[2]
        
    for z in range(len(y)):
#        print(proj[z])
        if (0 < proj[z,0]) and (proj[z,0] < 4000) and (0 < proj[z,1]) and (proj[z,1] < 6000 ):
            in_or_out.append("inside")               
        else:
            in_or_out.append("outside")
            
    test = np.zeros(4)
    test[3] = 1
    test[2] = 1
    cam = np.matmul(M,test)
#    print("cam")
#    print(cam)
    for z in range(len(y)):
        if(0<proj[z,2]):
            inside.append(z)
        else:
            outside.append(z)
    print("Projections:")        
    for x in range(len(y)):   
        make_vec_string(x,vector[x,:],proj[x,:],in_or_out[x])

    return inside,outside

if __name__ == "__main__":


    if len(sys.argv) != 3:
        print("hey. enter params.txt and points.txt")
        sys.exit()
    
    f1 = open(sys.argv[1], "r")
    if f1.mode == 'r':
        para =f1.read()
#        print("file found")
    else:
        print("file not found")
        sys.exit()

    f2 = open(sys.argv[2], "r")
    if f2.mode == 'r':
        points =f2.read()
#        print("file found")
    else:
        print("file not found")
        sys.exit()
        
#    check_arr()
    rx, ry, rz, tx, ty, tz, f, d, ic, jc = parse_text(para)
    
    
    R  = construct_R(rx,ry,rz)
    t  = construct_t(tx,ty,tz)
    t = -t
    Rt = construct_Rt(R,t)
    K  = construct_K(f,d,ic,jc)
    x,y,z = parse_points(points)
    points_arr = construct_points(x,y,z)
    M = np.matmul(K,Rt)
    print_M(M)
    inside,outside = compute_in_out(M,points_arr,y)
    
    if(len(inside)==0):
        print("visible")
    else:
        print("visible: " + str(inside).replace("[","").replace("]","").replace(",",""))
        print("hidden: " +str(outside).replace("[","").replace("]","").replace(",","") )
    
