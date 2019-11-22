import cv2
import numpy as np
import sys


def odd(num): #one decimal display
    a = str((round(num*1000)/1000))
    a = format(num, '.1f')
    return a    


def tdd(num): #two decimal display
    a = format(num, '.2f')
    return a  


def display_img_opencv_full_size(img_name, img): # display pic from notes
    a=1
    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def compute_abs_energy(img): # calculates energy using sobel derivatives

    sobelx = cv2.Sobel(img,cv2.CV_64F, 1, 0)
    sobely = cv2.Sobel(img,cv2.CV_64F, 0, 1)
    energy = np.abs(sobelx)+ np.abs(sobely)
#    display_img_opencv_full_size("energy", energy.astype(np.uint8))
    return energy
 
    
def calculate_seam(W, energy,ind,flag, last_seam_number): # calculates W and finds the seam to be removed
    big_seam_finder = np.zeros(W.shape)

    for i in range(W.shape[0]):
        if i != 0:
            left= np.arange(W.shape[1]-2)
            right= np.arange(W.shape[1]-2)
            center = np.arange(W.shape[1]-2)
            left[1:W.shape[1]]   = W[i-1, 1:-2]
            left[0] = 1000000      
            right[0:W.shape[1]-2]   = W[i-1, 2:(W.shape[1])]
            right[W.shape[1]-3]     = 1000000
            center = W[i-1,1:-1]
            three  = np.vstack((left,center,right))
            W[i,1:-1] = energy[i,1:-1] + np.amin(three, axis = 0)
            big_seam_finder[i-1,1:-1] = np.argmin(three,axis = 0)-1

        else:
            W[0,1:-1] = energy[0,1:-1]


    min_ind =(np.argmin(W[W.shape[0]-1,:]))

    seam = np.flip(big_seam_finder[:,min_ind], axis = 0)

    for i in range(W.shape[0]):
        seam[i] = seam[i]+ seam[i-1]

    seam = seam + min_ind
    reverse_sum = 0
    seam = find_seam(W)
    seam = np.asarray(seam)
