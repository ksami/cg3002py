#!/usr/bin/python
# The idea behind this script is if plugging a RaspberryPi into a foreign network whilst r$
# (i.e. without a monitor/TV), you need to know what the IP address is to SSH into it.
#
# This script emails you the IP address if it detects an ethernet address other than it's $
# that it normally has, i.e. on your home network.


import subprocess
import string
import smtplib
import time
from email.mime.text import MIMEText

def execute(command):
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process.communicate()[0]

# startup = execute('aplay /home/pi/cg3002py/audio/beep.wav')

def email():
	print "going to sleep"

	#sleep for 30 seconds first
	#to make sure wireless is connected
	time.sleep(30)

	print "woke up, executing commands"

	ipaddr = execute('/sbin/ifconfig wlan0 | grep inet')
	text = ipaddr

	# debug
	print ipaddr

	datetime = time.asctime()

	print datetime

	SUBJECT = 'IP Address from Raspberry Pi at: %s' % datetime
	TO = 'ksami.ken@gmail.com'
	FROM = 'ksami.ken@gmail.com'
	BODY = string.join((
	        'From: %s' % FROM,
	        'To: %s' % TO,
	        'Subject: %s' % SUBJECT,
	        '',
	        text
	        ), '\r\n')

	BODY = MIMEText(BODY)
	server = smtplib.SMTP_SSL('smtp.gmail.com', 465)     # NOTE:  This is the GMAIL SSL port.
	server.login('ksami.ken@gmail.com', 'thisisap455w0rd')
	refused = server.sendmail(FROM, [TO], BODY.as_string())
	print "refused is ", refused
	server.quit()

if __name__ = "__main__":
	email()