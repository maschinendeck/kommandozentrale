import shelve
class SwitchClass():
	state = None
	methods = []
	def __init__(self, initial_data={}, **kwargs):
		initial_data.update(kwargs)
		for k,v in initial_data.items():
			setattr(self, k, v)
		self.state = self.loadState()

	def loadState(self):
		# get state from cache
		with shelve.open('kommandozentrale.db') as db:
			if self.name in db:
				return db[self.name]
			else:
				self.setState(False)

	def getState(self):
		return self.state

	def setState(self, state):
		with shelve.open('kommandozentrale.db') as db:
			db[self.name] = state
		self.state = state


class LightSwitch(SwitchClass):
	methods = ["on", "off"]

	def on(self):
		self.setState(True)
		return self.state

	def off(self):
		self.setState(False)
		return self.state



