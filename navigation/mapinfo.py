
import json
import urllib2
from math import sin, cos, degrees, atan2, sqrt, pi, radians
import sys
from nodeinfo import NodeInfo
from priodict import priorityDictionary
import time

MAP = 'map'
NODEID = 'nodeId'
X = 'x'
Y = 'y'
NODENAME = 'nodeName'
LINKTO = 'linkTo'

INFO = 'info'
NORTHAT = 'northAt'

LEFT = 0
RIGHT = 1

NODE = 0
GO_FORWARD = 1
TURN = 2
ARRIVE_DESTINATION = 3

ANGLE_THRESHOLD = 10
CORRIDOR_THRESHOLD = 273 / 2.0
DISTANCE_THRESHOLD = 150

# string constants
MODE = "MODE"
COORDX = "X"
COORDY = "Y"
LEFTORRIGHT = "LEFTORRIGHT"
DESTINATION = "DESTINATION"

baseurl = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'
building = 'COM1'
level = '2'
query = 'Building=' + building + '&' + 'Level=' + level

class MapInfo:

	def __init__ (self, jsonString):
		mapinfo = json.loads(jsonString)
		self.degree = int(mapinfo[INFO][NORTHAT])
		self.mapList = [] # list of nodes
		self.adjacencyList = {} # dictionary of rooms that is linked to the room in index i
		linkToList = []
		self.path = []
		self.current = 0
		self.size = 0
		self.tcoord = 0
		self.total_x = 0
		self.total_y = 0

		for node in mapinfo[MAP] :
			nodeinfo = NodeInfo(int(node[NODEID]), int(node[X]), int(node[Y]), node[NODENAME])	
			self.mapList.append(nodeinfo)
			
			linkList = []
			links = node[LINKTO].split(", ")
			for link in links:
				linkList.append(int(link))
			linkToList.append(linkList)

			self.size = self.size + 1

		for i in range(self.size):
			dic = {} # a dictionary with key "index" and value "their corresponding distances from node i"
			bigDic = {} # a dictionary with key i and value dic
			for index in linkToList[i]:
				distance = sqrt( (self.mapList[i].getX() - self.mapList[index-1].getX()) ** 2 +  (self.mapList[i].getY() - self.mapList[index-1].getY()) ** 2 ) 
				vertex = {(index-1): distance}
				dic.update(vertex)
			bigDic = {i: dic}
			self.adjacencyList.update(bigDic)

		#self.printSelf()

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

		start = start - 1
		end = end - 1
		final_distances,predecessors = Dijkstra(self.adjacencyList,start,end)
		while 1:
			self.path.append(end)
			if end == start: break
			end = predecessors[end]
		self.path.reverse()

		print self.path

		coordX = self.mapList[self.path[self.current]].getX()
		coordY = self.mapList[self.path[self.current]].getY()
		destination = self.mapList[self.size - 1].getName()

		return {COORDX : coordX, COORDY: coordY, DESTINATION: destination}

	def giveDirection (self, mode, distance, heading, coordX, coordY):

		if(mode == TURN):

			heading_angle = (heading + 225) % 360

			startX = self.mapList[self.path[self.current]].getX()
			startY = self.mapList[self.path[self.current]].getY()
			endX = self.mapList[self.path[self.current+1]].getX()
			endY = self.mapList[self.path[self.current+1]].getY()

			edge_angle = atan2((startY - endY),(startX - endX))
			edge_angle = degrees(edge_angle)

			if(edge_angle < 0):
				edge_angle += 360

			print "heading", heading_angle, "edge_angle", edge_angle

			if( edge_angle - ANGLE_THRESHOLD <= heading_angle and heading_angle <= edge_angle + ANGLE_THRESHOLD):
				mode = GO_FORWARD
				print "Go forward"

				return {MODE : mode, COORDX : coordX, COORDY : coordY}
				
			else:
				mode = TURN
				turning = LEFT
				cross_vector = cos(radians(edge_angle)) * sin(radians(heading_angle)) - cos(radians(heading_angle)) * sin(radians(edge_angle))
				if(cross_vector < 0):
					turning = RIGHT

				return {MODE : mode, COORDX : coordX, COORDY : coordY, LEFTORRIGHT : turning}


		elif(mode == GO_FORWARD):
			# update coordinates
			#heading_angle = (heading + 225) % 360

			startX = self.mapList[self.path[self.current]].getX()
			startY = self.mapList[self.path[self.current]].getY()
			endX = self.mapList[self.path[self.current+1]].getX()
			endY = self.mapList[self.path[self.current+1]].getY()
			
			angle = atan2((endY - startY),(endX - startX))
			angle = degrees(edge_angle)

			if(angle < 0):
				angle += 360

			coordX += distance * cos(radians(angle))
			coordY += distance * sin(radians(angle))
			self.total_x += distance * cos(radians(angle))
			self.total_y += distance * sin(radians(angle))

			if(time.time() - self.tcoord >= 7):
				print "Edge angle", angle
				print "current edge", self.current, "node X", endX, "node Y", endY
				print "total x", self.total_x, "total_y", self.total_y
				print "x", coordX, "y", coordY, "--- meters away", sqrt((endX - coordX)**2 + (endY - coordY)**2)
				self.tcoord = time.time()

			# check if it is along the path			
			#if(sqrt((endX - coordX)**2 + (endY - coordY)**2) >= DISTANCE_THRESHOLD):
			if((endX - coordX)**2 + (endY - coordY)**2 >= DISTANCE_THRESHOLD**2):
				mode = GO_FORWARD
				return {MODE : mode, COORDX : coordX, COORDY : coordY}
			else:
				self.current += 1
				if(self.current == len(self.path) - 1):
					mode = ARRIVE_DESTINATION
					return {MODE : mode, COORDX : coordX, COORDY : coordY}
				else:
					mode = TURN

					# check the updated 
					heading_angle = (heading + 225) % 360

					startX = self.mapList[self.path[self.current]].getX()
					startY = self.mapList[self.path[self.current]].getY()
					endX = self.mapList[self.path[self.current+1]].getX()
					endY = self.mapList[self.path[self.current+1]].getY()

					edge_angle = atan2((startY - endY),(startX - endX))
					edge_angle = degrees(edge_angle)

					if(edge_angle < 0):
						edge_angle += 360

					#coordX = startX
					#coordY = startY

					if( edge_angle - ANGLE_THRESHOLD <= heading_angle and heading_angle <= edge_angle + ANGLE_THRESHOLD):
						mode = GO_FORWARD
						print "Go forward"

						return {MODE : mode, COORDX : coordX, COORDY : coordY}
					else:
						mode = TURN
						turning = LEFT
						cross_vector = cos(radians(edge_angle)) * sin(radians(heading_angle)) - cos(radians(heading_angle)) * sin(radians(edge_angle))
						if(cross_vector < 0):
							turning = RIGHT

						return {MODE : mode, COORDX : coordX, COORDY : coordY, LEFTORRIGHT : turning}


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

if __name__ == "__main__":
    response = urllib2.urlopen(baseurl + query)
    jsondata = response.read()
    mapinfo = MapInfo(jsondata)
    print mapinfo.shortestPath(1, 12)
    print mapinfo.giveDirection(TURN, 0, 90, 0, 1260)













