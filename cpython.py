# Python process to call C process

import subprocess
import sys

def execute(command):
	process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	output = process.stdout.readline()
	print output

	# Poll process for new output until finished
	while process.poll() == None:
		# ctrl = raw_input("kill or dont kill: ")
		# if ctrl == "kill":
		# 	ctrl = "0"
		# else:
		# 	ctrl = "1"
		# process.stdin.write("0")
		# nextline = process.stdout.readline()
		# if nextline == '' and process.poll() != None:
		# 	break


		msg = raw_input("kill or dont kill: ")
		if process.poll() == None:
			process.stdin.write(msg)

		output = process.stdout.readline()
		if output == '' and process.poll() != None:
			break
		print output
		#sys.stdout.write(nextline)
		#sys.stdout.flush()
		#q_cam.put(nextline)

	output = process.communicate()[0]
	exitCode = process.returncode

# test with cpython cprocess.o
if __name__ == '__main__':
	print 'executing {program}'.format(program=sys.argv[1])
	execute(sys.argv[1])