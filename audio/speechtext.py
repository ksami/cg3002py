import sys,os
import subprocess

class Listen:
	program = "/home/pi/cg3002py/audio/cont -samprate 48000 -dict /home/pi/pocketsphinx-0.8/model/lm/en_US/cmu07a.dic -nfft 2048"

	#params:
	#q_listen: output from pocketsphinx
	#q_listenctrl: input to pocketsphinx
	def listen(self, q_listen, q_listenctrl):
		process = subprocess.Popen(Listen.program, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		print "listen running"
		# Poll process for new output until finished
		while process.poll() == None:
			# send 1 for continue, 0 for kill
			ctrl = q_listenctrl.get(block=True)
			if ctrl == "kill":
				ctrl = "0"
			else:
				ctrl = "1"

			# will have error if process is dead but trying to write
			if process.poll() == None:
				process.stdin.write(ctrl)

			# read output
			nextline = process.stdout.readline()
			if nextline == "" and process.poll() != None:
				break

			print nextline
			q_listen.put(nextline)

		output = process.communicate()[0]
		exitCode = process.returncode

	def listenTest(self, cmd):
		process = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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
	#program = "sudo /home/pi/cg3002py/audio/cont -samprate 48000 -dict /home/pi/pocketsphinx-0.8/model/lm/en_US/cmu07a.dic -nfft 2048"
	#os.system(program)
	listen = Listen()
	listen.listenTest(Listen.program)
	#if len(sys.argv) < 2:
	#	print "run with python speechtext.py cprocess.o"
	#else:
	#	print "executing {program}".format(program=sys.argv[1])
	#	listen.listenTest(sys.argv[1])
