# Main file handling multiple processes

import multiprocessing
import time
import proc
import timer
import smwmap
import cpython

cameraExe = "cprocess.o"
mapName = "DemoBuilding"
mapFloor = "2"

if __name__ == "__main__":
	q = multiprocessing.Queue()
	mapqueue = multiprocessing.Queue()
	cameraqueue = multiprocessing.Queue()

	cameraConsume = multiprocessing.Process(target=proc.consume, args=(cameraqueue,))
	#camera = multiprocessing.Process(target=cpython.execute, args=(cameraqueue,cameraExe))
	alarm = multiprocessing.Process(target=timer.xseconds, args=(q,1))
	getmap = multiprocessing.Process(target=smwmap.obtainMap, args=(mapqueue, mapName, mapFloor))
	pro = multiprocessing.Process(target=proc.produce, args=(q,))
	pro2 = multiprocessing.Process(target=proc.produce2, args=(q,))
	con = multiprocessing.Process(target=proc.consume, args=(q,))

	# start processes
	cameraConsume.start()
	#camera.start()
	alarm.start()
	pro.start()
	pro2.start()
	con.start()
	getmap.start()

	# timer seconds since processes started
	for x in range(1,6):
		time.sleep(1)
		print str(x)
	
	# get data from mapqueue
	mapinfo = mapqueue.get()
	print repr(mapinfo)

	# wait for processes to end
	cameraConsume.join()
	#camera.join()
	alarm.join()
	pro.join()
	pro2.join()
	con.join()
	getmap.join()