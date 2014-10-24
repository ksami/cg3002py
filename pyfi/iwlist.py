#!/usr/bin/env python
# Copyright 2004, 2005 Roman Joost <roman@bromeco.de> - Rotterdam, Netherlands
# Copyright 2009 by Sean Robinson <seankrobinson@gmail.com>
#
# This file is part of Python WiFi
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import errno
import sys
import types

import pythonwifi.flags
from pythonwifi.iwlibs import Wireless, Iwrange, getNICnames


##########################################################################
def print_aps(wifi, args=None):
    """ Print the access points detected nearby.

        iwlist.c uses the deprecated SIOCGIWAPLIST, but iwlist.py uses
        regular scanning (i.e. Wireless.scan()).

    """
    # "Check if the interface could support scanning"
    try:
        iwrange = Iwrange(wifi.ifname)
    except IOError, (error_number, error_string):
        sys.stderr.write("%-8.16s  Interface doesn't support scanning.\n\n" % (
                            wifi.ifname))
    else:
        # "Check for Active Scan (scan with specific essid)"
        # "Check for last scan result (do not trigger scan)"
        # "Initiate Scanning"
        try:
            results = wifi.scan()
        except IOError, (error_number, error_string):
            if error_number != errno.EPERM:
                sys.stderr.write(
                    "%-8.16s  Interface doesn't support scanning : %s\n\n" %
                    (wifi.ifname, error_string))
        else:
            if (len(results) == 0):
                print "%-8.16s  Interface doesn't have " % (wifi.ifname, ) + \
                      "a list of Peers/Access-Points"
            else:
                print "%-8.16s  Peers/Access-Points in range:"% (wifi.ifname, )
                for ap in results:
                    if (ap.quality.quality):
                        if (ap.quality.updated & \
                                    pythonwifi.flags.IW_QUAL_QUAL_UPDATED):
                            quality_updated = "="
                        else:
                            quality_updated = ":"
                        if (ap.quality.updated & \
                                    pythonwifi.flags.IW_QUAL_LEVEL_UPDATED):
                            signal_updated = "="
                        else:
                            signal_updated = ":"
                        if (ap.quality.updated & \
                                    pythonwifi.flags.IW_QUAL_NOISE_UPDATED):
                            noise_updated = "="
                        else:
                            noise_updated = ":"
                        print "    %s : Quality%c%s/%s  Signal level%c%s/%s  Noise level%c%s/%s" % \
                            (ap.bssid,
                            quality_updated,
                            ap.quality.quality,
                            wifi.getQualityMax().quality,
                            signal_updated,
                            ap.quality.getSignallevel(),
                            "100",
                            noise_updated,
                            ap.quality.getNoiselevel(),
                            "100")
                    else:
                        print "    %s" % (ap.bssid, )
                print


##################################################################################
ifname = "wlan0"

if __name__ == "__main__":
    wifi = Wireless(ifname)
    print_aps(wifi)

