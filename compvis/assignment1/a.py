import cv2
import numpy as np
import sys

def tdd(num): #two decimal display
    a = str((round(num*100)/100))
    return a

def display_img_opencv_full_size(img_name, img):
    """
    We can display images directly through OpenCV.  You will notice
    that this generates a huge window.
    """
    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def average_function( h, w, b, img):
    sum = 0
    for x in range(0, b, 1):
        for y in range(0, b, 1):
            sum = sum+img[h+x,w+y]
    
    ave = sum/(b*b)
    return ave
#    print('average is ' + str(ave) )

    
def average_image(m, n, M, N, img):
    test1 = np.zeros((m,n))
    sn = (N//n)
    sm = (M//m)
#    print(img)
    print(str(M/m) + " rounds to " + str(sm)) 
    print(str(N/n) + " rounds to " + str(sn)) 
    i = 0
    for x in range(0,m):
        print("x = " + str(x*sm) + " x+1 = " + str(((x+1)*sm)-1))
        for y in range(0,n):
#            test1[x,y] = average_function(x*b, y*b, b, img)
            a = img[round(x*sm):round(((x+1)*sm))-1,round(y*sn):round(((y+1)*(sn)))-1]
            test1[x,y] = np.mean(a)
            print("y = " + str(y*sn) + " y+1=" + str(((y+1)*(sn))-1))
            i = i+1


#    print(test1.astype(np.uint8))
#    print('')
#    sn = (N/n)
#    sm = (M/m)
#    test = cv2.resize(img, (n,m), fx = sn, fy = sm, interpolation = cv2.INTER_AREA)
#    print(test)
    print(i)
    return test1

def block_image(d_img, mb, nb, m, n, b):


    new_img = np.zeros((mb,nb))
    for x in range(0,m):
        for y in range(0,n):
            new_img[(x*b):(((x+1)*b)),(y*b):(((y+1)*(b)))] = d_img[x,y]
    
    return new_img
            
if __name__ == "__main__":

    if len(sys.argv) != 5:
        print("hey. enter an image, then 2 numbers, and a scale.")
        sys.exit()


        
    img_name = sys.argv[1]

    """
    Open the image using OpenCV
    """
    img = cv2.imread(img_name,0)

    print('Image shape:', img.shape)
    m = int(sys.argv[2])
    n = int(sys.argv[3])
    b = int(sys.argv[4])
    d_img = average_image(m, n, img.shape[0],img.shape[1], img)
    new_img = block_image(d_img, m*b, n*b, m, n, b)
    med = np.median(new_img.flatten())
    th, dst = cv2.threshold(new_img, med, 255, cv2.THRESH_BINARY);
    print('Downsized images are (' + str(m) + ', ' + str(n)+ ')')
    print('Block images are ' + str(m*b) + ', ' + str(n*b))
    print('Average intensity at (' + str(m//4) + ', ' + str(n//4) + ') is ' + tdd(d_img[m//4,n//4]))
    print('Average intensity at (' + str(m//4) + ', ' + str(3*n//4) + ') is ' + tdd(d_img[m//4,3*n//4]))
    print('Average intensity at (' + str(3*m//4) + ', ' + str(n//4) + ') is ' + tdd(d_img[3*m//4,n//4]))
    print('Average intensity at (' + str(3*m//4) + ', ' + str(3*n//4) + ') is ' + tdd(d_img[3*m//4,3*n//4]))
    print('Binary threshold: ' + str(round(med*10)/10))
  
    img_1 = cv2.resize(new_img, (n*b, m*b))
    name_to_display = 'Resized ' + img_name
#    display_img_opencv_full_size(name_to_display, d_img)
#    display_img_opencv_full_size(name_to_display, dst)
    print(img_name)
    im_name_1 = img_name.replace(".jpg","")+"_g.jpg"
    cv2.imwrite(im_name_1 ,new_img.astype(np.uint8))
    print("Wrote image "+im_name_1)
    im_name_2 = img_name.replace(".jpg","")+"_b.jpg"
    cv2.imwrite(im_name_2,dst.astype(np.uint8))
    print("Wrote image "+im_name_2)
