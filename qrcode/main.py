import subprocess
import sys
import multiprocessing
import time

qrcode_exe = "exec /home/pi/cg3002py/qrcode/opencv-qrcode"

def qrscan(q_qrcode):
	process = subprocess.Popen(qrcode_exe, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print "qrscan running"

	# Poll process for new output until finished
	while process.poll() == None:
		# read output
		nextline = process.stdout.readline()
		if nextline == "" and process.poll() != None:
			break

		print nextline
		q_qrcode.put(nextline)

	output = process.communicate()[0]
	exitCode = process.returncode


def qrscantest():
	process = subprocess.Popen("opencv-qrcode", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	print "qrscan running"

	# Poll process for new output until finished
	while process.poll() == None:
		# read output
		nextline = process.stdout.readline()
		if nextline == "" and process.poll() != None:
			break

		print nextline

	output = process.communicate()[0]
	exitCode = process.returncode


if __name__ == "__main__":
	p_qrscan = multiprocessing.Process(target=qrscantest)
	p_qrscan.start()

	for i in xrange(1, 11):
		time.sleep(1)
		print i

	print "p_qrscan.is_alive():", p_qrscan.is_alive()
	p_qrscan.terminate()
	print "p_qrscan.is_alive():", p_qrscan.is_alive()
	p_qrscan.join()
	print "p_qrscan.is_alive():", p_qrscan.is_alive()