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


if __name__ == "__main__":
	main()