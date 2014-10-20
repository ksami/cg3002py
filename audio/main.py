from textspeech import Speak
from speechtext import Listen

def speak(speak, cmd):
	speak.speak(cmd)

def speakq(speak, q_tts):
	speak.speakq(q_tts)

def speakTest(speak, myString):
	speak.speakTest(myString)

def listen(q_listen):
	listen = Listen()
	listen.listen(q_listen)
