import numpy as np
import math as math
import random
from scipy.spatial import Voronoi as vp
import pymel.core as pm
import voronoi as vo
from collections import defaultdict
from region import Region


class Terrain:

    def __init__( self, name ):
        self.regions={}
        self.adjVertices = defaultdict( list )
        self.rCurveName = name
        self.vertices = None
        self.vertices3d = None

    def createRiver( self ):
        initialPoint = [0, 0, 0]
        river = pm.curve( n=self.rCurveName, p=[initialPoint] )
        self.addPointsToRiver(river)

    def addPointsToRiver( self, river ):
        ctxName = "CurveAddPtCtx"
        pm.select( river , r=True )
        if pm.contextInfo(ctxName, ex=True) is False:
            ctx = pm.curveAddPtCtx("CurveAddPtCtx")
            print ctx
        else:
            ctx = ctxName
        pm.setToolTo(ctx)

    def computeRiverAltitude( self, angle=0.05 ):
        #default angle is 1 degree

        #generate a random value from 0 to angle
        rAngle = np.random.uniform( 0, angle, len(self.regions) )
        # print 'angle ' + str(rAngle)
        tY = 0 #tY is the total sum of y 
        eY = 0
        #for from second point to last
        for i in range( 1, len(self.regions) ):
            dist = np.linalg.norm(self.regions[i].point - self.regions[i-1].point)
            # print 'dist ' + str(dist)
            eY = (dist/2)*np.tan(rAngle[i]) + tY
            tY += dist*np.tan(rAngle[i])
            self.regions[i].setEPAltitude( tY )
            self.regions[i-1].setNextEdgeAltitude( eY )
            # print y

    def computeTerrain( self ):

        rEPs = np.array( self.getEditPointsRiver2D ( ) )
        #add limit to map to avoid infinity values
        rPoints = self.computeBoundary(rEPs)

        # print rEPs
        # pm.curve( d=1, p=getEditPointsRiver3D ( river ) )

        vorPoints_np = vp(rPoints)

        self.vertices = vorPoints_np.vertices

        #remove all infinites values
        vorRegions = self.removeNegatives ( vorPoints_np.regions )

        #create a dict with all the region Objects
        self.createRegionObjects( vorRegions, rEPs )

        #vertex X is shared by N faces
        self.computeAdjacentVertices( )

        # computeAdjEdges ( adjVertices )
        self.computeRegionBoundary(  )

        self.computeRiverAltitude( 0.1 )

        self.generateTerrain( )

        # self.draw3dRiver( )

    # def computeAdjEdges ( adjVertices ):
    #     print adjVertices
    #     for key, value in adjVertices.items():
    #         if len( value ) > 1:
    #             if 

    def generateTerrain( self ):

        self.vertices3d = []

        #insert zeros to Y values
        for i in range( 0, len( self.vertices ) ):
            tv = self.vertices[i]
            tv = np.insert( tv, 1, 0.0 )
            self.vertices3d.append( tv )


        for region in self.regions.values():
            for vertexIndex in region.regionI:
                if region.nextEdge is not None:
                    if vertexIndex in region.nextEdge:
                        #sum Y value to vertex
                        yDist = region.nextEdgeY - self.vertices3d[vertexIndex][1]
                        self.vertices3d[vertexIndex][1] = yDist

        for v in self.vertices3d:
            print v


        vorFaces = []
        faceNames = []
        for region in self.regions.values():
            tempFace = []
            # print region.regionI
            for vertex in region.regionI:
                npVertex = self.vertices3d[vertex]
                tempFace.append(npVertex)
            # print tempFace
            vorFaces.append(tempFace)
            faceNames.append( pm.polyCreateFacet( n='terrainPlane', p=tempFace )[0] )
        pm.group( faceNames, n='terrain')


    def computeRegionBoundary( self ):

        for i in range( 0, len(self.regions) ):
            rI = self.regions[i].regionI
            for j in range ( i+1, len(self.regions) ):
                rJ = self.regions[j].regionI
                # print 'comparing ' + str(rI) + ' with ' + str(rJ)
                edge = self.intersect(rI, rJ)
                if  edge is not None:
                    if self.regions[i].id == self.regions[j].id-1:
                        self.regions[i].setBoundary(edge)
                        continue


    def createRegionObjects ( self, rIndeces, rEPs ):
        regionVertices = self.indexToVertex( self.vertices, rIndeces )
        # print len(regionVertices)
        for region, regionIndex in zip(regionVertices, rIndeces):
            for i in range(0, len(rEPs)):
                if self.pointInRegion ( rEPs[i], region ):
                    self.regions[i] = Region( i, rEPs[i], regionIndex )
                    continue

    #receives Region indeces
    #returns Region with vertices values
    def indexToVertex( self, vorVertices, vorRegions ):
        regionVertices = []
        for region in vorRegions:
            # print region
            rVertices = []
            for vIndex in region:
                rVertices.append( vorVertices[vIndex].tolist() )
            regionVertices.append( rVertices )
        return regionVertices


    #check if point is inside region
    def pointInRegion( self, point, region ):
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

    def intersect( self, a, b):
        result = list(set(a) & set(b))
        if not result:
            return None
        else:
            return result


    def checkPointsInList( self, pointArray, p1, p2 ):
        if p1 in pointArray:
            if p2 in pointArray:
                return True
            else:
                return False

    def removeNegatives( self, listPoints ):
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

    def removeNegativeRidges( self, listPoints ):
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
    
    def computeBoundary( self, rEPs ):
        tEPs = np.absolute(rEPs)
        xmax, zmax = abs(tEPs.max(axis=0))
        boundary = max( xmax, zmax ) * 2
        # print boundary
        rEPs = np.append(rEPs, [[-boundary,-boundary]], axis=0)
        rEPs = np.append(rEPs, [[boundary,-boundary]], axis=0)
        rEPs = np.append(rEPs, [[-boundary,boundary]], axis=0)
        rEPs = np.append(rEPs, [[boundary,boundary]], axis=0)

        return rEPs

    def computeAdjacentVertices( self ):
        for key, region in self.regions.items():
            for vertex in region.regionI:
                self.adjVertices[vertex].append (key)

    def getEditPointsRiver2D( self ):
        #ignores Y value
        rEPs = pm.xform( str(self.rCurveName) + '.ep[*]', q=True, ws=True, t=True )
        # with Y
        #return zip(rEPs[0::3], rEPs[1::3], rEPs[2::3])
        # without Y
        return zip(rEPs[0::3], rEPs[2::3])

    def getCVRiver3D( self ):
        rEPs = pm.xform( str( self.rCurveName ) + '.cv[*]', q=True, ws=True, t=True )
        return zip(rEPs[0::3], rEPs[1::3], rEPs[2::3])

    def getEditPointsRiver3D( self ):
        rEPs = pm.xform( str(self.rCurveName) + '.ep[*]', q=True, ws=True, t=True )
        return zip(rEPs[0::3], rEPs[1::3], rEPs[2::3])

    def retrieveVertices( self ):
        #get points
        xOrig = pm.xform(str(self.rCurveName) + '.vtx[*]', q=True, ws=True, t=True)
        return zip(xOrig[0::3], xOrig[1::3], xOrig[2::3])

    def draw3dRiver( self ):
        riverPoints3D = []
        for region in self.regions.values():
            tP = region.point
            tP = np.insert(tP, 1, region.pointY)
            riverPoints3D.append( tP )
        print riverPoints3D
        river = pm.curve( n='rCurve3D', p=riverPoints3D )