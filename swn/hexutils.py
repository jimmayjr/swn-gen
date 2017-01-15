#!/usr/bin/env python

# Axial coordinate conversions -------------------------------------------------
## Axial to cube.
def axial_to_cube(q,r):
    x = q
    z = r
    y = -x-z
    return(x,y,z)

## Axial to odd-q.
def axial_to_odd_q(q,r):
    (x,y,z) = axial_to_cube(q,r)
    (row,col) = cube_to_odd_q(x,y,z)
    return(row,col)

# Cube coordinate conversions --------------------------------------------------
## Cube to axial.
def cube_to_axial(x,y,z):
    q = x
    r = z
    return(q,r)

## Cube to odd-q.
def cube_to_odd_q(x,y,z):
    col = x
    row = z + (x - (x&1)) / 2
    return(row,col)

# Offset coordinate conversions ------------------------------------------------
## Odd-q to axial.
def odd_q_to_axial(row,col):
    (x.y,z) = odd_q_to_cube(row,col)
    (q,r) = cube_to_axial(x,y,z)
    return(q,r)

## Odd-q to cube.
def odd_q_to_cube(row,col):
    x = col
    z = row - (col - (col&1)) / 2
    y = -x-z
    return(x,y,z)

# Rounding ---------------------------------------------------------------------
def axial_round(q,r):
    (x,y,z) = axial_to_cube(q,r)
    (rx,ry,rz) = cube_round(x,y,z)
    (rq,rr) = cube_to_axial(rx,ry,rz)
    return(rQ,rR)

def cube_round(x,y,z):
    rX = round(x)
    rY = round(y)
    rZ = round(z)
    xDiff = abs(rX - x)
    yDiff = abs(rY - y)
    zDiff = abs(rZ - z)
    if ( (xDiff > yDiff) and (xDiff > zDiff) ):
        rX = -rY-rZ
    elif ( yDiff > zDiff ):
        rY = -rX-rZ
    else:
        rZ = -rX-rY
    return(int(rX),int(rY),int(rZ))

def odd_q_round(row,col):
    (x,y,z) = odd_q_to_cube(row,col)
    (rX,rY,rZ) = cube_round(x,y,z)
    (rRow,rCol) = cube_to_odd_q(rX,rY,rZ)
    return(rRow,rCol)

# Distances --------------------------------------------------------------------
## Axial coordinate distance.
def axial_distance(aQ,aR,bQ,bR):
    (aX,aY,aZ) = axial_to_cube(aQ,aR)
    (bX,bY,bZ) = axial_to_cube(bQ,bR)
    return(cube_distance(aX,aY,aZ,bX,bY,bZ))

## Cube coordinate distance.
def cube_distance(aX,aY,aZ,bX,bY,bZ):
    return((abs(aX - bX) + abs(aY - bY) + abs(aZ - bZ))/2)

## Odd-r coordinate distance.
def odd_q_distance(aRow,aCol,bRow,bCol):
    (aX,aY,aZ) = odd_q_to_cube(aRow,aCol)
    (bX,bY,bZ) = odd_q_to_cube(bRow,bCol)
    return(cube_distance(aX,aY,aZ,bX,bY,bZ))

# Neighbors --------------------------------------------------------------------
def axial_neighbors(q,r):
    (x,y,z) = axialtoCube(q,r)
    cn = cube_neighbors(x,y,z)
    neighbors = list()
    for c in cn:
        neighbors.append(cube_to_axial(c[0],c[1],c[2]))
    return(neighbors)

def cube_neighbors(x,y,z):
    relNeighbors = [[ 1,-1, 0],
                    [ 1, 0,-1],
                    [ 0, 1,-1],
                    [-1, 1, 0],
                    [-1, 0, 1],
                    [0, -1, 1]]
    neighbors = list()
    for rn in relNeighbors:
        neighbors.append([x+rn[0],y+rn[1],z+rn[2]])
    return(neighbors)

def odd_q_neighbors(row,col):
    neighbors = list()
    (x,y,z) = odd_q_to_cube(row,col)
    cn = cube_neighbors(x,y,z)
    neighbors = list()
    for c in cn:
        neighbors.append(cube_to_odd_q(c[0],c[1],c[2]))
    return(neighbors)

# Lines ------------------------------------------------------------------------
def axial_line(aQ,aR,bQ,bR):
    (aX,aY,aZ) = axial_to_cube(aQ,aR)
    (bX,bY,bZ) = axial_to_cube(bQ,bR)
    cubeLineList = cube_line(aX,aY,aZ,bX,bY,bZ)
    axialLineList = list()
    for cl in cubeLineList:
        axialLineList.append(cube_to_axial(cl[0],cl[1],cl[2]))
    return(axialLineList)

def cube_line(aX,aY,aZ,bX,bY,bZ):
    d = cube_distance(aX,aY,aZ,bX,bY,bZ)
    line = list()
    for step in range(d+1):
        (rX,rY,rZ) = cube_linterp(aX,aY,aZ,bX,bY,bZ,1.0/d * step)
        line.append(cube_round(rX,rY,rZ))
    return(line)

def odd_q_line(aRow,aCol,bRow,bCol):
    (aX,aY,aZ) = odd_q_to_cube(aRow,aCol)
    (bX,bY,bZ) = odd_q_to_cube(bRow,bCol)
    cubeLineList = cube_line(aX,aY,aZ,bX,bY,bZ)
    oddQLineList = list()
    for cl in cubeLineList:
        oddQLineList.append(cube_to_odd_q(cl[0],cl[1],cl[2]))
    return(oddQLineList)

# Linear interpolation ---------------------------------------------------------
def axial_linterp(aQ,aR,bQ,bR,t):
    (aX,aY,aZ) = axial_to_cube(aQ,aR)
    (bX,bY,bZ) = axial_to_cube(bQ,bR)
    (x,y,z) = cube_linterp(aX,aY,aZ,bX,bY,bZ,t)
    (q,r) = cube_to_axial(x,y,z)
    return(q,r)

def cube_linterp(aX,aY,aZ,bX,bY,bZ,t):
    x = aX + (bX - aX) * t
    y = aY + (bY - aY) * t
    z = aZ + (bZ - aZ) * t
    return(x,y,z)