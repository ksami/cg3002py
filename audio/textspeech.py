import sys,os,time

class Speak(object):
	#Commands to read out
	cmd_list = {'sp': 'State starting position', 'e': 'State your ending position', 'c': 'Did you say ' 'gf': 'Go Forward', 'tl': 'Turn Left', 'tr': 'Turn Right'}
	
	def __init__(self):
		self.state = 0
		self.prevcmd = 'tl'
	#need to think of a better way to write this
	def sysinit(sys_queue):
		if(sys_queue.get() == 'c'):
			command = 'espeak -s 155 "'+cmd_list['c']+sys_queue.get() +'" > dev/null 2>&1'
			os.system(command)
			self.state = self.state -1
			
		else:
			if((sys_queue.get() == 'sp') and (self.state == 0)):
				command = 'espeak -s 155 "'+cmd_list['sp']+'" > dev/null 2>&1'
				os.system(command)
				self.state = self.state +1
				
			if(sys_queue.get() == 'ep' and (self.state == 1)):
				command = 'espeak -s 155 "'+cmd_list['ep']+'" > dev/null 2>&1'
				os.system(command)
				self.state = self.state +1
				
		
	def giveCmd(sys_queue):
		if(self.prevcmd == 'gf' and sys_queue.get() == 'gf'):
			#Do nothing
		else:
			self.prevcmd = sys_queue.get()
			command = 'espeak -s 155 "'+self.prevcmd+'" > /dev/null 2>&1'
			os.system(command)
	
	#just for testing
	def speakTest(myString):
		command = 'espeak -s 155 "'+myString+'"'
		os.system(command)



# for testing
# call with python textspeech.py texttoreadout
if __name__ == '__main__':
	lenOfArgs = len(sys.argv) -1
	printOrder = 1
	myString = ''
	
	while(lenOfArgs):
		myString = myString + sys.argv[printOrder] + ' '
		printOrder = printOrder + 1
		lenOfArgs = lenOfArgs - 1

	speak(myString)
