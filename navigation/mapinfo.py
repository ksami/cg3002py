
import json
import urllib2
from math import sin, cos, degrees, atan2, sqrt, pi, radians, fabs
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

START_BUILDING = 1
REACH_NODE = 2
GO_FORWARD = 3
TURN = 4
STAIRS = 5
REACH_DEST_BUILDING = 6

ANGLE_THRESHOLD = 5
WALKING_ANGLE_THRESHOLD = 20
CORRIDOR_THRESHOLD = 273 / 2.0
DISTANCE_THRESHOLD = 100
NUM_STEPS_CHECK = 3

EXPECTED_ALTITUDE = 66.81762071
ALTITUDE_THRESHOLD = 0.3


# string constants
MODE = "MODE"
COORDX = "X"
COORDY = "Y"
ANGLE = "ANGLE"
CURRENT_NODE = "CURRENT_NODE"
LEFTORRIGHT = "LEFTORRIGHT"
DESTINATION = "DESTINATION"
NUMBER_NODES = "NUMBER_NODES"

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
		self.num_steps = 0

		# debug purpose
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
		#print "\n\n\n"

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

		for p in self.path:
			print self.mapList[p].getName(), "----"

	def giveCurrentCoordinates(self, nodeId):
		return (self.mapList[nodeId].getX(), self.mapList[nodeId].getY())

	def giveDirection (self, mode, distance, heading, altitude, coordX, coordY, numSteps):

		if(mode == START_BUILDING):
			self.current = 0
			coordX = self.mapList[self.path[self.current]].getX()
			coordY = self.mapList[self.path[self.current]].getY()
			return {MODE : mode , NUMBER_NODES : len(self.path), CURRENT_NODE : self.mapList[self.path[0]].getId() , COORDX : coordX, COORDY : coordY}

		elif(mode == REACH_NODE):

			# check the updated heading
			heading_angle = 90 - (heading + self.degree) % 360
			if(heading_angle < 0):
				heading_angle += 360

			startX = self.mapList[self.path[self.current]].getX()
			startY = self.mapList[self.path[self.current]].getY()
			endX = self.mapList[self.path[self.current+1]].getX()
			endY = self.mapList[self.path[self.current+1]].getY()

			edge_angle = atan2((endY - coordY),(endX - coordX))
			edge_angle = degrees(edge_angle)

			if(edge_angle < 0):
				edge_angle += 360

			diff_angle = fabs(edge_angle - heading_angle)
			if(diff_angle > 180):
				diff_angle = 360 - diff_angle

			if( diff_angle <= ANGLE_THRESHOLD):
				mode = GO_FORWARD
				return {MODE : mode, COORDX : coordX, COORDY : coordY, CURRENT_NODE : self.mapList[self.path[0]].getId()}
			else:
				mode = TURN
				turning = LEFT
				cross_vector = cos(radians(edge_angle)) * sin(radians(heading_angle)) - cos(radians(heading_angle)) * sin(radians(edge_angle))
				if(cross_vector > 0):
					turning = RIGHT

				return {MODE : mode, COORDX : coordX, COORDY : coordY, LEFTORRIGHT : turning, ANGLE: diff_angle, CURRENT_NODE : self.mapList[self.path[0]].getId()}

		elif(mode == GO_FORWARD):

			startX = self.mapList[self.path[self.current]].getX()
			startY = self.mapList[self.path[self.current]].getY()
			endX = self.mapList[self.path[self.current+1]].getX()
			endY = self.mapList[self.path[self.current+1]].getY()
			
			edge_angle = atan2((endY - startY),(endX - startX))
			edge_angle = degrees(edge_angle)

			if(edge_angle < 0):
				edge_angle += 360

			coordX += distance * cos(radians(edge_angle))
			coordY += distance * sin(radians(edge_angle))
			self.num_steps += numSteps

			if((endX - coordX)**2 + (endY - coordY)**2 >= DISTANCE_THRESHOLD**2):

				if(self.num_steps <= NUM_STEPS_CHECK):
					mode = GO_FORWARD
					return {MODE : mode, COORDX : coordX, COORDY : coordY}
				else:
					heading_angle = 90 - (heading + self.degree) % 360
					if(heading_angle < 0):
						heading_angle += 360

					diff_angle = fabs(edge_angle - heading_angle)
					if(diff_angle > 180):
						diff_angle = 360 - diff_angle

					if( diff_angle <= WALKING_ANGLE_THRESHOLD):
						self.num_steps = 0
						mode = GO_FORWARD
						return {MODE : mode, COORDX : coordX, COORDY : coordY}
					else:
						mode = TURN
						turning = LEFT
						cross_vector = cos(radians(edge_angle)) * sin(radians(heading_angle)) - cos(radians(heading_angle)) * sin(radians(edge_angle))
						if(cross_vector > 0):
							turning = RIGHT

						return {MODE : mode, COORDX : coordX, COORDY : coordY, LEFTORRIGHT : turning, ANGLE : diff_angle}

			else:	
				self.current += 1
				if(self.current == len(self.path) - 1):
					mode = REACH_DEST_BUILDING
					return {MODE : mode, COORDX : coordX, COORDY : coordY}
				else:
					mode = REACH_NODE
					return {MODE : mode, COORDX : coordX, COORDY : coordY, CURRENT_NODE : self.mapList[self.path[self.current]].getId()}

		elif(mode == STAIRS):
			if(fabs(altitude - EXPECTED_ALTITUDE) <= ALTITUDE_THRESHOLD ):
				mode = REACH_DEST_BUILDING
				return {MODE : mode , COORDX : coordX, COORDY : coordY}

			else:
				print "Altitude:", altitude
				return {MODE : mode, COORDX : coordX, COORDY : coordY}



	# def giveDirection (self, mode, distance, heading, coordX, coordY):

	# 	if(mode == TURN):

	# 		a = (heading + self.degree) % 360
	# 		heading_angle = 90 - a
	# 		if(heading_angle < 0):
	# 			heading_angle += 360

	# 		startX = self.mapList[self.path[self.current]].getX()
	# 		startY = self.mapList[self.path[self.current]].getY()
	# 		endX = self.mapList[self.path[self.current+1]].getX()
	# 		endY = self.mapList[self.path[self.current+1]].getY()

	# 		edge_angle = atan2((endY - startY),(endX - startX))
	# 		edge_angle = degrees(edge_angle)

	# 		if(edge_angle < 0):
	# 			edge_angle += 360

	# 		print "raw heading", heading, "heading_angle", heading_angle , "edge_angle", edge_angle

	# 		if( edge_angle - ANGLE_THRESHOLD <= heading_angle and heading_angle <= edge_angle + ANGLE_THRESHOLD):
	# 			mode = GO_FORWARD
	# 			print "Go forward"

	# 			return {MODE : mode, COORDX : coordX, COORDY : coordY}
				
	# 		else:
	# 			mode = TURN
	# 			turning = LEFT
	# 			cross_vector = cos(radians(edge_angle)) * sin(radians(heading_angle)) - cos(radians(heading_angle)) * sin(radians(edge_angle))
	# 			if(cross_vector > 0):
	# 				turning = RIGHT

	# 			return {MODE : mode, COORDX : coordX, COORDY : coordY, LEFTORRIGHT : turning}


	# 	elif(mode == GO_FORWARD):

	# 		startX = self.mapList[self.path[self.current]].getX()
	# 		startY = self.mapList[self.path[self.current]].getY()
	# 		endX = self.mapList[self.path[self.current+1]].getX()
	# 		endY = self.mapList[self.path[self.current+1]].getY()
			
	# 		edge_angle = atan2((endY - startY),(endX - startX))
	# 		edge_angle = degrees(edge_angle)

	# 		if(edge_angle < 0):
	# 			edge_angle += 360

	# 		coordX += distance * cos(radians(edge_angle))
	# 		coordY += distance * sin(radians(edge_angle))
	# 		self.total_x += distance * cos(radians(edge_angle))
	# 		self.total_y += distance * sin(radians(edge_angle))

	# 		# if(time.time() - self.tcoord >= 7):
	# 		# 	print "Edge angle", edge_angle
	# 		# 	print "current edge", self.current, "node X", endX, "node Y", endY
	# 		# 	print "total x", self.total_x, "total_y", self.total_y
	# 		# 	print "x", coordX, "y", coordY, "--- meters away", sqrt((endX - coordX)**2 + (endY - coordY)**2)
	# 		# 	self.tcoord = time.time()

	# 		# check if it is along the path

	# 		if((endX - coordX)**2 + (endY - coordY)**2 >= DISTANCE_THRESHOLD**2):
	# 			mode = GO_FORWARD
	# 			return {MODE : mode, COORDX : coordX, COORDY : coordY}
	# 		else:

	# 			self.current += 1
	# 			if(self.current == len(self.path) - 1):
	# 				mode = ARRIVE_DESTINATION
	# 				return {MODE : mode, COORDX : coordX, COORDY : coordY}
	# 			else:
	# 				mode = TURN

	# 				# check the updated 
	# 				a = (heading + self.degree) % 360
	# 				heading_angle = 90 - a
	# 				if(heading_angle < 0):
	# 					heading_angle += 360

	# 				startX = self.mapList[self.path[self.current]].getX()
	# 				startY = self.mapList[self.path[self.current]].getY()
	# 				endX = self.mapList[self.path[self.current+1]].getX()
	# 				endY = self.mapList[self.path[self.current+1]].getY()

	# 				edge_angle = atan2((endY - startY),(endX - startX))
	# 				edge_angle = degrees(edge_angle)

	# 				if(edge_angle < 0):
	# 					edge_angle += 360

	# 				if( edge_angle - ANGLE_THRESHOLD <= heading_angle and heading_angle <= edge_angle + ANGLE_THRESHOLD):
	# 					mode = GO_FORWARD

	# 					return {MODE : mode, COORDX : coordX, COORDY : coordY}
	# 				else:
	# 					mode = TURN
	# 					turning = LEFT
	# 					cross_vector = cos(radians(edge_angle)) * sin(radians(heading_angle)) - cos(radians(heading_angle)) * sin(radians(edge_angle))
	# 					if(cross_vector > 0):
	# 						turning = RIGHT

	# 					return {MODE : mode, COORDX : coordX, COORDY : coordY, LEFTORRIGHT : turning}


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












