
import json
import math
import sys
from nodeinfo import NodeInfo
from priodict import priorityDictionary

MAP = 'map'
NODEID = 'nodeId'
X = 'x'
Y = 'y'
NODENAME = 'nodeName'
LINKTO = 'linkTo'

INFO = 'info'
NORTHAT = 'northAt'

class MapInfo:

	def __init__ (self, jsonString):
		mapinfo = json.loads(jsonString)
		self.degree = int(mapinfo[INFO][NORTHAT])
		self.mapList = [] # list of nodes
		self.adjacencyList = {} # dictionary of rooms that is linked to the room in index i
		linkToList = []
		self.size = 0

		for node in mapinfo[MAP] :
			nodeinfo = NodeInfo(int(node[NODEID]), int(node[X]), int(node[Y]), node[NODENAME])	
			self.mapList.append(nodeinfo)
			
			linkList = []
			links = node[LINKTO].split(",")
			for link in links:
				linkList.append(int(link))
			linkToList.append(linkList)

			self.size = self.size + 1

		for i in range(self.size):
			dic = {} # a dictionary with key "index" and value "their corresponding distances from node i"
			bigDic = {} # a dictionary with key i and value dic
			for index in linkToList[i]:
				distance = math.sqrt( (self.mapList[i].getX() - self.mapList[index-1].getX()) ** 2 +  (self.mapList[i].getY() - self.mapList[index-1].getY()) ** 2 ) 
				vertex = {(index-1): distance}
				dic.update(vertex)
			bigDic = {i: dic}
			self.adjacencyList.update(bigDic)

		self.printSelf()

	def printSelf(self):
		print "-\n-------map------\n"
		for i in range(self.size):
			node = self.mapList[i]
			print str(node.getId()) , str(node.getX()) , str(node.getY()) , node.getName()

		print "\n"

		for i in self.adjacencyList.keys():
			print str(i) , "---------------"
			for key, value in self.adjacencyList[i].items():
				print str(key) , str(value)

		print "linkto\n\n"

	def shortestPath(self, start, end):
		"""
		Find a single shortest path from the given start vertex
		to the given end vertex.
		The input has the same conventions as Dijkstra().
		The output is a list of the vertices in order along
		the shortest path.
		"""
		start = start - 1
		end = end - 1
		self.current = 0
		final_distances,predecessors = Dijkstra(self.adjacencyList,start,end)
		self.path = []
		while 1:
			self.path.append(end)
			if end == start: break
			end = predecessors[end]
		self.path.reverse()

		# just for debugging purposes
		nodeList = []
		for p in path:
			nodeList.append(self.mapList[p].getId())

		for i in range(len(path)-1):
			print self.mapList[path[i]].getId(), self.mapList[path[i]].getName(), "---TO---", self.mapList[path[i+1]].getId(), self.mapList[path[i+1]].getName()

		print "\n"

		return nodeList

	def shortestPathByCoordinates(self, coordX, coordY, endID):

		minimumDist = sys.maxint
		minimumNodeID = 0

		for mapItem in self.mapList:
			distance = math.sqrt( (mapItem.getX() - coordX)**2 +  (mapItem.getY() - coordY)**2)
			if(distance < minimumDist):
				minimumDist = distance
				minimumNodeID = mapItem.getId()

		return self.shortestPath(minimumNodeID, endID)

	def giveDirection (self, coordX, coordY, heading):

		while(self.current <= len(self.path) - 1):
	
			startX = self.maplist[self.path[self.current]].getX()
			startY = self.maplist[self.path[self.current]].getY()

			endX = self.maplist[self.path[self.current+1]].getX()
			endY = self.maplist[self.path[self.current+1]].getY()			

			#checking if that coordinates is along that edge
			# need checking on that condition
			if(  (startX <= coordX <= endX) and (startY <= coordY <= endY) ):
				break

			self.current += 1

		if(self.current == len(self.path) - 1):
			#reach destination
			return 0

		angle = math.atan2((endY - startY),(endX - startX))
		if(angle < 0):
			angle += 2*math.pi

		return math.degrees(angle) + 90 - (heading + self.degree) 


def Dijkstra(graph,start,end=None):
		"""
		Find shortest paths from the start vertex to all
		vertices nearer than or equal to the end.

		The input graph G is assumed to have the following
		representation: A vertex can be any object that can
		be used as an index into a dictionary.  G is a
		dictionary, indexed by vertices.  For any vertex v,
		G[v] is itself a dictionary, indexed by the neighbors
		of v.  For any edge v->w, G[v][w] is the length of
		the edge.  This is related to the representation in
		<http://www.python.org/doc/essays/graphs.html>
		where Guido van Rossum suggests representing graphs
		as dictionaries mapping vertices to lists of neighbors,
		however dictionaries of edges have many advantages
		over lists: they can store extra information (here,
		the lengths), they support fast existence tests,
		and they allow easy modification of the graph by edge
		insertion and removal.  Such modifications are not
		needed here but are important in other graph algorithms.
		Since dictionaries obey iterator protocol, a graph
		represented as described here could be handed without
		modification to an algorithm using Guido's representation.

		Of course, G and G[v] need not be Python dict objects;
		they can be any other object that obeys dict protocol,
		for instance a wrapper in which vertices are URLs
		and a call to G[v] loads the web page and finds its links.

		The output is a pair (D,P) where D[v] is the distance
		from start to v and P[v] is the predecessor of v along
		the shortest path from s to v.

		Dijkstra's algorithm is only guaranteed to work correctly
		when all edge lengths are positive. This code does not
		verify this property for all edges (only the edges seen
	 	before the end vertex is reached), but will correctly
		compute shortest paths even for some graphs with negative
		edges, and will raise an exception if it discovers that
		a negative edge has caused it to make a mistake.
		"""

		final_distances = {}	# dictionary of final distances
		predecessors = {}	# dictionary of predecessors
		estimated_distances = priorityDictionary()   # est.dist. of non-final vert.
		estimated_distances[start] = 0

		for vertex in estimated_distances:
			final_distances[vertex] = estimated_distances[vertex]
			if vertex == end: break

			for edge in graph[vertex]:
				path_distance = final_distances[vertex] + graph[vertex][edge]
				if edge in final_distances:
					if path_distance < final_distances[edge]:
						raise ValueError, \
	  "Dijkstra: found better path to already-final vertex"
				elif edge not in estimated_distances or path_distance < estimated_distances[edge]:
					estimated_distances[edge] = path_distance
					predecessors[edge] = vertex

		return (final_distances,predecessors)