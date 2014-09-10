# smwmap.py
# Fetches JSON map data

import urllib2
import json

# Strings
baseurl = 'http://showmyway.comp.nus.edu.sg/getMapInfo.php?'
building = 'DemoBuilding'
level = '1'
query = 'Building=' + building + '&' + 'Level=' + level

# Obtains map from the server and places it on the queue
# params: queue, building name, level
def obtainMap(mapqueue, bldg, lvl):
	building = bldg
	level = lvl
	response = urllib2.urlopen(baseurl + query)
	jsondata = response.read()
	mapinfo = json.loads(jsondata)
	mapqueue.put(mapinfo)

# For testing:
# Run in command line using
# python map.py
if __name__ == '__main__':
	response = urllib2.urlopen(baseurl + query)
	jsondata = response.read()
	nodes = json.loads(jsondata)
	print repr(nodes)