# Python process to call C process

import subprocess
import sys

def execute(command):
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	# Poll process for new output until finished
	while True:
		nextline = process.stdout.readline()
		if nextline == '' and process.poll() != None:
			break

		print nextline
		#sys.stdout.write(nextline)
		#sys.stdout.flush()

	output = process.communicate()[0]
	exitCode = process.returncode

# test with cpython cprocess.o
if __name__ == '__main__':
	print 'executing {program}'.format(program=sys.argv[1])
	execute(sys.argv[1])