import numpy as np
import math as math
import random
from scipy.spatial import Voronoi as vp
import pymel.core as pm
import voronoi as vo
from collections import defaultdict

tSize = 100
tSub = 50
terrain = None

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def main():
    # terrain = pm.polyPlane( n='wTerrain', sx=tSub, sy=tSub, w=tSize, h=tSize)
    createRiver()

def computeRiverAltitude( river, angle=0.05 ):
    #default angle is 1 degree
    #edit Points
    rEPs = np.array(getCVRiver3D ( river ))
    print rEPs
    #generate a random value from 0 to angle
    rAngle = np.random.uniform( 0, angle, len(rEPs) )
    # print 'angle ' + str(rAngle)
    y = [0]
    tY = 0
    #for from second point to last
    for i in range( 1, len(rEPs) ):
        dist = np.linalg.norm(rEPs[i] - rEPs[i-1])
        # print 'dist ' + str(dist)
        tY += dist*np.tan(angle)
        y.append( tY )
        # print y
    rEPs[:,1] = y
    print rEPs
    return rEPs

def draw3dRiver( river2d ):
    river = pm.curve( n='rCurve3D', p=computeRiverAltitude(river2d) )

def computeTerrain( river ):
    rEPs = np.array(getEditPointsRiver2D ( river ))
    rPoints = computeBoundary(rEPs)

    # print rEPs
    pm.curve( d=1, p=getEditPointsRiver3D ( river ) )

    # print rPoints
    vorPoints_np = vp(rPoints)
    # print vorPoints_np
    # print vorPoints_np.vertices
    vorRegions = []
    for x in vorPoints_np.regions:
        nonNegative = True
        for y in x:
            if y == -1:
                nonNegative = False
        if nonNegative is True:
            #not empty
            if x:
                vorRegions.append(x)

    adjVertices = computeAdjacentVertices(vorRegions)
    # print vorRegions
    vorFaces = []
    faceNames = []
    for region in vorRegions:
        tempFace = []
        for vertex in region:
            npVertex = vorPoints_np.vertices[vertex]
            npVertex = np.insert(npVertex, 1, 0.0)
            tempFace.append(npVertex)
        # print tempFace
        vorFaces.append(tempFace)
        faceNames.append( pm.polyCreateFacet( n='terrainPlane', p=tempFace )[0] )
    pm.group( faceNames, n='terrain')

    
def computeBoundary(rEPs):
    tEPs = np.absolute(rEPs)
    xmax, zmax = abs(tEPs.max(axis=0))
    boundary = max( xmax, zmax ) * 1.1
    print boundary
    rEPs = np.append(rEPs, [[-boundary,-boundary]], axis=0)
    rEPs = np.append(rEPs, [[boundary,-boundary]], axis=0)
    rEPs = np.append(rEPs, [[-boundary,boundary]], axis=0)
    rEPs = np.append(rEPs, [[boundary,boundary]], axis=0)

    return rEPs

def computeAdjacentVertices( regions ):
    adjVertices = defaultdict( list )

    rIndex = 0
    for region in regions:
        for vertex in region:
            adjVertices[vertex].append (rIndex)
        rIndex += 1
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
