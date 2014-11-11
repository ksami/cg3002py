import subprocess
import sys

qrcode_exe = shlex.split("zbarcam --nodisplay --prescale=320x240 -Sdisable -Sqrcode.enable")

def main():
	process = subprocess.Popen(qrcode_exe, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	try:
		# Poll process for new output until finished
		while process.poll() == None:
			# read output
			nextline = process.stdout.readline()
			if nextline == "" and process.poll() != None:
				break

			elif nextline != " ":
				print nextline

		output = process.communicate()[0]
		exitCode = process.returncode

	except KeyboardInterrupt:
		print "process.poll():", process.poll()
		process.terminate()
		print "process.poll():", process.poll()
		# process.kill()
		# print "process.poll():", process.poll()
		process.wait()
		print "process.poll():", process.poll()

if __name__ == "__main__":
	main()