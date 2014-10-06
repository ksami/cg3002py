# smwmap.py
# Fetches JSON map data

import urllib2
import json
from orientationinfo import OrientationInfo
from mapinfo import MapInfo
from wifiinfo import WifiInfo

# Strings
baseurl = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'
building = 'yimelo'
level = '5'
query = 'Building=' + building + '&' + 'Level=' + level
orienInfo = 0
mapInfo = 0
wifiInfo = 0

# Obtains map from the server and places it on the queue
# params: queue, building name, level
def obtainMap(mapqueue, bldg, lvl):
	building = bldg
	level = lvl
	response = urllib2.urlopen(baseurl + query)
	jsondata = response.read()
	orienInfo = OrientationInfo(jsondata)
	mapInfo = MapInfo(jsondata)
	wifiInfo = WifiInfo(jsondata)
	mapqueue.put(jsondata)

# For testing:
# Run in command line using
# python map.py
if __name__ == '__main__':
	response = urllib2.urlopen(baseurl + query)
	jsondata = response.read()
	nodes = json.loads(jsondata)
	mapInfo = MapInfo(jsondata)
	print mapInfo.shortestPath(15, 16)
	#print "\n\n\n"
	print mapInfo.shortestPathByCoordinates(450, 125, 16)
	#print "\n"
	print "You are off by", mapInfo.giveDirection(450, 125, 180)
	#print repr(nodes)

