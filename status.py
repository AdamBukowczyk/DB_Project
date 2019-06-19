import json
import sys

def createStatus(status='OK', data=None, debug=None):
	jsonObj = {
		"status": status
	}
	if data is not None: 
		jsonObj["data"] = data
	if debug is not None:
		jsonObj["debug"] = debug
	json.dump(jsonObj, sys.stdout)
	print('\n')
	
def createErrorStatus(data=None, debug=None):
	createStatus('Error', data, debug)