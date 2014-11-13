import subprocess
import multiprocessing
import time

import startup.email

def execute(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process.communicate()[0]

startup = execute('aplay /home/pi/cg3002py/audio/beep.wav')

email=multiprocessing.Process(target=startup.email.email)
email.start()

main = execute('sudo python /home/pi/cg3002py/main.py')