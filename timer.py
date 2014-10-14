# Timer.py

import time

# Raises a flag when x seconds are up
# params: num of seconds
def alarm(x):
	try:
		time.sleep(x)
		print "timer up!!"
	except KeyboardInterrupt:
		#Ctrl-C
		pass

# Puts x onto queue q once x seconds are up
# params: queue, num of seconds
def timer(q, x):
	try:
		time.sleep(x)
		q.put(x)
	except KeyboardInterrupt:
		#Ctrl-C
		pass

# For testing:
# Run in command line using
# python timer.py 3
if __name__ == '__main__':
	import sys
	seconds = int(sys.argv[1])

	try:
		time.sleep(seconds)
		print "timer up!"
	except KeyboardInterrupt:
		#Ctrl-C
		print "interrupted"