#    print(reverse_sum)
#    seam = np.flip(seam, axis = 0)

    for i in range(seam.shape[0]):
        reverse_sum = reverse_sum + energy[i, int(seam[i])]
    

    if(ind == 0 or ind == 1 or ind == (last_seam_number)) and flag == 1:
        print("Points on seam: " + str(ind))
        print("vertical")
        print("0, " + str(seam[0]))
        print( str(W.shape[0]//2) + ", " + str(seam[W.shape[0]//2]) )
        print( str(W.shape[0]-1) + ", " + str(seam[W.shape[0]-1]) )
        print("Energy of seam " + str(ind) + ": " + tdd(reverse_sum/W.shape[0]))
        print("")
        
    if(ind == 0 or ind == 1 or ind == (last_seam_number)) and flag == 0:
        print("Points on seam: " + str(ind))
        print("horizontal")
        print(str(seam[0])+", 0")
        print( str(seam[W.shape[0]//2]) + ", " +str(W.shape[0]//2)  )
        print( str(seam[W.shape[0]-1]) + ", " +str(W.shape[0]-1) )
        print("Energy of seam " + str(ind) + ": " + tdd(reverse_sum/W.shape[0]))
        print("")

    return W,seam


def remove_seam(img_bw, img_c,seam_ind, ind, img_name, flag): # copies over the columns without the pixel
    new_img_bw = np.zeros((img_bw.shape[0], img_bw.shape[1]-1))
    new_img_c = np.zeros((img_c.shape[0], img_c.shape[1]-1 ,img_c.shape[2]))
    
    if(ind == 0):
        img_c = print_seam(img_c,seam_ind,img_name,flag)
    
    for i in range(img_bw.shape[0]):

        new_img_bw[i,0:seam_ind[i]] = img_bw[i,0:seam_ind[i]]
        new_img_bw[i,seam_ind[i]:img_bw.shape[1]] = img_bw[i,seam_ind[i]+1:img_bw.shape[1]]
        new_img_c[i,0:seam_ind[i], :] = img_c[i,0:seam_ind[i],:]
        new_img_c[i,seam_ind[i]:img_bw.shape[1],:] = img_c[i,seam_ind[i]+1:img_bw.shape[1],:]

    return new_img_bw, new_img_c



def print_seam(img_c, seam, name, flag): # creates the image with the first seam in all red
    
    red_line = img_c
    img_name = name.replace(".png","")
    for i in range(img_bw.shape[0]):

        red_line[i,seam[i],0] = 0
        red_line[i,seam[i],1] = 0
        red_line[i,seam[i],2] = 254
        
    if flag == 0:
        img_c =np.swapaxes(img_c,0,1)
        
    cv2.imwrite(img_name+"_seam.png",img_c.astype(np.uint8))
#    display_img_opencv_full_size("seam_c", red_line.astype(np.uint8))
    if flag == 0:
        img_c =np.swapaxes(img_c,0,1)
    
    return img_c

def find_seam(W): # traces back the minimum energy path to get seam to remove
    leg = W.shape[0]-1
    index = np.argmin(W[leg,:])
    list_of_ind = []
    i = leg-1
    
    while 0 <= i:
        
        if(0==index): #should never happen
            print("index 0, readjusting")
            min_vec = np.asarray([1000000 , W[i,index], W[i,index+1]])
#        elif(W.shape[0]==index): # happens occasionally BUT DOES NOT CRASH
#            print("large index, readjusting")
#            min_vec = np.asarray([ W[i,index-1], W[i,index], 1000000])
        else:
            
            min_vec = np.asarray([W[i,index-1], W[i,index], W[i,index+1]])
            
        small_ind = np.argmin(min_vec)
        list_of_ind.append(index)

        if(small_ind==0):
            index = index-1
        elif(small_ind==1):
            index = index
        elif(small_ind==2):
            index = index+1
            
        i = i-1

    list_of_ind.append(index)
    list_of_ind = list(reversed(list_of_ind))
    return list_of_ind

    
    
    

if __name__ == "__main__":


    if len(sys.argv) != 2:
        print("hey. enter an image, then 2 numbers, and a scale.")
        sys.exit()
        
    img_name = (sys.argv[1])
    
    img_bw = cv2.imread(img_name,0)
    img_c = cv2.imread(img_name)

    flag = 0
    
    if(img_bw.shape[1]<img_bw.shape[0]):
        img_bw = img_bw.T
        img_c =np.swapaxes(img_c,0,1)

    else:
        flag = 1

    if(img_bw.shape[1]==img_bw.shape[0]):
        print("image is square")
        sys.exit()
        
    # initializing
    energy = compute_abs_energy(img_bw)
    W = np.zeros(img_bw.shape)
    W[:,0]= np.ones(W.shape[0])*1000000
    W[:,W.shape[1]-1] = np.ones(W.shape[0])*1000000 
    i = 0
    last_seam_number = W.shape[1]-W.shape[0]-1
    
    # the actual algorithm
    while W.shape[0]!=W.shape[1]-1: 
        energy = compute_abs_energy(img_bw)
        W = np.zeros(img_bw.shape)
        W[:,0]= np.ones(W.shape[0])*1000000
        W[:,W.shape[1]-1] = np.ones(W.shape[0])*1000000 
        
        W,seam = calculate_seam(W,energy,i,flag,last_seam_number)
        img_bw, img_c = remove_seam(img_bw,img_c, seam, i, img_name, flag)
        i=i+1
        
    img_name = img_name.replace(".png","")


    if flag == 1:
        
        cv2.imwrite(img_name+"_final.png",img_c.astype(np.uint8))

    else:
        img_c =np.swapaxes(img_c,0,1)
        cv2.imwrite(img_name+"_final.png",img_c.astype(np.uint8))

