import numpy as np
import math
import sys

def inpoly( x,y, xpoly, ypoly ):
    """
    Usage: inside = inpoly( x,y, xpoly, ypoly )
    
    Purpose: computes which points are interior to a polygon, including
             the polygon's boundary
                                      
    Input:
      x,y     - (x(n), y(n)) n = 1,npts are points to test
      xpoly,ypoly - (xpoly(i),ypoly(i)) i=1,npoly are vertices of the polygon. 
    
    Output:
      inside  - array of npts logicals, same shape as x
                inside(n)=true if (x(n),y(n)) is in interior
    """

    # check size of input arrays
    npts = x.size
    if ( y.size != npts ):
        print('ERROR inpoly: x and y must be the same length')
        sys.exit(1)
            
    npoly = xpoly.size
    if (ypoly.size != npoly):
        print('ERROR inpoly: xpoly and ypoly must be the same length')
        sys.exit(1)

    # initialize output as false
    inside = np.full(x.shape, False, dtype='bool')
    
    # establish polygon boundary rectangle
    xpolyMin = np.amin(xpoly)
    xpolyMax = np.amax(xpoly)
    ypolyMin = np.amin(ypoly)
    ypolyMax = np.amax(ypoly)
    
   # Ensure polygon is closed and runs 1 more than npoly
    if (xpoly[0] == xpoly[-1]) and (ypoly[0] == ypoly[-1]):
        npoly = npoly-1
    else:
        xpoly = np.append(xpoly, xpoly[0])
        ypoly = np.append(ypoly, ypoly[0])
    
    # constants for vertical lines
    EPS = 0.00000001
    INF = 99999999.0
    
    # characterize polygon line segments just once
    xleft  = xpoly[:npoly]
    xright = xpoly[1:]
    yleft  = ypoly[:npoly]
    yright = ypoly[1:]

    pdelx = xright - xleft # stores consecutive xpoly deltas
    pdely = yright - yleft # stores consecutive ypoly deltas
    pslope = np.full(npoly, INF, dtype='float') # initialize segment slopes as vertical
    nonVert = (abs(pdelx) > EPS)
    pslope[nonVert] = np.divide(pdely[nonVert], pdelx[nonVert])
    
    # store min,max xpoly and ypoly values each segment
    pminx  = np.full(npoly, 0, dtype='float') # min x values each segement
    pminy  = np.full(npoly, 0, dtype='float') # min y values each segement
    pmaxx  = np.full(npoly, 0, dtype='float') # max x values each segement
    pmaxy  = np.full(npoly, 0, dtype='float') # max y values each segement

    xMonotonic = (pdelx > 0)
    xNonMonotonic = np.logical_not(xMonotonic)
    pminx[xMonotonic]    = xleft[xMonotonic]
    pmaxx[xMonotonic]    = xright[xMonotonic]
    pminx[xNonMonotonic] = xright[xNonMonotonic]
    pmaxx[xNonMonotonic] = xleft[xNonMonotonic]
    
    yMonotonic = (pdely > 0)
    yNonMonotonic = np.logical_not(yMonotonic)
    pminy[yMonotonic]    = yleft[yMonotonic]
    pmaxy[yMonotonic]    = yright[yMonotonic]
    pminy[yNonMonotonic] = yright[yNonMonotonic]
    pmaxy[yNonMonotonic] = yleft[yNonMonotonic]

    # To determine if a point (x0,y0) is in or out, an infinite ray (y=y0) 
    # is extended to the right of the point. If it crosses the polygonal 
    # boundary an odd number of times, the point is interior. 
    
    # restrict testing to only points within the polygon bounding box
    testX  = np.logical_and( (x>=xpolyMin), (x<=xpolyMax) )
    testY  = np.logical_and( (y>=ypolyMin), (y<=ypolyMax) )
    testXY = np.logical_and( testX, testY )

    allpts  = np.array(range(npts),  dtype = np.int32)
    allsegs = np.array(range(npoly), dtype = np.int32)
  
    for n in allpts[testXY]:
        x0 = x[n]
        y0 = y[n]

        # find all x intersections of polygon along y=y0 in [x0,INF)
        nintxn = 0
        
        # only look at polygon segments which bracket y=y0
        testK = np.logical_and( (pminy <= y0), (y0 <= pmaxy) )
        
        for k in allsegs[testK]:
                    
            # check for vertex
            if ( (x0 == xpoly[k]) and (y0 == ypoly[k]) ): 
                nintxn = 1
                break
            
            # next check for interior on non-horizontal line segment
            if ( (pslope[k] != 0) and (y0 < pmaxy[k]) ):
                if (pslope[k] == INF):
                    xt = xpoly[k]
                else:
                    # (xt,y0) is on line between (xpoly[k],ypoly[k])
                    #                        and (xpoly[k+1],ypoly[k+1])
                    xt = xpoly[k] + (y0-ypoly[k])/pslope[k]
                if (xt >= x0):
                    if ((xt-x0)>EPS):  
                        nintxn = nintxn+1
                    else:
                        # x0,y0 on boundary - include it
                        nintxn = 1
                        break
                    
            else:
                # horizontal segment - see if (x0,y0) is on it
                if (pslope[k]==0) and (y0 == ypoly[k]) and (pminx[k] <= x0) \
                        and (x0 <= pmaxx[k]):
                    nintxn = 1
                    break
                # test endpoint vertex on this segment as only other possibility
                if ( (x0 == xpoly[k+1]) and (y0 == ypoly[k+1]) ): 
                    nintxn = 1
                    break
                      
        # (x0,y0) is interior if # intersections is odd
        inside[n] = ((nintxn % 2) == 1)
    
    return(inside)
    
