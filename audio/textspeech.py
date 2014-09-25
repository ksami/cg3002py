import sys,os

def textToSpeech(myString):
	speak = 'espeak -s 155 "'+myString+'"'
	os.system(speak)


if __name__ == '__main__':
	lenOfArgs = len(sys.argv) -1
	printOrder = 1
	myString = ''
	while(lenOfArgs):
		myString = myString + sys.argv[printOrder] + ' '
		printOrder = printOrder + 1
		lenOfArgs = lenOfArgs - 1

	textToSpeech(myString)
