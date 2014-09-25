# Timer.py

import time

# Raises a flag when x seconds are up
# params: num of seconds
def alarm(x):
	time.sleep(x)
	print "timer up!!"

# For testing:
# Run in command line using
# python timer.py 3
if __name__ == '__main__':
	import sys
	seconds = int(sys.argv[1])
	time.sleep(seconds)

	print "timer up!"

