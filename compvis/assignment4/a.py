import cv2
import numpy as np
import sys
from sklearn.cluster import DBSCAN

tau = 0

def odd(num): #one decimal display
    a = str((round(num*1000)/1000))
    a = format(num, '.1f')
    return a  


def tdd(num): #two decimal display
    a = str((round(num*1000)/1000))
    a =format(num, '.2f')
    return a    


def display_img_opencv_full_size(img_name, img): # display pic from notes

    cv2.imshow(img_name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
   
    

def find_inliers(inter,M,b): # uses objective function to count inliers
    
    global tau
    
    new_x = inter[0]
    new_y = inter[1]
    tau_sq = tau*tau
    k = 0
    inl = []
    outl= []
       
    for i in range(M.size):

        card = ((M[i]*new_x) - new_y + b[i])**2
        
        if((card<tau_sq)):
            k=k+1
            inl.append(i)
        else:
            outl.append(i)
    return k,inl,outl
    
    
def find_intersection(m1,b1,m2,b2): # uses geometric formula for finding intersections
    
    new_x = (b2-b1)/(m1-m2)
    new_y = (new_x*m1)+b1
    return [new_x, new_y]

def find_center(point,M,b): # uses linear regression to find line, then the average x value to get FoE
    
    global tau
    n = 0
    k = 1
    LR_points = []
    size = M.shape[0]
     
    while n < M.shape[0]:
        m = n+1
        while k <M.shape[0]:
            calc_point = find_intersection(M[n],b[n],M[k],b[k])
            dist = np.sqrt(((calc_point[0]-point[0])**2) + ((calc_point[1]-point[1])**2) )
            if dist <= tau :
                LR_points.append(calc_point)
                
            k = k+1
        n = n+1

        LR_points = np.asarray(LR_points)
    Ys = np.expand_dims(LR_points[:,1],axis=1)
    ones = np.ones((LR_points.shape[0],1))
    Xs = np.concatenate((ones,np.expand_dims(LR_points[:,0],axis =1)),axis=1)
    inv_XtX = np.linalg.inv(np.matmul(Xs.T,Xs))
    XtY = np.matmul(Xs.T,Ys)
    co = np.matmul(inv_XtX,XtY)
    
    new_x = np.mean(LR_points[:,0])
    new_y = (co[1]*new_x)+co[0]
    print("FoE Found:", int(new_x),int(new_y[0]))
    return [new_x,new_y[0]]

    
    
def RANSAC(M,b): # standard ransac except points and coefficent roles are reversed

    global tau
    
    tau = 30
    samples = 300
    print("tau set to", tau)
    print("number of samples:", samples)
    N = M.shape[0]
    kmax = 0 
    
    for i in range(samples):
        
        sample = np.random.randint(0, N, 2) # gets 2 random indexes
        if(sample[0]!=sample[1]): # ignores same index samples
            inter = find_intersection(M[sample[0]],b[sample[0]],M[sample[1]],b[sample[1]])
            k,_,_ = find_inliers(inter,M,b)
            
            if(kmax<k): # if we find a soln with more inliers
                kmax = k
                point = inter
    
    k,inliers,outliers = find_inliers(point,M,b)
    FoE = find_center(point,M[inliers],b[inliers])
    print("Inliers found:",len(inliers))
    print("Outliers found:",len(outliers))
    return FoE, np.asarray(inliers),np.asarray(outliers)



def drawlines(img1,lines,pts1,pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r,c = img1.shape[0],img1.shape[1]
#    img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
#    img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)
    for r,pt1,pt2 in zip(lines,pts1,pts2):
        color = tuple(np.random.randint(0,255,3).tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,1)
        img1 = cv2.circle(img1,tuple(pt1),5,color,-1)
#        img2 = cv2.circle(img2,tuple(pt2),5,color,-1)
    display_img_opencv_full_size("FoE img",img1)
    return img1

def create_motion(pt1,pt2): #motion is pt2-pt1 for x and y coord. Also makes lines out of result.
    new_points_2 = pt2-pt1
    motion_vect = new_points_2
    M = (pt2[:,1]-pt1[:,1])/(pt2[:,0]-pt1[:,0])
    b = pt1[:,1]-M[:]*pt1[:,0]
    
    return M,b,motion_vect
    

def frame_analysis(img1,img2): # writes cirlces and lines onto image 2 and finds features to look at. 

    # based on optical flow example in opencv docs
    
    number_of_corners = 500  
    
    feature_params = dict( maxCorners = number_of_corners,
                            qualityLevel = 0.35,
                            minDistance =  5,
                           blockSize = 7 )
    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (7,7),
                      maxLevel = 2,
                      criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, .03))
    
    # Create some random colors
    color = np.random.randint(0,255,(number_of_corners,3))
    
    # Take first frame and find corners in it
    old_frame = img1
    old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
    
    # Create a mask image for drawing purposes
    mask = np.zeros_like(old_frame)
    frame = img2
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **lk_params)
    good_new = p1[st==1]
    good_old = p0[st==1]
    new_err = err[st==1]
    mask_dist = np.zeros(new_err.shape[0])
    old_size = (new_err.shape[0])

    m,B,motion_vectors = create_motion(good_old,good_new) #get motion lines

    motion_mag = np.sqrt(motion_vectors[:,0]**2+motion_vectors[:,1]**2)
    thresh = 3 
    mask_dist = motion_mag>thresh
    motion_mag = motion_mag[mask_dist ==1] # mask based on size of motion
    m = m[mask_dist ==1]
    B = B[mask_dist ==1]
    motion_vectors = motion_vectors[mask_dist==1,:]
    
    new_err = new_err[mask_dist == 1]
    good_new_moving = good_new[mask_dist == 1]
    good_old_moving = good_old[mask_dist == 1]
    new_size = (new_err.shape[0])
    print("Number of points before stationary threshold:", old_size)
    print("Number of points after stationary threshold:", new_size)
    
    for i,(new,old) in enumerate(zip(good_new,good_old)):    
        a,b = new.ravel()  
        c,d = old.ravel()
        frame = cv2.line(frame, (a,b),(c,d), color[i].tolist(), 2)
        frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
    img = cv2.add(frame,mask)
    
    display_img_opencv_full_size("Motion Image", img)
    
    moving = new_size/old_size
    
    return moving,good_new_moving,good_old_moving,m,B,motion_vectors, img


