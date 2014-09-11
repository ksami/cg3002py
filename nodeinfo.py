
class NodeInfo:

	def __init__ (self, nodeId, coordX, coordY, nodeName):
		self.nodeId = nodeId
		self.coordX = coordX
		self.coordY = coordY
		self.nodeName = nodeName

	def getId(self):
		return self.nodeId

	def getX(self):
		return self.coordX

	def getY(self):
		return self.coordY

	def getName(self):
		return self.nodeName
