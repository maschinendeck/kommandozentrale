import json

class TestCase():
	payload = None
	response = None

	def getPayload(self):
		assert self.payload != None, "Payload can't be None"
		return json.dumps(self.payload).encode("utf8")

	def validateResponse(self, response):
		return json.loads(response.decode("utf8")) == self.getResponse()

	def getResponse(self):
		assert self.response != None, "Response can't be None"
		return self.response

class Config(TestCase):
	payload = {"action":"get_config"}
	def validateResponse(self, response):
		result = True
		response = json.loads(response.decode("utf8"))
		if response["result"] == "config" and "config" in response \
			and isinstance(response["config"], dict):
			for switch_name in response["config"]:
				switch = response["config"][switch_name]
				if not (isinstance(switch, dict) and \
					"methods" in switch and isinstance(switch["methods"], list) and \
					"metadata" in switch and isinstance(switch["metadata"], dict) and \
					"type" in switch["metadata"] and isinstance(switch["metadata"]["type"], str) and \
					"location" in switch["metadata"] and isinstance(switch["metadata"]["location"], str) and \
					"state" in switch and isinstance(switch["state"], bool)):
					result = False
		else:
			result = False
		return result

class ExistingSwitch(TestCase):
	payload = {"action":"call_method", "switch":"hauptraum/decke_rechts","method":"on"}
	response = {"switch": "hauptraum/decke_rechts", "result": "state", "state": True}

class NotExistingSwitch(TestCase):
	payload = {"action":"call_method", "switch":"nonexistingswitch","method":"on"}
	response = {"result": "error", "error": "Switch with name nonexistingswitch not found"}

class PublicMethod(TestCase):
	payload = {"action":"call_method", "switch":"hauptraum/decke_rechts","method":"on"}
	response = {"switch": "hauptraum/decke_rechts", "result": "state", "state": True}

class PrivateMethod(TestCase):
	payload = {"action":"call_method", "switch":"hauptraum/decke_rechts","method":"getState"}
	response = {"result": "error", "error": "Method \"getState\" of switch \"hauptraum/decke_rechts\" is not public"}

class GetState(TestCase):
	payload = {"action":"get_state", "switch":"hauptraum/decke_rechts"}
	response = {"metadata": {"type": "bool", "location": "Decke Rechts"}, "switch": "hauptraum/decke_rechts", "result": "state", "state": True}