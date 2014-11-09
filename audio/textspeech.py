import sys,os,time

class Speak:
	#Commands to read out
	cmd_list = {
		"sb": "State starting building",
		"sl": "State starting level",
		"sn": "State starting node",
		"sp": "Please state starting position", #for debugging so that no need to go tru so many steps
		"ep": "Please state your ending position",  #for debugging so that no need to go tru so many steps
		"eb": "State ending building",
		"el": "State ending level",
		"en": "State ending node",
		"r": "You have reached your destination ",
		"c": "Did you say {confirm}",
		"gf": "Go Forward",
		"tl": "Turn Left by {angle}",
		"tr": "Turn Right by {angle}",
		"os": "System starting up",
		"is": "Welcome. Clench your fist to start",
		"ns": "Starting navigation",
		"ws": "System paused",
		"rn": "You have reached node {node}",
		"sj": "You have to walk through {numBuildings} buildings",
		"sb": "You are currently at building {building} level {level}. You have to walk pass {numNodes} nodes. Now starting at node {startNode}"
	}
	program = "exec espeak -s 155 "  #program to execute
	dumpOutput = " > /dev/null 2>&1"
	def __init__(self):
		self.prevcmd = ""
			

	def speak(self, cmd):
		#if self.prevcmd == "gf" and cmd == "gf":
			#Do nothing
		#	pass
		#else:
		#cmd = "c,stringtoconfirm" or "r,destination"
		if cmd[0] == "c":
			#slice from comma to end
			a = Speak.cmd_list[cmd[0]] #a is the command (Change Later)
			w = cmd[2:]			   	   #w is the stuff to add to the command (Change Later) 
			command = (program + a).format(confirm = w) + dumpOutput
			self.prevcmd = cmd[0]

		elif cmd[0:2] == "tl" or cmd == "tr":
			a = Speak.cmd_list[cmd[0:2]]
			w = cmd[3:]
			command = (program + a).format(angle = w) + dumpOutput

		elif cmd[0:2] == "rn":
			a = Speak.cmd_list[cmd[0:2]]
			w = cmd[3:]
			command = (program + a).format(node = w) + dumpOutput

		elif cmd[0:2] == "sj":
			a = Speak.cmd_list[cmd[0:2]]
			w = cmd[3:]
			command = (program + a).format(numBuildings = w) + dumpOutput

		elif cmd[0:2] == "sb":
			cmd = cmd.split(',')
			a = Speak.cmd_list[cmd[0]]
			w = cmd[1]
			x = cmd[2]
			y = cmd[3]
			z = cmd[4]
			command = (program + a).format(building=w, level=x, numNodes=y, startNode=z) + dumpOutput

		else:
			a = Speak.cmd_list[cmd]
			command = (program + a) + dumpOutput

		os.system(command)


	def speakq(self, q_tts):
		while True:
			cmd = q_tts.get(block=True)

			#if self.prevcmd == "gf" and cmd == "gf":
				#Do nothing
			#	pass
			#else:
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
