# Main file handling multiple processes

import multiprocessing
import time

import timer
import smwmap
import cpython
import audio.textspeech
import pedometer.test

cameraExe = "./cprocess.o"
mapName = "COM1"
mapFloor = "2"

if __name__ == "__main__":
	q_cam = multiprocessing.Queue()
	q_map = multiprocessing.Queue()

	pedo = multiprocessing.Process(target=pedometer.test.execute)
	camera = multiprocessing.Process(target=cpython.execute, args=(q_cam, cameraExe))
	texttospeech = multiprocessing.Process(target=audio.textspeech.speakq, args=(q_cam,))
	alarm = multiprocessing.Process(target=timer.alarm, args=(4,))
	getmap = multiprocessing.Process(target=smwmap.obtainMap, args=(q_map, mapName, mapFloor))

	# start processes
	pedo.start()
	camera.start()
	texttospeech.start()
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
	pedo.join()
	camera.join()
	texttospeech.join()
	alarm.join()
	getmap.join()
