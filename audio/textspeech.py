import sys,os,time

class Speak:
	#Commands to read out
	cmd_list = {
		"sp": "Please state starting position",
		"ep": "Please state your ending position",
		"r": "You have reached your destination ",
		"c": "Did you say ",
		"gf": "Go Forward",
		"tl": "Turn Left",
		"tr": "Turn Right"
	}
	program = "exec espeak -s 155 \"{}\" > /dev/null 2>&1"

	def __init__(self):
		self.prevcmd = ""
			

	def speak(self, cmd):
		if self.prevcmd == "gf" and cmd == "gf":
			#Do nothing
			pass
		else:
			#cmd = "c,stringtoconfirm" or "r,destination"
			if cmd[0] == "c" or cmd[0] == "r":
				#slice from comma to end
				strtoconfirm = Speak.cmd_list[cmd[0]] + cmd[2:]
				command = Speak.program.format(strtoconfirm)
				self.prevcmd = cmd[0]
			else:
				command = Speak.program.format(Speak.cmd_list[cmd])
				self.prevcmd = cmd

			os.system(command)


	def speakq(self, q_tts):
		while True:
			cmd = q_tts.get(block=True)

			if self.prevcmd == "gf" and cmd == "gf":
				#Do nothing
				pass
			else:
				#cmd = "c,stringtoconfirm" or "r,destination"
				if cmd[0] == "c" or cmd[0] == "r":
					#slice from comma to end
					strtoconfirm = Speak.cmd_list[cmd[0]] + cmd[2:]
					command = Speak.program.format(strtoconfirm)
					self.prevcmd = cmd[0]
				else:
					command = Speak.program.format(Speak.cmd_list[cmd])
					self.prevcmd = cmd

				os.system(command)


	#just for testing
	def speakTest(self, myString):
		command = Speak.program.format(myString)
		print "running: ", command
		os.system(command)


# for testing
# call with python textspeech.py texttoreadout
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "call with python textspeech.py texttoreadout"
	else:
		speak = Speak()
		myString = sys.argv[1]
		print "speaking"
		speak.speakTest(myString)
