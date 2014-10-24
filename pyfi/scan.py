#!/usr/bin/env python
import errno
import sys
import json

import pythonwifi.flags
from pythonwifi.iwlibs import Wireless

ifname = "wlan0"
filename = "wifinodes.json"


class WifiNodes:
    def __init__(self, ifname):
        self.nodes = {}
        self.wifi = Wireless(ifname)

    def addNode(self, mac, lvl, id=99):
        # if it already exists
        if id in self.nodes.keys():
            if mac in self.nodes[id].keys():
                if (lvl < self.nodes[id][mac]["min"]):
                    self.nodes[id][mac]["min"] = lvl
                if (lvl > self.nodes[id][mac]["max"]):
                    self.nodes[id][mac]["max"] = lvl
            else:
                self.nodes[id][mac] = {"min": lvl, "max": lvl}
        else:
            self.nodes[id] = {mac: {"min": lvl, "max": lvl}}

    def scan(self, id=99):
        try:
            results = self.wifi.scan()
        except IOError, (error_number, error_string):
            if error_number != errno.EPERM:
                sys.stderr.write(
                    "%-8.16s  Interface doesn't support scanning : %s\n\n" %
                    (self.wifi.ifname, error_string))
        else:
            if (len(results) == 0):
                print "%-8.16s  Interface doesn't have " % (self.wifi.ifname, ) + \
                      "a list of Peers/Access-Points"
            else:
                print "%-8.16s  Peers/Access-Points in range:"% (self.wifi.ifname, )
                for ap in results:
                    if (ap.quality.quality):
                        print "MAC: %s   Signal level: %s/%s" % \
                            (ap.bssid,
                            ap.quality.getSignallevel(),
                            "100")
                        self.addNode(ap.bssid, ap.quality.getSignallevel(), id)
                    else:
                        print "    %s, unable to get quality" % (ap.bssid, )


def main():
    results = WifiNodes(ifname)

    print "wifi scanning for ", ifname
    print "enter -1 for node id to write out results and exit"
    print "================================================================"

    while(True):
	try:
            id = int(raw_input("Enter node id: "))
            if id < 0:
                break
            results.scan(id)
	except Exception:
            print "exception, try again"

    # Write results to file
    print "writing results"
    with open(filename, "w") as outfile:
        json.dump(results.nodes, outfile, indent=4)


if __name__ == "__main__":
    main()
