import sys,os
import subprocess

class Listen:
	program = "exec /home/pi/cg3002py/audio/cont -samprate 48000 -dict /home/pi/pocketsphinx-0.8/model/lm/en_US/cmu07a.dic -nfft 2048"

	#params:
	#q_listen: output from pocketsphinx
	def listen(self, q_listen):
		process = subprocess.Popen(Listen.program, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print "listen running"
		# Poll process for new output until finished
		while process.poll() == None:
			# read output
			nextline = process.stdout.readline()
			if nextline == "" and process.poll() != None:
				break

			print nextline
			q_listen.put(nextline)

		output = process.communicate()[0]
		exitCode = process.returncode

	def listenTest(self, cmd):
		process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

		# Poll process for new output until finished
		while process.poll() == None:
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


# test with python speechtext.py
if __name__ == "__main__":
	listen = Listen()
	listen.listenTest(Listen.program)
