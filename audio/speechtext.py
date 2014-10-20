import sys,os
import subprocess

#TODO replace "compiledcfile"
class Listen:
	program = "compiledcfile -samprate 48000 -dict /home/pi/pocketsphinx-0.8/model/lm/en_US/cmu07a.dic -nfft 2048"

	# currently prints all output from the c process
	def listen(self, q_listen):
		process = subprocess.Popen(Listen.program, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		# Poll process for new output until finished
		while True:
			nextline = process.stdout.readline()
			if nextline == "" and process.poll() != None:
				break

			#print nextline
			#sys.stdout.write(nextline)
			#sys.stdout.flush()
			q_listen.put(nextline)

		output = process.communicate()[0]
		exitCode = process.returncode

	def listenTest(self, cmd):
		process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		# Poll process for new output until finished
		while True:
			nextline = process.stdout.readline()
			if nextline == "" and process.poll() != None:
				break

			print nextline
			#sys.stdout.write(nextline)
			#sys.stdout.flush()
			#q_cam.put(nextline)

		output = process.communicate()[0]
		exitCode = process.returncode

		print "stdout: ", output
		print "exitCode: ", exitCode


# test with python speechtext.py cprocess.o
if __name__ == "__main__":
	listen = Listen()

	if len(sys.argv) < 2:
		print "run with python speechtext.py cprocess.o"
	else:
		print "executing {program}".format(program=sys.argv[1])
		listen.listenTest(sys.argv[1])
