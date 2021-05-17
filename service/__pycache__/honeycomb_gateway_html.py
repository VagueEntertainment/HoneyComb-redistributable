#!/usr/bin/python3

import subprocess
import sys
import os
sys.path.append("..")
import json
import time
import honeycomb_core as Core

from bottle import hook, route, run, template, request, static_file

@hook('before_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    
@hook('after_request')
def cors_enable():
    response.headers['Access-Control-Allow-Origin'] = '*'

@route('/api', method='POST')
def index():
	themessage = request.forms.get("msg")
	appId = ""
	key = ""
	message = ""
	print(themessage)
	if len(themessage.split("<::>")) == 3:
		print("Encrypted message")
		appId = themessage.split("<::>")[0]
		key = Account.get_priv_from_pub(appId,"App")
		message = themessage.split("<::>")[1]
		decrypted = message
		#decrypted = Seed.simp_decrypt(key,message)
		print("From: "+decrypted)
		response = Core.message(decrypted)
		encrypt = Seed.simp_crypt(key,response)
		#print("Returning: "+Seed.simp_decrypt(key,encrypt))
		return encrypt
	else:
		print("Non-encrypted message")
		if themessage != None:
			return Core.message("gateway",themessage)


run(host='0.0.0.0', port=8675)
