import json
from wifinodeinfo import WifiNodeInfo

WIFI = 'wifi'
NODEID = 'nodeId'
X = 'x'
Y = 'y'
NODENAME = 'nodeName'
MACADDR = 'macAddr'

class WifiInfo:

	def __init__ (self, jsonString):
		wifiinfo = json.loads(jsonString)
		self.wifiList = []
		for node in wifiinfo[WIFI] :
			wifinode = WifiNodeInfo(int(node[NODEID]), int(node[X]), int(node[Y]), node[NODENAME], node[MACADDR])	
			self.wifiList.append(wifinode)


	def getNode(self, index):
		for wifi in self.wifiList:
			if (wifi.getId() == index):
				return maps

	def getWifiNodes(self):
		return self.wifiList

	def printSelf(self):
		print 'wifi\n'
		for wifi in self.wifiList:
			print str(wifi.getId()) + " " + str(wifi.getX()) + " " + str(wifi.getY()) + " " + wifi.getName() + " " + wifi.getMacAddress() + "\n"
		print "-----\n"
