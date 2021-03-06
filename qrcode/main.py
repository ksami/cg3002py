import subprocess
import sys
import multiprocessing
import time
import shlex
import os

qrcode_exe = shlex.split("/home/pi/cg3002py/qrcode/opencv-qrcode")

def qrscan(q_qrcode, q_kill):
	process = subprocess.Popen(qrcode_exe, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print "qrscan running"

	# Poll process for new output until finished
	while process.poll() == None:
		# check for terminate
		try:
			kill = q_kill.get(block=False)
			if kill == 1:
				print "process.poll():", process.poll()
				process.terminate()
				print "process.poll():", process.poll()
				# process.kill()
				# print "process.poll():", process.poll()
				process.wait()
				print "process.poll():", process.poll()
		# Queue.empty
		except Exception:
			#ignore
			pass

		# read output
		nextline = process.stdout.readline()
		if nextline == "" and process.poll() != None:
			break

		elif nextline[0] != ' ' and nextline[0] != '\n':
			print "qr:", nextline
			q_qrcode.put(nextline)

	output = process.communicate()[0]
	exitCode = process.returncode


def qrscantest(q_kill):
	process = subprocess.Popen(qrcode_exe, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print "qrscan running"

	# Poll process for new output until finished
	while process.poll() == None:
		# check for terminate
		try:
			kill = q_kill.get(block=False)
			if kill == 1:
				print "process.poll():", process.poll()
				process.terminate()
				print "process.poll():", process.poll()
				# process.kill()
				# print "process.poll():", process.poll()
				process.wait()
				print "process.poll():", process.poll()
		# Queue.empty
		except Exception:
			#ignore
			pass

		# read output
		nextline = process.stdout.readline()
		if nextline == "" and process.poll() != None:
			break

		elif nextline[0] != ' ' and nextline[0] != '\n':
			print nextline
			os.system("aplay /home/pi/cg3002py/audio/tone.wav")

	output = process.communicate()[0]
	exitCode = process.returncode


if __name__ == "__main__":
	q_kill = multiprocessing.Queue()
	p_qrscan = multiprocessing.Process(target=qrscantest, args=(q_kill,))
	p_qrscan.start()

	try:
		for i in xrange(1, 3001):
			time.sleep(1)
			print i

		q_kill.put(1)
		
	except KeyboardInterrupt:
		q_kill.put(1)

	# print "p_qrscan.is_alive():", p_qrscan.is_alive()
	# p_qrscan.terminate()
	# print "p_qrscan.is_alive():", p_qrscan.is_alive()
	# p_qrscan.join()
	# print "p_qrscan.is_alive():", p_qrscan.is_alive()
