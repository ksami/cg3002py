# Main file handling multiple processes

import multiprocessing
import time
import proc
import timer
import smwmap

if __name__ == "__main__":
	q = multiprocessing.Queue()
	mapqueue = multiprocessing.Queue()

	alarm = multiprocessing.Process(target=timer.xseconds, args=(q,1))
	getmap = multiprocessing.Process(target=smwmap.obtainMap, args=(mapqueue, 'DemoBuilding', '2'))
	pro = multiprocessing.Process(target=proc.produce, args=(q,))
	pro2 = multiprocessing.Process(target=proc.produce2, args=(q,))
	con = multiprocessing.Process(target=proc.consume, args=(q,))

	alarm.start()
	pro.start()
	pro2.start()
	con.start()
	getmap.start()

	# alarm.join()
	# pro.join()
	# pro2.join()
	# con.join()
	# getmap.join()

	for x in range(1,6):
		time.sleep(1)
		print str(x)
	
	mapinfo = mapqueue.get()
	print repr(mapinfo)