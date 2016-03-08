import shelve
class OnOffSwitch():
	state = False
	methods = ["on", "off"]
	def __init__(self, initial_data={}, **kwargs):
		initial_data.update(kwargs)
		for k,v in initial_data.items():
			setattr(self, k, v)
		self.state = self.getCurrentState()

	def on(self):
		self.state = True
		return self.state

	def off(self):
		self.state = False
		return self.state

	def getState(self):
		return self.state

	def getCurrentState(self):
		# get state from cache
		with shelve.open('kommandozentrale.db') as db:
			if self.name in db:
				return db[self.name]
			else:
				db[self.name] = False