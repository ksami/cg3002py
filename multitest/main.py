# multiprocessing test

import multiprocessing
import time

import worker

def createProcess(function, args=()):
	return multiprocessing.Process(target=function, args=args)

def createQueue():
	return multiprocessing.Queue()

def main():
	q_frommain = createQueue()
	q_tomain = createQueue()

	worker1 = createProcess(worker.work, args=(q_frommain, q_tomain, 1))
	worker2 = createProcess(worker.work, args=(q_frommain, q_tomain, 2))
	worker3 = createProcess(worker.work, args=(q_frommain, q_tomain, 3))

	try:
		worker1.start()
		worker2.start()
		worker3.start()

		while True:
			msg = q_tomain.get()
			print msg

	except KeyboardInterrupt:
		q_frommain.put(True)

		worker1.join()
		worker2.join()
		worker3.join()


# Parses a string from the output of speechtotext into int
def strToInt(input):
	outputList = []

	# "1 2 3(2)" into ["1", "2", "3(2)"]
	inputList = input.split()

	# ["1", "2", "3(2)"] into ["1", "2", "3"]
	for i in xrange(0, len(inputList)):
		# ignore ()
		outputList.append(inputList[i][0])

	# ["1", "2", "3"] into "123"
	output = "".join(outputList)

	# "123" into 123
	return int(output)


def timer():
	q_timer = createQueue()
	timer = createProcess(function=worker.timer, args=(q_timer, 5))
	timer.start()

	while True:
		try:
			msg = q_timer.get(block=False)
			if msg != None:
				print "type:",type(msg)
				print "msg:",msg
				if msg == 5:
					print "done"
					break
		except Exception, e:
			print "exception: ", e



if __name__ == "__main__":
	#main()
	#ret = strToInt("1 2 3(2)")
	#print ret
	timer()