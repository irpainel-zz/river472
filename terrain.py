import numpy as np
from scipy.spatial import Voronoi as vp
import pymel.core as pm
import voronoi as vo

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

def calcTerrain( river ):
    rEPs = getEditPointsRiver3D ( river )
    rEPs = np.append(rEPs, [[-100,-100]], axis=0)
    rEPs = np.append(rEPs, [[100,-100]], axis=0)
    rEPs = np.append(rEPs, [[-100,100]], axis=0)
    rEPs = np.append(rEPs, [[100,100]], axis=0)

    # print rEPs


    #to numpy
    rPoints = rEPs
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

    
    # print vorFaces
    # pm.polyCreateFacet( p=[(0.0, 0.0, 0.0), (10.0, 0.0, 0.0), (10.0, 10.0, 0.0)] )
    # print vorRegions

    # calc voronoi
    # points = []
    # for i in range ( 0, len(rEPs) ):
    #     point =  Point(rEPs[i][0], rEPs[i][1] )
    #     points.append ( Point(rEPs[i][0], rEPs[i][1] ) )
    # vorPoints = vo.computeVoronoiDiagram(points)

    # print vorPoints[2]
    # print vorPoints[0]
    # vorVertices = vorPoints[0]
    # vorIndex = vorPoints[2]
    # edgesDict = {}
    # for i in range ( 0, len(vorIndex) ):
    #     # if vorIndex[i][1] == -1 or vorIndex[i][2] == -1 :
    #     edgesDict[ vorIndex[i][0] ] = ( [ vorVertices[ vorIndex[i][1] ],  vorVertices[ vorIndex[i][2] ] ] )
    #     # else:
    #     #     print "i found infinites"
    # # print edgesDict
    # for i in range ( 0, len(edgesDict) ):
    #     x = edgesDict[i]
    #     pm.curve( p=[(x[0][0], 0, x[0][1]), (x[1][0], 0, x[1][1]) ], d= 1)
    # terrainPts = retrieveVertices(terrain[0])

    # tPointsDict ( terrainPts )

# def tPointsDict ( tPts ):
#     tPtsDict = {}
#     for i in range(0, len(tPts)):
#         tPtsDict[ (tPts[i][0], tPts[i][1]) ] = i
#
#     print tPtsDict
#     print len (tPtsDict)
#     print len (tPts)

def getEditPointsRiver2D(river):
    #better solution:
    #ignores Y value
    rEPs = pm.xform( str(river) + '.ep[*]', q=True, ws=True, t=True )
    # with Y
    #return zip(rEPs[0::3], rEPs[1::3], rEPs[2::3])
    # without Y
    return zip(rEPs[0::3], rEPs[2::3])

def getEditPointsRiver3D(river):
    rEPs = pm.xform( str(river) + '.ep[*]', q=True, ws=True, t=True )
    return np.array(zip(rEPs[0::3], rEPs[2::3]))

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
