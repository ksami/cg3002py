from mapinfo import MapInfo

# constants for map
cached_map = ["com1lvl2.json", "com2lvl2.json", "com2lvl3.json"]

NODE_ID_0_1 = 31
NODE_ID_1_0 = 1
NODE_ID_1_2 = 16
NODE_ID_2_1 = 10

NODE_BETWEEN_BUILDINGS = [[0, NODE_ID_0_1, 0], [NODE_ID_1_0, 0, NODE_ID_1_2], [0, NODE_ID_2_1, 0]]

# dictionary keys
MODE = "MODE"
COORDX = "X"
COORDY = "Y"
ANGLE = "ANGLE"
NODE_NAME = "NODE_NAME"
LEFTORRIGHT = "LEFTORRIGHT"
DESTINATION = "DESTINATION"
NUMBER_OF_BUILDINGS = "NUMBER_OF_BUILDINGS"
CURRENT_BUILDING = "CURRENT_BUILDING"

# turning directions
LEFT = 0
RIGHT = 1

# state machine modes
START_JOURNEY = 0
START_BUILDING = 1
REACH_NODE = 2
GO_FORWARD = 3
TURN = 4
REACH_DEST_BUILDING = 5
ARRIVE_DESTINATION = 6

class MapInfoList:

	def __init__(self):

		# download three maps:
		self.mapinfoList = []
		self.currentBuilding = 0
		self.mode = START_BUILDING
		
		for i in range(3) :
			with open(cached_map[i], "r") as f:
				lines = f.readlines()
				jsondata = "".join(lines)
			mapinfo = MapInfo(jsondata)
			self.mapinfoList.append(mapinfo)

	def shortestPath(self, startBuilding, startLevel, startNode, endBuilding, endLevel, endNode):

		self.startMap = 0   	
		self.endMap = 2

		if(startBuilding == 2 and startLevel == 2):
			self.startMap = 1
		elif(startBuilding == 2 and startLevel == 3):
			self.startMap = 2

		if(endBuilding == 1 and endLevel == 2):
			self.endMap = 0
		elif(endBuilding == 2 and endLevel == 2):
			self.endMap = 1

		start = []
		end = []
		self.building = []    	

		index = self.startMap
		direction = 1
		if(self.startMap > self.endMap):
			direction = -1

		start.append(startNode)	
		self.building.append(index)

		while(index != self.endMap):
			end.append(NODE_BETWEEN_BUILDINGS[index][index+direction])
			start.append(NODE_BETWEEN_BUILDINGS[index+direction][index])
			self.building.append(index+direction)
			index += direction
		end.append(endNode)

		for i in range(len(start)):
			print building[i]
			self.mapinfoList[building[i]].shortestPath(start[i], end[i])

	def giveDirection (self, distance, heading, coordX, coordY, numSteps):

		if(self.mode == START_JOURNEY):
			self.mode = START_BUILDING
			return {MODE : START_JOURNEY, NUMBER_OF_BUILDINGS : len(self.building)}

		else:
			result = self.mapinfoList[self.building[self.currentBuilding]].giveDirection(self.mode, distance, heading, coordX, coordY, numSteps)
			if(result[MODE] != TURN):
				self.mode = result[MODE]

			if(self.mode == START_BUILDING):
				self.mode = REACH_NODE
				result.append({CURRENT_BUILDING : self.building[self.currentBuilding]})
				return result

			elif(self.mode == REACH_DEST_BUILDING):

				if(self.currentBuilding == len(self.building) - 1):
					self.mode = ARRIVE_DESTINATION
					for key in result.keys():
        				if key == MODE:
            				result[key] = ARRIVE_DESTINATION
					return result

				else:
					self.currentBuilding += 1
					self.mode = START_BUILDING
					return result

			else:
				return result		

if __name__ == "__main__":
	mapi = MapInfoList()
	mapi.shortestPath(2, 3, 1, 1, 2, 12)


