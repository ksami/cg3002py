import time

def produce(q):
	print "producing..."
	time.sleep(3)
	q.put("hello1")

def produce2(q):
	print "producing too..."
	time.sleep(5)
	q.put("hi2")

def consume(q):
	print "consuming"
	while True:
		print q.get()