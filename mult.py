# Main file handling multiple processes

import multiprocessing
import time
import proc
import timer

if __name__ == "__main__":
	q = multiprocessing.Queue()
	alarm = multiprocessing.Process(target=timer.xseconds, args=(q,1))
	pro = multiprocessing.Process(target=proc.produce, args=(q,))
	pro2 = multiprocessing.Process(target=proc.produce2, args=(q,))
	con = multiprocessing.Process(target=proc.consume, args=(q,))

	alarm.start()
	pro.start()
	pro2.start()
	con.start()