def make_lines(m,b): #unused
    
    ones = -1*np.ones(m.shape[0])
    lines = [m,ones,b]
    lines = np.asarray(lines)
    lines = np.swapaxes(lines,0,1)
    
    return lines


def normalize_features(motion_vect,img,out_pts1,out_pts2): # normalizes features between 0 and 1
    motion_x = motion_vect[:,0]**2
    motion_y = motion_vect[:,1]**2
    motion_mag = np.sqrt(motion_x**2 + motion_y**2)
    
    motion_factor = 1
    motion_x = ((motion_x - np.amin(motion_x))/(np.amax(motion_x)-np.amin(motion_x)))*motion_factor
    motion_y = ((motion_y - np.amin(motion_y))/(np.amax(motion_y)-np.amin(motion_y)))*motion_factor
    motion_mag = ((motion_mag - np.amin(motion_mag))/(np.amax(motion_mag)-np.amin(motion_mag)))*motion_factor
    
    
    r_dim = img.shape[0]
    c_dim = img.shape[1]
    
    out_pts1[:,0] = out_pts1[:,0]/c_dim
    out_pts1[:,1] = out_pts1[:,1]/r_dim
    motion_x = np.expand_dims(motion_x,axis=1)
    motion_y = np.expand_dims(motion_y,axis=1)
    motion_mag = np.expand_dims(motion_mag,axis=1)
    motion = np.concatenate((motion_x,motion_y,motion_mag), axis=1)
    features = np.concatenate((out_pts1,motion),axis=1)

    return features
    
def find_and_print_rectangle(points, img): # prints rectangle and points in clusters within bounding box
    
    min_x = np.amin(points[:,0])-5 
    min_y = np.amin(points[:,1])-5
    max_x = np.amax(points[:,0])+5
    max_y = np.amax(points[:,1])+5
    point1 = (int(min_x),int(min_y))
    point2 = (int(max_x),int(max_y))
#    print("points:",point1,point2)
    
    for x in range(points.shape[0]):
        pt1 = points[x]
        img = cv2.circle(img,tuple(pt1),5,(0,255,0),-1)
        
    img = cv2.rectangle(img, point1, point2, (0,0,255))

    return img
    
    
def FoE_image_maker(FoE,img2):
    text = "FoE"
    FoE = (int(FoE[0]),int(FoE[1]))
    img2 = cv2.circle(img2,FoE,8,(0,0,200),-1)
    cv2.putText(img2, text, FoE, cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)

    display_img_opencv_full_size("FoE", img2)
    cv2.imwrite("FoE.png", img2 )
    
def db_scan_maker(features, img2_dup1,pts): #performs clustering
    
    db = DBSCAN(eps=.08, min_samples=2).fit(features)
    labels = db.labels_
#    print(labels)
    print("Number of Clusters found:", np.amax(labels)+1)

    for i in range(np.amax(labels)+1):
#        print(np.where(labels==i+1)[0])
        indices = np.where(labels==i)
        temp_pt2 = pts[indices]
        img2_dup1 =find_and_print_rectangle(temp_pt2,img2_dup1)
        
    indices = np.where(labels==-1)
    temp_pt2 = pts[indices]
    for x in range(temp_pt2.shape[0]):
        pt1 = temp_pt2[x]
        img = cv2.circle(img2_dup1,tuple(pt1),5,(30,30,200),-1)

        
    return img2_dup1

if __name__ == "__main__":
    print()
    img_name1 = (sys.argv[1])
    img_name2 = (sys.argv[2])
    img1 = cv2.imread(img_name1)
    img2 = cv2.imread(img_name2)
    img2_dup1 = cv2.imread(img_name2)
    moving,pts2,pts1,m,b,motion_vectors,img2 = frame_analysis(img1,img2)

    
    if moving > .60:
        print("camera is moving,", odd(moving*100), "% of points are in motion")
        print()
        FoE,inlier_index,outlier_index = RANSAC(m,b)
#        lines = make_lines(m[inlier_index],b[inlier_index])
        FoE_image_maker(FoE,img2)
        out_pts1 = pts1[outlier_index]
        out_pts2 = pts2[outlier_index]
        motion_vector = motion_vectors[outlier_index,:]
        features = normalize_features(motion_vector,img2,out_pts1,out_pts2)
        db_scan_maker(features,img2_dup1, out_pts2)
        display_img_opencv_full_size("clustered", img2_dup1)
        cv2.imwrite("Clustered.png", img2_dup1  )

    else:
        print("camera is not moving,",odd(moving*100), "% of points are in motion")
        print()
        features = normalize_features(motion_vectors,img2,pts1,pts2)
        db_scan_maker(features,img2_dup1,pts2)
        display_img_opencv_full_size("clustered", img2_dup1)
        cv2.imwrite("Clustered.png", img2_dup1 )

    print()
