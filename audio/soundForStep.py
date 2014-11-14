import sys,os,multiprocessing,time

def stepTicker(q_stepTicker, q_kill):
	while True:
		#check for terminate
		try:
			kill = q_kill.get(block=False)
			if kill == 1:
				break
		# Queue.empty
		except Exception:
			#ignore
			pass

		try:
			step = q_stepTicker.get(block=False)
			if step == 1:
				os.system("aplay losticks.wav")
		except Exception:
			#ignore
			pass

if __name__ == "__main__":
	q_test = multiprocessing.Queue()
	q_kill = multiprocessing.Queue()
	p= multiprocessing.Process(target=stepTicker, args=(q_test, q_kill))
	p.start()
	print("After Calling stepTicker")
	for x in xrange(0,10):
		print("In for loop")
		time.sleep(1)
		q_test.put(1)

	q_kill.put(1)