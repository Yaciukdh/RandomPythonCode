import numpy as np
import sys


def tdd(num): #three decimal display
    a = str((round(num*1000)/1000))
    a =format(num, '.3f')
    return a    
    
def make_line(ix,iy,jx,jy):
    
    cov = np.cov([ix, jx],[iy, jy],bias=True) # orthogonal least squares
    val,ei = np.linalg.eig(cov)
    
    if(0==val[0]):
        a = ei[0,0]
        b = ei[1,0]
        
    else:
        a = ei[0,1]
        b = ei[1,1]
        
    #finding rho via theta and ux,uy method
    theta = np.arccos(a)
    ux = (ix+jx)/2
    uy = (iy+jy)/2
    rho = ux*np.cos(theta)+uy*np.sin(theta)

    return np.array([a,b,-rho])

def find_inliers(co_array, tau, x,y): # uses objective function to count inliers
    
    a   = co_array[0]
    b   = co_array[1]
    rho = co_array[2]
    tau_sq = tau*tau
    k = 0
    
    for i in range(x.size):

        card = (a*x[i]+ b*y[i] +rho)*(a*x[i]+ b*y[i] +rho)
        if((card<tau_sq)):
                k=k+1
    return k
    
def find_ave_in_out(co_array, tau, x,y): # finds average distance of outliers and inliers

    a   = co_array[0]
    b   = co_array[1]
    rho = co_array[2]
    tau_sq = tau*tau
    
    # counters and sum vars
    k_i = 0
    sum_i = 0
    k_o = 0
    sum_o = 0
 
    for i in range(x.size):

        card = (a*x[i]+ b*y[i] +rho)*(a*x[i]+ b*y[i] +rho)
        if((card<tau_sq)):
                k_i = k_i+1
                dist = np.abs(a*x[i] + b*y[i] + rho)
                sum_i = sum_i + dist
                
        else:
                k_o = k_o + 1
                dist = np.abs(a*x[i] + b*y[i] + rho)
                sum_o = sum_o + dist
    
    ave_in = sum_i/k_i
    ave_out = sum_o/k_o
    ave = np.array([ave_in, ave_out])
    
    return ave
    
if __name__ == "__main__":

    if len(sys.argv) == 4:
       
        text_file_name = (sys.argv[1])
        samples = int(sys.argv[2])
        tau = float(sys.argv[3])
        
    elif len(sys.argv) == 5:
        
        text_file_name = (sys.argv[1])
        samples = int(sys.argv[2])
        tau = float(sys.argv[3])
        seed = int(sys.argv[4])
        np.random.seed(seed)
        
    else:
        print("hey. enter a .txt, a tau, and an output name")
        sys.exit()

    
    f = open(text_file_name, "r" )
    
    if f.mode == 'r':
        text =f.read()
    else:
        sys.exit()
    

    text = text.split()
    num_arr = np.asarray(text) # separating x and y coord
    x = num_arr[0:num_arr.size:2].astype(np.float32)
    y = num_arr[1:num_arr.size:2].astype(np.float32)

    kmax = 0
    line = np.array([0,0,0])
    N = x.shape[0]

    
    for i in range(samples):
        
        sample = np.random.randint(0, N, 2) # gets 2 random indexes
        
        if(sample[0]!=sample[1]): # ignores same index samples
            co_array = make_line(x[sample[0]],y[sample[0]],x[sample[1]],y[sample[1]])
            k = find_inliers(co_array, tau, x,y)
            
            if(kmax<k): # if we find a soln with more inliers
                print("Sample "+ str(i) + ":" )
                print("indices (" + str(sample[0]) + "," + str(sample[1]) + ")")
                print("line (" + tdd(co_array[0]) + "," + tdd(co_array[1]) +"," + tdd(co_array[2]) + ")") 
                print("inliers "+ str(k))
                print("")
                kmax = k
                line = co_array

    in_out = find_ave_in_out(line, tau, x,y) #find ending stats
    print("avg inlier dist " + tdd(in_out[0]))
    print("avg outlier dist " + tdd(in_out[1]))
