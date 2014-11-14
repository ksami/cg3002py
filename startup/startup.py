import subprocess
import multiprocessing
import time

import emailip

def execute(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process.communicate()[0]

startup = execute('aplay /home/pi/cg3002py/audio/beep.wav')

email=multiprocessing.Process(target=emailip.email)
email.start()

main = execute('sudo python /home/pi/cg3002py/main-nocomms.py 2>&1 /home/pi/cg3002log')
