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
    rEPs = getEditPointsRiver2D ( river )
    rEPs.append((-100,-100))
    rEPs.append((100,-100))
    rEPs.append((-100,100))
    rEPs.append((100,100))
    rEPs.append((-1000,-1000))
    rEPs.append((1000,-1000))
    rEPs.append((-1000,1000))
    rEPs.append((1000,1000))
    rEPs.append((-10000,-10000))
    rEPs.append((10000,-10000))
    rEPs.append((-10000,10000))
    rEPs.append((10000,10000))
    print rEPs
    # calc voronoi
    points = []
    for i in range ( 0, len(rEPs) ):
        point =  Point(rEPs[i][0], rEPs[i][1] )
        points.append ( Point(rEPs[i][0], rEPs[i][1] ) )
    vorPoints = vo.computeVoronoiDiagram(points)
    print vorPoints[2]
    print vorPoints[0]
    vorVertices = vorPoints[0]
    vorIndex = vorPoints[2]
    edgesDict = {}
    for i in range ( 0, len(vorIndex) ):
        # if vorIndex[i][1] == -1 or vorIndex[i][2] == -1 :
        edgesDict[ vorIndex[i][0] ] = ( [ vorVertices[ vorIndex[i][1] ],  vorVertices[ vorIndex[i][2] ] ] )
        # else:
        #     print "i found infinites"
    # print edgesDict
    for i in range ( 0, len(edgesDict) ):
        x = edgesDict[i]
        pm.curve( p=[(x[0][0], 0, x[0][1]), (x[1][0], 0, x[1][1]) ], d= 1)
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

    #not so good solution, the lines above do the same
    #selec river CVs and save their names in an array
    # pm.select ( (river + ".cv[*]"), r = True );
    # cvNames = pm.ls ( sl=True, fl=True );
    # # print cv
    # # clear select
    # pm.select ( cl=True );
    # #cvNames[0] contains rCurveShape1.cv[0]
    # rCVs = []
    # # retrieve all Curve CVs points
    # for i in range ( 0, len(cvNames) ):
    #     rCVs.append ( pm.xform( cvNames[i], q=True, ws=True, t=True) )
    # return rCVs

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
