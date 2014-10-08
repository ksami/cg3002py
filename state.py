import time

class State(object):
	# States for the whole system
	STATE_OFF = 0
	STATE_IDLE = 1
	STATE_INIT = 2
	STATE_NAVI = 3
	STATE_WAIT = 4


	def __init__(self):
		self.currentState = State.STATE_OFF

	# Changes state to next valid state
	def changeState(self, isHandOpen=False):

		if self.currentState == State.STATE_OFF:
			self.currentState = State.STATE_IDLE

		elif self.currentState == State.STATE_IDLE:
			self.currentState = State.STATE_INIT

		elif self.currentState == State.STATE_INIT:
			if isHandOpen == True:
				self.currentState = State.STATE_IDLE
			else:
				self.currentState = State.STATE_NAVI

		elif self.currentState == State.STATE_NAVI:
			self.currentState = State.STATE_WAIT

		elif self.currentState == State.STATE_WAIT:
			if isHandOpen == True:
				self.currentState = State.STATE_IDLE
			else:
				self.currentState = State.STATE_NAVI

		else:
			#corrupted state?
			pass

	# Returns current state
	def getCurrentState(self):
		return self.currentState