import cv2
import numpy as np

import os
import sys
import math

def odd(num): #one decimal display
    a = str((round(num*1000)/1000))
    a = format(num, '.1f')
    return a    


def check_energy(energy): # there was a piazza post about checking to make sure there was no 0 energy pixiels
    
    
    energy[energy<.000001] = .000001
        
    return energy

def display_img_opencv_full_size(img_name, img): # display pic from notes

    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def sq_grad(img): # get deriv mag image
        
    sobelx = cv2.Sobel(img,cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(img,cv2.CV_64F, 0, 1, ksize=3)
    
    sobel_mag = sobelx**2 + sobely**2
        
    return sobel_mag
    
    
def make_image_tensor(img_list): # make a multidimensional vector of bw images
    
    l = []
    img_list = sorted(img_list)
    for x in range(len(img_list)):
        img = cv2.imread(img_list[x],0)
        l.append(img)
    a_a = np.asarray(l)
    a_a = np.swapaxes(a_a , 0,1)
    a_a = np.swapaxes(a_a , 1,2)

    return a_a

def get_images(dir_name, home_dir): #gets images from a specificd directory and then returns to last directory
    
# based off of code given by professor Stewart

    os.chdir(dir_name)
    img_list = os.listdir('./')
    img_list = [name for name in img_list if 'jpg' in name.lower()]
    dirz =  os.path.dirname(os.path.realpath(__file__))

    img_array = make_image_tensor(img_list)
    os.chdir(home_dir)
    
    return img_array


def make_image_tensor_c(img_list):# make a multidimensional vector of colored images


    l = []
    img_list = sorted(img_list)

    for x in range(len(img_list)):
        img = cv2.imread(img_list[x])
        l.append(img)
        
    a_a = np.asarray(l)
    a_a = np.swapaxes(a_a , 0,1)
    a_a = np.swapaxes(a_a , 1,2)
    a_a = np.swapaxes(a_a , 2,3)

    return a_a



def get_images_c(dir_name, home_dir): #gets color images from a specificd directory and then returns to last directory

    os.chdir(dir_name)
    img_list = os.listdir('./')
    img_list = [name for name in img_list if 'jpg' in name.lower()]
    dirz =  os.path.dirname(os.path.realpath(__file__))

    img_array = make_image_tensor_c(img_list)
    os.chdir(home_dir)
    
    return img_array


def make_dem(energy): # makes denomonator of weighted average

    dem = np.zeros((energy.shape[0], energy.shape[1]))
    
    for x in range(energy.shape[0]):
        for y in range(energy.shape[1]):
            dem[x,y] = energy[x,y,:].sum()
                 
    return dem

def reduce_num_of_img( img, energy, p): #creates cumulative sum of different images    
    
    new_base = np.zeros((img.shape[0], img.shape[1],img.shape[2]))
    dem = np.zeros((energy.shape[0], energy.shape[1]))
    quick = np.zeros((energy.shape[0],energy.shape[1]))

 

    for x in range(img.shape[0]):
        for y in range(img.shape[1]):
            dem[x,y] = energy[x,y,:].sum()  
            
    for c in range(img.shape[2]):
        for z in range(img.shape[3]):
            quick[:,:] = quick[:,:] + (img[:,:,c,z]*(energy[:,:,z]))
    
        new_base[:,:,c] = quick[:,:]
        quick = np.zeros((energy.shape[0],energy.shape[1]))

    
        
#    print(dem)
#    print(new_base.shape)
    

#    display_img_opencv_full_size("who", last_img)
    return (new_base, dem)



def create_RGB_image(energy, home_dir, dir_name, p): # creates an weighted averaged rbg image
    
    rbg_im_arr = get_images_c(dir_name,home_dir)

    en_tot   = np.ones(rbg_im_arr.shape)
    en_num   = np.ones((energy.shape[0],energy.shape[1], rbg_im_arr.shape[2]))
    last_img = np.ones((energy.shape[0],energy.shape[1], 3))

    energy = np.power(energy,p)
    
#    dem = make_dem(energy) # makes denominator
    en_num, dem = reduce_num_of_img(rbg_im_arr, energy, p) # make numerator
        
    for j in range(last_img.shape[2]): # 
        last_img[:,:,j] = en_num[:,:,j]/dem
    
    ret_arr = last_img.astype(np.uint8)
    
    return ret_arr
    
def print_stats_at_ind(img_list, indx, indy , rgb ): # prints text of stats
    print("")
    print("Energies at (" + str(indx) + "," + str(indy) + ")")
    
    for x in range(img_list.shape[2]):
        print(str(x)+": " +odd(img_list[indx,indy,x]))
    print("RGB = ("  + str(rgb[indx,indy,0]) + ", " + str(rgb[indx,indy,1]) + ", " + str(rgb[indx,indy,1])+ ")" )


def print_end_stats(img_arr, rgb): # sets up printing

    m = img_arr.shape[0]
    n = img_arr.shape[1]
    
    print("Results:")
    
    print_stats_at_ind(img_arr, m//4,n//4, rgb)
    print_stats_at_ind(img_arr, m//4,3*n//4, rgb)
    print_stats_at_ind(img_arr, 3*m//4,n//4, rgb)
    print_stats_at_ind(img_arr, 3*m//4,3*n//4, rgb)

    
if __name__ == "__main__":


    if len(sys.argv) != 5:
        print("hey. enter an image, then 2 numbers, and a scale.")
        sys.exit()
        
    dir_name = (sys.argv[1])
    out_img = (sys.argv[2])
    sig     = float(sys.argv[3])
    p       = float(sys.argv[4])
    
    home_dir =  os.path.dirname(os.path.realpath(__file__))
    
    img_arr = get_images(dir_name, home_dir) # get bw images in array
    shapes = img_arr.shape
    x_dim   = shapes[0]
    y_dim   = shapes[1]
    pic_ind = shapes[2]
    energy = np.zeros(shapes)
    gauss  = np.zeros(shapes)
    h = math.floor((2.5*sig))
    
    for j in range(pic_ind):
        
        
        sq_gr = sq_grad(img_arr[:,:,j])
        energy[:,:,j] = cv2.GaussianBlur((sq_gr),(2*h+1,2*h+1),sig)

    energy = check_energy(energy)
    RGB = create_RGB_image(energy, home_dir, dir_name,p)# makes a rbg image to write

   
    print_end_stats(energy,RGB)
    cv2.imwrite(out_img, RGB.astype(np.uint8))
    print("Wrote " + out_img)
    
