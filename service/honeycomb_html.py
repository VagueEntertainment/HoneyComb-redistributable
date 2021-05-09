#!/usr/bin/env python3

import subprocess
import sys
import os
sys.path.append("..")
import json
import time
import honeycomb_core as Core
import logging

from bottle import route, run, template, request, static_file

@route('/', method='POST')
def index():
	themessage = request.forms.get("msg")
	appId = ""
	key = ""
	message = ""
	#print(themessage)
	if len(themessage.split("<::>")) == 3:
		#print("Encrypted message")
		appId = themessage.split("<::>")[0]
		key = Account.get_priv_from_pub(appId,"App")
		message = themessage.split("<::>")[1]
		decrypted = message
		#decrypted = Seed.simp_decrypt(key,message)
		#print("From: "+decrypted)
		response = Core.message(decrypted)
		encrypt = Seed.simp_crypt(key,response)
		#print("Returning: "+Seed.simp_decrypt(key,encrypt))
		return encrypt
	else:
		#print("Non-encrypted message")
		if themessage != None:
			return Core.message("service",themessage)

print("Started")
run(host='0.0.0.0', port=8000)
