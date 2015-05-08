from terrain import Terrain


class TerrainMain:

	def __init__ ( self ):
		#dict with the curve name as index
		self.terrain = []
		#the curve name will always be rCurve + index ( ie rCurve0 )
		self.rCurveName = 'rCurve'
		self.currentTerrain = None
		self.newTerrain()

	def newTerrain( self ):
		self.currentTerrain = Terrain( self.rCurveName + str(len(self.terrain)) )
		print self.currentTerrain.rCurveName
		self.terrain.append( self.currentTerrain )
		self.currentTerrain.createRiver ()

	def reloadModule( self ):
		import terrain
		reload( terrain )
		from terrain import Terrain

