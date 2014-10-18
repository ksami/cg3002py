import sys,os,time

class Read(object):
	#Commands to read out
	cmd_list = {'sp': 'State starting position', 'e': 'State your ending position', 'c': 'Did you say' 'gf': 'Go Forward', 'tl': 'Turn Left', 'tr': 'Turn Right'}
	
	def sysinit(sys_queue):
		if(sys_queue.get == 'sp'):
			command = 'espeak -s 155 "'+cmd_list['sp']+'" > dev/null 2>&1'
			os.system(command)
		
	
	def speakq(q_string):
		while True:
			myString = q_string.get()
			print myString
			command = 'espeak -s 155 "'+myString+'" > /dev/null 2>&1'
			os.system(command)

	def speak(myString):
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
