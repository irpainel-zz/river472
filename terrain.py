import numpy as np
import math as math
import random
from scipy.spatial import Voronoi as vp
import pymel.core as pm
import voronoi as vo
from collections import defaultdict
from region import Region

tSize = 100
tSub = 50
terrain = None


def main():
    # terrain = pm.polyPlane( n='wTerrain', sx=tSub, sy=tSub, w=tSize, h=tSize)
    createRiver()

def computeRiverAltitude( dictRegions, angle=0.05 ):
    #default angle is 1 degree

    #generate a random value from 0 to angle
    rAngle = np.random.uniform( 0, angle, len(dictRegions) )
    # print 'angle ' + str(rAngle)
    tY = 0 #tY is the total sum of y 
    eY = 0
    #for from second point to last
    for i in range( 1, len(dictRegions) ):
        dist = np.linalg.norm(dictRegions[i].point - dictRegions[i-1].point)
        # print 'dist ' + str(dist)
        eY = (dist/2)*np.tan(rAngle[i]) + tY
        tY += dist*np.tan(rAngle[i])
        dictRegions[i].setEPAltitude( tY )
        dictRegions[i-1].setNextEdgeAltitude( eY )
        # print y
    return dictRegions

def draw3dRiver( river2d ):
    river = pm.curve( n='rCurve3D', p=computeRiverAltitude(river2d) )

def computeTerrain( river ):

    rEPs = np.array(getEditPointsRiver2D ( river ))
    #add limit to map to avoid infinity values
    rPoints = computeBoundary(rEPs)

    # print rEPs
    # pm.curve( d=1, p=getEditPointsRiver3D ( river ) )

    vorPoints_np = vp(rPoints)

    vorVertices = vorPoints_np.vertices

    #remove all infinites values
    vorRegions = removeNegatives ( vorPoints_np.regions )

    #create a dict with all the region Objects
    dictRegions= createRegionObjects( vorVertices, vorRegions, rEPs )

    #vertex X is shared by N faces
    adjVertices = computeAdjacentVertices( dictRegions )

    # computeAdjEdges ( adjVertices )
    dictRegions = computeRegionBoundary( dictRegions )

    dictRegions = computeRiverAltitude ( dictRegions )


    for reg in dictRegions.values():
        print reg.pointY
        print reg.nextEdgeY

    # vorFaces = []
    # faceNames = []
    # for region in vorRegions:
    #     tempFace = []
    #     for vertex in region:
    #         npVertex = vorPoints_np.vertices[vertex]
    #         npVertex = np.insert(npVertex, 1, 0.0)
    #         tempFace.append(npVertex)
    #     # print tempFace
    #     vorFaces.append(tempFace)
    #     faceNames.append( pm.polyCreateFacet( n='terrainPlane', p=tempFace )[0] )
    # pm.group( faceNames, n='terrain')

# def computeAdjEdges ( adjVertices ):
#     print adjVertices
#     for key, value in adjVertices.items():
#         if len( value ) > 1:
#             if 

def computeRegionBoundary( dictRegions ):

    for i in range( 0, len(dictRegions) ):
        rI = dictRegions[i].regionI
        for j in range ( i+1, len(dictRegions) ):
            rJ = dictRegions[j].regionI
            # print 'comparing ' + str(rI) + ' with ' + str(rJ)
            edge = intersect(rI, rJ)
            if  edge is not None:
                if dictRegions[i].id == dictRegions[j].id-1:
                    dictRegions[i].setBoundary(edge)
                    continue
    return dictRegions


def createRegionObjects ( vorVertices, rIndeces, rEPs ):
    regionVertices = indexToVertex( vorVertices, rIndeces )
    objRegionsArray = {}
    # print len(regionVertices)
    for region, regionIndex in zip(regionVertices, rIndeces):
        for i in range(0, len(rEPs)):
            if pointInRegion ( rEPs[i], region ):
                objRegionsArray[i] = Region( i, rEPs[i], regionIndex )
                continue
    return objRegionsArray

#receives Region indeces
#returns Region with vertices values
def indexToVertex( vorVertices, vorRegions ):
    regionVertices = []
    for region in vorRegions:
        # print region
        rVertices = []
        for vIndex in region:
            rVertices.append( vorVertices[vIndex].tolist() )
        regionVertices.append( rVertices )
    return regionVertices


#check if point is inside region
def pointInRegion( point, region ):
    poly = region
    x = point[0]
    y = point[1]

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

def intersect(a, b):
    result = list(set(a) & set(b))
    if not result:
        return None
    else:
        return result


def checkPointsInList( pointArray, p1, p2 ):
    if p1 in pointArray:
        if p2 in pointArray:
            return True
        else:
            return False

def removeNegatives( listPoints ):
    rList = []
    for x in listPoints:
        nonNegative = True
        for y in x:
            if y == -1:
                nonNegative = False
        if nonNegative is True:
            #not empty
            if x:
                rList.append(x)
    return rList

def removeNegativeRidges( listPoints ):
    rList = []
    for x in listPoints:
        nonNegative = True
        for y in x:
            if y == -1:
                nonNegative = False
        if nonNegative is True:
            #not empty
            if x:
                rList.append(x)
    return rList
    
def computeBoundary(rEPs):
    tEPs = np.absolute(rEPs)
    xmax, zmax = abs(tEPs.max(axis=0))
    boundary = max( xmax, zmax ) * 2
    # print boundary
    rEPs = np.append(rEPs, [[-boundary,-boundary]], axis=0)
    rEPs = np.append(rEPs, [[boundary,-boundary]], axis=0)
    rEPs = np.append(rEPs, [[-boundary,boundary]], axis=0)
    rEPs = np.append(rEPs, [[boundary,boundary]], axis=0)

    return rEPs

def computeAdjacentVertices( regions ):
    adjVertices = defaultdict( list )

    for key, region in regions.items():
        for vertex in region.regionI:
            adjVertices[vertex].append (key)
    print adjVertices.items()
    return adjVertices

def getEditPointsRiver2D(river):
    #ignores Y value
    rEPs = pm.xform( str(river) + '.ep[*]', q=True, ws=True, t=True )
    # with Y
    #return zip(rEPs[0::3], rEPs[1::3], rEPs[2::3])
    # without Y
    return zip(rEPs[0::3], rEPs[2::3])

def getCVRiver3D(river):
    rEPs = pm.xform( str(river) + '.cv[*]', q=True, ws=True, t=True )
    return zip(rEPs[0::3], rEPs[1::3], rEPs[2::3])

def getEditPointsRiver3D(river):
    rEPs = pm.xform( str(river) + '.ep[*]', q=True, ws=True, t=True )
    return zip(rEPs[0::3], rEPs[1::3], rEPs[2::3])

def createRiver():
    initialPoint = [0, 0, 0]
    river = pm.curve( n='rCurve', p=[initialPoint] )
    addPointsToRiver(river)

def addPointsToRiver(river):
    ctxName = "CurveAddPtCtx"
    pm.select( river , r=True )
    if pm.contextInfo(ctxName, ex=True) is False:
        ctx = pm.curveAddPtCtx("CurveAddPtCtx")
        print ctx
    else:
        ctx = ctxName
    pm.setToolTo(ctx)

def retrieveVertices(name):
    #get points
    xOrig = pm.xform(str(name) + '.vtx[*]', q=True, ws=True, t=True)
    return zip(xOrig[0::3], xOrig[1::3], xOrig[2::3])


if __name__ == "__main__":
    main()
