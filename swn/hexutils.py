#!/usr/bin/env python

# Axial coordinate conversions -------------------------------------------------
## Axial to cube.
def axialToCube(q,r):
    x = q
    z = r
    y = -x-z
    return(x,y,z)

## Axial to odd-q.
def axialToOddQ(q,r):
    (x,y,z) = axialToCube(q,r)
    (row,col) = cubeToOddQ(x,y,z)
    return(row,col)

# Cube coordinate conversions --------------------------------------------------
## Cube to axial.
def cubeToAxial(x,y,z):
    q = x
    r = z
    return(q,r)

## Cube to odd-q.
def cubeToOddQ(x,y,z):
    col = x
    row = z + (x - (x&1)) / 2
    return(row,col)

# Offset coordinate conversions ------------------------------------------------
## Odd-q to axial.
def oddQToAxial(row,col):
    (x.y,z) = oddQToCube(row,col)
    (q,r) = cubeToAxial(x,y,z)
    return(q,r)

## Odd-q to cube.
def oddQToCube(row,col):
    x = col
    z = row - (col - (col&1)) / 2
    y = -x-z
    return(x,y,z)

# Rounding ---------------------------------------------------------------------
def axialRound(q,r):
    (x,y,z) = axialToCube(q,r)
    (rx,ry,rz) = cubeRound(x,y,z)
    (rq,rr) = cubeToAxial(rx,ry,rz)
    return(rQ,rR)

def cubeRound(x,y,z):
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

def oddQRound(row,col):
    (x,y,z) = oddQToCube(row,col)
    (rX,rY,rZ) = cubeRound(x,y,z)
    (rRow,rCol) = cubeToOddQ(rX,rY,rZ)
    return(rRow,rCol)

# Distances --------------------------------------------------------------------
## Axial coordinate distance.
def axialDistance(aQ,aR,bQ,bR):
    (aX,aY,aZ) = axialToCube(aQ,aR)
    (bX,bY,bZ) = axialToCube(bQ,bR)
    return(cubeDistance(aX,aY,aZ,bX,bY,bZ))

## Cube coordinate distance.
def cubeDistance(aX,aY,aZ,bX,bY,bZ):
    return((abs(aX - bX) + abs(aY - bY) + abs(aZ - bZ))/2)

## Odd-r coordinate distance.
def oddQDistance(aRow,aCol,bRow,bCol):
    (aX,aY,aZ) = oddQToCube(aRow,aCol)
    (bX,bY,bZ) = oddQToCube(bRow,bCol)
    return(cubeDistance(aX,aY,aZ,bX,bY,bZ))

# Neighbors --------------------------------------------------------------------
def axialNeighbors(q,r):
    (x,y,z) = axialtoCube(q,r)
    cn = cubeNeighbors(x,y,z)
    neighbors = list()
    for c in cn:
        neighbors.append(cubeToAxial(c[0],c[1],c[2]))
    return(neighbors)

def cubeNeighbors(x,y,z):
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

def oddQNeighbors(row,col):
    neighbors = list()
    (x,y,z) = oddQToCube(row,col)
    cn = cubeNeighbors(x,y,z)
    neighbors = list()
    for c in cn:
        neighbors.append(cubeToOddQ(c[0],c[1],c[2]))
    return(neighbors)

# Lines ------------------------------------------------------------------------
def axialLine(aQ,aR,bQ,bR):
    (aX,aY,aZ) = axialToCube(aQ,aR)
    (bX,bY,bZ) = axialToCube(bQ,bR)
    cubeLineList = cubeLine(aX,aY,aZ,bX,bY,bZ)
    axialLineList = list()
    for cl in cubeLineList:
        axialLineList.append(cubeToAxial(cl[0],cl[1],cl[2]))
    return(axialLineList)

def cubeLine(aX,aY,aZ,bX,bY,bZ):
    d = cubeDistance(aX,aY,aZ,bX,bY,bZ)
    line = list()
    for step in range(d+1):
        (rX,rY,rZ) = cubeLInterp(aX,aY,aZ,bX,bY,bZ,1.0/d * step)
        line.append(cubeRound(rX,rY,rZ))
    return(line)

def oddQLine(aRow,aCol,bRow,bCol):
    (aX,aY,aZ) = oddQToCube(aRow,aCol)
    (bX,bY,bZ) = oddQToCube(bRow,bCol)
    cubeLineList = cubeLine(aX,aY,aZ,bX,bY,bZ)
    oddQLineList = list()
    for cl in cubeLineList:
        oddQLineList.append(cubeToOddQ(cl[0],cl[1],cl[2]))
    return(oddQLineList)

# Linear interpolation ---------------------------------------------------------
def axialLInterp(aQ,aR,bQ,bR,t):
    (aX,aY,aZ) = axialToCube(aQ,aR)
    (bX,bY,bZ) = axialToCube(bQ,bR)
    (x,y,z) = cubeLInterp(aX,aY,aZ,bX,bY,bZ,t)
    (q,r) = cubeToAxial(x,y,z)
    return(q,r)

def cubeLInterp(aX,aY,aZ,bX,bY,bZ,t):
    x = aX + (bX - aX) * t
    y = aY + (bY - aY) * t
    z = aZ + (bZ - aZ) * t
    return(x,y,z)


# Plaintext hex representations ------------------------------------------------
#   HEIGHT AND WIDTH MUST BE ODD
# ODDR_TEXT = [r'   _______    ',
#              r'  /       \   ',
#              r' /         \  ',
#              r'/           \ ',
#              r'\           / ',
#              r' \         /  ',
#              r'  \_______/   ']
# ODDR_TEXT_W =     13    # Width
# ODDR_TEXT_H =     7     # Height
# ODDR_TEXT_COORD = (1,4) # Coordinate position, zero indexed
# ODDR_TEXT_LABEL = (4,6) # Label position, zero indexed 

ODDR_TEXT = [r'  _____   ',
             r' /     \  ',
             r'/       \ ',
             r'\       / ',
             r' \_____/  ']
ODDR_TEXT_W =     9     # Width
ODDR_TEXT_H =     5     # Height
ODDR_TEXT_COORD = (1,2) # Coordinate position, zero indexed
ODDR_TEXT_LABEL = (3,4) # Label position, zero indexed 