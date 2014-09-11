
import json
from nodeinfo import NodeInfo

MAP = 'map'
NODEID = 'nodeId'
X = 'x'
Y = 'y'
NODENAME = 'nodeName'
LINKTO = 'linkTo'

class MapInfo:

	def __init__ (self, jsonString):
		mapinfo = json.loads(jsonString)
		self.mapList = [] # list of nodes
		self.linkLists = [[]] #list of rooms that is linked to the room in index i
		
		for node in mapinfo[MAP] :
			nodeinfo = NodeInfo(int(node[NODEID]), int(node[X]), int(node[Y]), node[NODENAME])	
			self.mapList.append(nodeinfo)
			
			linkList = []
			links = node[LINKTO].split(", ")
			for link in links:
				linkList.append(int(link))
			self.linkLists.append(linkList)


	def getNode(self, index):
		for maps in self.mapList:
			if (maps.getId() == index):
				return maps

	def getListOfNodes(self):
		return self.mapList

	def getLinkLists(self):
		return self.linkLists

	def printSelf(self):
		print "map\n"
		for node in self.mapList:
			print str(node.getId()) + " " + str(node.getX()) + " " + str(node.getY()) + " " + node.getName() + "\n"
		print"---------\n\n"

		print "linkto\n\n"
		i = 0;
		for linkList in self.linkLists:
			print str(i) + " --- "
			for link in linkList:
				print str(link) + ", "
			print "\n"
			i = i + 1
