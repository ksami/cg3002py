import sys,os,time

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
