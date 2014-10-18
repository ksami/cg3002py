import time

def work(q_frommain, q_tomain, x):
	isKill = False

	while isKill == False:
		try:
			for i in xrange(1,x*10000000):
				pass
			q_tomain.put("process " + str(x))
			isKill = q_frommain.get(block=False)

		#Queue.Empty
		except Exception:
			pass

		#Ctrl-C
		except KeyboardInterrupt:
			isKill = True

	print "process " + str(x) + " exiting"