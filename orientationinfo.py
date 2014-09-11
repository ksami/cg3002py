import json

class OrientationInfo:

	INFO = 'info'
	NORTHAT = 'northAt'

	def __init__(self, jsonString):
		orientinfo = json.loads(jsonString)
		self.degree = int(orientinfo['info']['northAt'])

	def getDegree(self):
		return self.degree

	def printSelf(self):
		print "\n\nnorthAt : " + str(self.degree) + "\n"