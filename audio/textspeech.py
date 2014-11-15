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
		"gf": "Forward",
		"gu": "Go Up",
		"tl": "Left",
		"tr": "Right",
		"os": "System starting up",
		"is": "Welcome. Clench your fist to start",
		"ns": "Starting navigation",
		"ws": "System paused",
		"rn": "You have reached node {node}",
		#"sj": "You have to walk through {numBuildings} buildings",
		"bn": "Currently at building {building} and node {node}"
	}
	program = "exec espeak -s 155 "  #program to execute
	dumpOutput = " > /dev/null 2>&1"
	def __init__(self):
		self.prevcmd = ""
			

	def speak(self, cmd):
		program = "exec espeak -s 155 "
		dumpOutput = " > /dev/null 2>&1"
		if cmd[0] == "c":
			#slice from comma to end
			a = Speak.cmd_list[cmd[0]] #a is the command (Change Later)
			w = cmd[2:]			   	   #w is the stuff to add to the command (Change Later) 
			command = (program + "\"" + a + "\"").format(confirm = w) + dumpOutput
			#print command for debugging

		# elif cmd[0:2] == "tl" or cmd[0:2] == "tr":
		# 	a = Speak.cmd_list[cmd[0:2]]
		# 	#w = cmd[3:]
		# 	command = (program + "\"" + a + "\"").format(angle = w) + dumpOutput

		elif cmd[0:2] == "rn":
			a = Speak.cmd_list[cmd[0:2]]
			w = cmd[3:]
			command = (program + "\"" + a + "\"").format(node = w) + dumpOutput

		elif cmd[0:2] == "sj":
			a = Speak.cmd_list[cmd[0:2]]
			w = cmd[3:]
			command = (program + "\"" + a + "\"").format(numBuildings = w) + dumpOutput

		#current node
		elif cmd[0:2] == "bn":
			cmd = cmd.split(',')
			a = Speak.cmd_list[cmd[0]]
			w = cmd[1]
			x = cmd[2]
			command = (program + "\"" + a + "\"").format(building=w, node=x) + dumpOutput

		else:
			try:
				a = Speak.cmd_list[cmd]
			except:
				raise
			command = (program + "\"" + a + "\"") + dumpOutput

		os.system(command)


	def speakq(self, q_tts, q_kill):
		while True:
			# check for terminate
			try:
				kill = q_kill.get(block=False)
				if kill == 1:
					break
			# Queue.empty
			except Exception:
				#ignore
				pass

			try:
				cmd = q_tts.get(block=False)
				print "espeaking:", cmd
				program = "exec espeak -s 155 "
				dumpOutput = " > /dev/null 2>&1"
				if cmd[0] == "c":
					#slice from comma to end
					a = Speak.cmd_list[cmd[0]] #a is the command (Change Later)
					w = cmd[2:]			   	   #w is the stuff to add to the command (Change Later) 
					command = (program + "\"" + a + "\"").format(confirm = w) + dumpOutput
					#print command for debugging

				elif cmd[0:2] == "tl" or cmd[0:2] == "tr":
					a = Speak.cmd_list[cmd[0:2]]
					w = cmd[3:]
					command = (program + "\"" + a + "\"").format(angle = w) + dumpOutput

				elif cmd[0:2] == "rn":
					a = Speak.cmd_list[cmd[0:2]]
					w = cmd[3:]
					command = (program + "\"" + a + "\"").format(node = w) + dumpOutput

				elif cmd[0:2] == "sj":
					a = Speak.cmd_list[cmd[0:2]]
					w = cmd[3:]
					command = (program + "\"" + a + "\"").format(numBuildings = w) + dumpOutput

				elif cmd[0:2] == "sb":
					cmd = cmd.split(',')
					a = Speak.cmd_list[cmd[0]]
					w = cmd[1]
					x = cmd[2]
					y = cmd[3]
					z = cmd[4]
					command = (program + "\"" + a + "\"").format(building=w, level=x, numNodes=y, startNode=z) + dumpOutput

				elif cmd[0:2] == "bn":
					cmd = cmd.split(',')
					a = Speak.cmd_list[cmd[0]]
					w = cmd[1]
					x = cmd[2]
					command = (program + "\"" + a + "\"").format(building=w, node=x) + dumpOutput

				else:
					try:
						a = Speak.cmd_list[cmd]
					except:
						raise
					command = (program + "\"" + a + "\"") + dumpOutput

				os.system(command)
			# Queue.empty
			except Exception:
				#ignore
				pass


	#just for testing can remove liao!
	def speakTest(self):
		while True:
			myString = raw_input("Enter string to talk: ")
			speak.speak(myString)

	#Make a Tick sound if queue has a value
	def stepTicker(self, q_stepTicker, q_kill):
		while True:
			# check for terminate
			try:
				kill = q_kill.get(block=False)
				if kill == 1:
					break
			# Queue.empty
			except Exception:
				#ignore
				pass

			try:
				step = q_stepTicker.get(block=False)
				if step == 1:
					os.system("aplay losticks.wav")
			except Exception:
				#ignore
				pass



# for testing
# call with python textspeech.py. Change test str to test accordingly
if __name__ == "__main__":
	speak = Speak()
	#speak.stepTicker()
	speak.speakTest()
