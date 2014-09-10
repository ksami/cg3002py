import time

# Raises a flag when x seconds are up
# params: queue, num of seconds
def xseconds(q,x):
	time.sleep(x)
	q.put("timer up!!")

# For testing:
# Run in command line using
# python timer.py 3
if __name__ == '__main__':
	import sys
	seconds = int(sys.argv[1])
	time.sleep(seconds)

	print "timer up!"

