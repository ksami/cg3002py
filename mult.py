# Main file handling multiple processes

import multiprocessing
import time

import timer
import smwmap
import cpython

cameraExe = "./cprocess.o"
mapName = "COM1"
mapFloor = "2"

if __name__ == "__main__":
	q_map = multiprocessing.Queue()

	camera = multiprocessing.Process(target=cpython.execute, args=(cameraExe,))
	alarm = multiprocessing.Process(target=timer.alarm, args=(4,))
	getmap = multiprocessing.Process(target=smwmap.obtainMap, args=(q_map, mapName, mapFloor))

	# start processes
	camera.start()
	alarm.start()
	getmap.start()

	# timer seconds since processes started
	for x in range(1,10):
		time.sleep(1)
		print str(x)
	
	# get data from mapqueue
	mapinfo = q_map.get()
	print repr(mapinfo)

	# wait for processes to end
	camera.join()
	alarm.join()
	getmap.join()
