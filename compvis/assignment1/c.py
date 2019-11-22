import cv2
import numpy as np
import os
import sys



def display_img_opencv_full_size(img_name, img):
    """
    We can display images directly through OpenCV.  You will notice
    that this generates a huge window.
    """
    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def get_images_names(dir_name, should_list_images=False):
    '''
    Return the name of a randomly-chosen image from the given folder.
    Show the list of images in the folder if that is requested.
    '''
#    random.seed()
    os.chdir(dir_name)
    img_list = os.listdir('./')
    img_list = [name for name in img_list if 'jpg' in name.lower()]

    if should_list_images:
        print("Here are the images in %s" % dir_name)
        for i_name in img_list:
            print(i_name)
        print()

#    ii = random.randint(0, len(img_list) - 1)
    return img_list

def make_image_tensor(img_list):
    
    for x in range(img_list.size)
        print(img_list[x])
    
    
    

def find_two_images(im_list):
    
    size = len(im_list)
    comp = np.zeros((3,size))
    
    for x in range(size):
        i_name = im_list[x]
        img = cv2.imread(i_name)
        comp[:,x] = [np.mean(img[:,:,0]),np.mean(img[:,:,1]),np.mean(img[:,:,2])]

#    for x in range(size):
#        print(comp[:,x])
    
    diff = np.zeros((size,size))
    
    for x in range(size):
        for y in range(size):
            diff[x,y] = (((comp[0,x]-comp[0,y])*(comp[0,x]-comp[0,y]))+((comp[1,x]-comp[1,y])*(comp[1,x]-comp[1,y]))+((comp[2,x]-comp[2,y])*(comp[2,x]-comp[2,y])))
    
#    print(diff.astype(np.uint8))
    ind = np.unravel_index(np.argmax(diff, axis=None), diff.shape)
#    print(ind[0])
#    print(ind[1])
#    print(diff.astype(np.uint8))
    print("Checkerboard from " + im_list[ind[0]] + " and " + im_list[ind[1]] + ". Distance between them is " + str(np.amax(diff)) )


    return ind
    
def crop_image(image):
    
    crop_axis  = image.shape[0]
    other_axis = image.shape[1]
    
    if(crop_axis < image.shape[1]):
        crop_axis  = image.shape[1]
        other_axis = image.shape[0]

#    print(image.shape)
    
    if(crop_axis != other_axis):
        dif   = (crop_axis - other_axis)/2
        start = dif
        end = crop_axis- dif
    
#    print(start)
#    print(end)
    
        if(crop_axis == image.shape[1]):
        
            image = image[ : , int(start):int(end)]
        
        if(crop_axis == image.shape[0]):
 
            image = image[int(start):int(end) , : ]

        print("Image cropped at (0," + str(int(start)) + ") and (" + str(int(end)) + "," + str(int(crop_axis-1)) + ")")
    
    else:
        print("Image does not require cropping")
    
    return image
    
def resize(img, s):    

    if(img.shape[0] != s & img.shape[1] != s):
        new_img = cv2.resize(img, (int(s), int(s)))
        print("Resized from " + str(img.shape) + " to " + str(new_img.shape))
    else:
        print("No resizing needed")
        new_img = img
        
    return new_img
    
def make_ch_board(img_1, img_2, M, N):
    
#    print("here!")
    
    top     = np.concatenate((img_1,img_2), axis=0)
    bot     = np.concatenate((img_2,img_1), axis=0)
    block   = np.concatenate((top,bot), axis=1)
    block1  = np.concatenate((top,bot), axis=1)
    block2  = np.concatenate((top,bot), axis=1)

#    new_img = np.tile(block.astype(np.uint8),(int(int(M)/2),int(int(N)/2,1)))
    
    for x in range(int(int(M)/2)-1):
        block1 = np.concatenate((block1,block), axis=0)
        block2 = np.concatenate((block2,block), axis=0)
    for y in range(int(int(N)/2)-1):
        block2 = np.concatenate((block2,block1), axis=1)

    
    display_img_opencv_full_size("checkerz", block2)
    

if __name__ == "__main__":
    
    print('')
    if len(sys.argv) != 6:
        print("hey. enter a directory, then an image name, then 3 numbers.")
        sys.exit()
    
    dir_name = sys.argv[1]
    out_name = sys.argv[2]
    M = int(sys.argv[3] )
    N = int(sys.argv[4])
    s = int(sys.argv[5])
    
#    print(dir_name)
#    print(out_name)
#    print(M)
#    print(N)
#    print(s)    
    
    im_list = get_images(dir_name)
    sizer = (len(im_list))

    if(sizer > 2):
        
        ind = find_two_images(im_list)
#        print(im_list[ind[0]])
        img_1 = cv2.imread(im_list[ind[0]])
        img_2 = cv2.imread(im_list[ind[1]])
#        print(ind)
        display_img_opencv_full_size("checkerz", img_1)
        display_img_opencv_full_size("checkerz", img_2)

        img_1 = crop_image( img_1 )
        img_1 = resize( img_1, s )
        
        img_2 = crop_image( img_2 )
        img_2 = resize( img_2, s )

        make_ch_board(img_1,img_2,M,N)
        
    if(sizer == 2):
        
        print("Exactly two images: " + im_list[0] + " and " + im_list[1] + ". Creating a checkerboard from them." )
        img_1 = cv2.imread(im_list[0])
        img_2 = cv2.imread(im_list[1])       
        img_1 = crop_image( img_1 )
        img_1 = resize( img_1, s )
        img_2 = crop_image( img_2 )
        img_2 = resize( img_2, s )
        
        make_ch_board(img_1,img_2,M,N)


        
    if(sizer == 1):
        print("One image: " + im_list[0] + ". It will form the white square.")
        img_1 = cv2.imread(im_list[0])
        img_1 = crop_image( img_1 )
        img_1 = resize( img_1, s )
        black = np.ones((s,s,3))*255
#        print(black.shape)
        make_ch_board(img_1,black,M,N)





    if(sizer == 0):
        print("No images. Creating an ordinary checkerboard.")
        white = np.zeros((s,s,3))
        black = np.ones((s,s,3))*255
        make_ch_board(white,black,M,N)

