# Timer.py

import time

# Raises a flag when x seconds are up
# params: queue, num of seconds
def xseconds(timequeue,x):
	time.sleep(x)
	timequeue.put("timer up!!")

# For testing:
# Run in command line using
# python timer.py 3
if __name__ == '__main__':
	import sys
	seconds = int(sys.argv[1])
	time.sleep(seconds)

	print "timer up!"

