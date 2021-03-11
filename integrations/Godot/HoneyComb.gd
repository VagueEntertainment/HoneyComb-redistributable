extends Node


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
signal honeycomb_returns(return_type,data)
signal loading()

var websocket = WebSocketClient.new()
var websocket_transfer
var request = ""
var connectionType = 2
var settings = {}
var dynamic_props = {}
var hive_engine_tokens = []
var honeycomb_process = []
var pid 
var dir = Directory.new()
# Called when the node enters the scene tree for the first time.
func _ready():
	check_for_service()
	websocket.connect("connection_closed", self, "_closed")
	websocket.connect("connection_error", self, "_closed")
	websocket.connect("connection_established", self, "_connected")
	websocket.connect("data_received", self, "_on_data")
	pass # Replace with function body.

func _process(_delta):
	if connectionType == 2:
		websocket.poll()
	pass
### Preflight
func _closed(was_clean = false):
	# was_clean will tell you if the disconnection was correctly notified
	# by the remote peer before closing the socket.
	print("Closed, clean: ", was_clean)
	set_process(false)
	
func _connected(proto = ""):
	# This is called on connection, "proto" will be the selected WebSocket
	# sub-protocol (which is optional)
	print("Connected with protocol: ", proto)
	# You MUST always use get_peer(1).put_packet to send data to server,
	# and not put_packet directly when not using the MultiplayerAPI.
	#websocket.get_peer(1).put_packet("Test packet".to_utf8())
	websocket.get_peer(1).put_packet('{"act":["check_settings"],"type":"check"}'.to_utf8())
	websocket_transfer = websocket.get_peer(1)

func _on_data():

	# Print the received packet, you MUST always use get_peer(1).get_packet
	# to receive data from server, and not get_packet directly when not
	# using the MultiplayerAPI.
	var data = websocket.get_peer(1).get_packet().get_string_from_utf8()
	#print("Got data from server: ", data)
	var jsoned = parse_json(data)
	match jsoned["honeycomb"]["type"]:
		"check":
				emit_signal("honeycomb_returns","service",["running"])
				$service_check.stop()
				get_settings()
				#get_hive_engine_tokens()
				#hive_get_dynamic_props()
		"get_settings":
			settings = jsoned["honeycomb"]["settings"]
			emit_signal("honeycomb_returns","honeycomb_settings",[jsoned])
			#check_client_registration(settings["hiveaccount"])
		_: 
			emit_signal("honeycomb_returns",jsoned["honeycomb"]["type"],[data])

func websocket_returns(data):
	print("websocket did something")
	print(websocket.poll())
	pass
	
func check_for_service():
	match connectionType:
		1:
			var check = HTTPRequest.new()
			check.set_timeout(10)
			add_child(check)
			check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["check",check])
			check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["check_settings"]}')
		2:
			print("Using Web Sockets")
			var err = websocket.connect_to_url("ws://0.0.0.0:8671")
			if err !=OK:
				 print("Unable to connect")
				 #set_process(false)
				 connectionType = 1
	
func check_client_registration(account):
	var msg = {
				act = ["registration_check"],
				account = account,
				type ="check_registration"
			}
	match connectionType:
		1:
			var check = HTTPRequest.new()
			check.set_timeout(10)
			add_child(check)
			check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["check_registration",check])
			check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg='+to_json(msg))
		2:
			websocket_transfer.put_packet(to_json(msg).to_utf8())
	
func set_location():
	var msg = {
			act = ["update_loc"],
			appname = "com.vagueentertainment.honeycomb",
			type = "location"
		}
	match connectionType:
		1:
			var check = HTTPRequest.new()
			check.set_timeout(10)
			add_child(check)
			check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["location",check])
			check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg='+to_json(msg))
		2:
			websocket_transfer.put_packet(to_json(msg).to_utf8())
			

func launch_service():
	#if check_for_service():
	#	print("launching")
		
	pass
	
func get_settings():
	var msg = {
				act = ["get_settings"],
				type ="get_settings"
			}
	match connectionType:
		1:
			var check = HTTPRequest.new()
			check.set_timeout(10)
			add_child(check)
			check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["get_settings",check])
			check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg='+to_json(msg))
		2:
			websocket_transfer.put_packet(to_json(msg).to_utf8())
	pass
	
func set_settings():
	
	pass

func login(_name,_password):
	pass

func add_account(account,keys):
	var msg = {
					act = ["add_account"],
					account = account,
					keys = [keys["posting"]+'","'+keys["active"]]
				}
	match connectionType:
		1:
			if keys.has("posting") and keys.has("active"):
				print("Keys are in order")
				var check = HTTPRequest.new()
				check.set_timeout(10)
				add_child(check)
				check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["add_account",check])
				check.request("http://0.0.0.0:8670/",[],false,HTTPClient.METHOD_POST,'msg='+to_json(msg))
		2:
			if keys.has("posting") and keys.has("active"):
				print("Keys are in order")
				websocket_transfer.put_packet(to_json(msg).to_utf8())

func list_accounts():
	var msg = {
				act = ["get_accounts"],
				type = "get_accounts"
				}
	match connectionType:
		1:
			var check = HTTPRequest.new()
			check.set_timeout(10)
			add_child(check)
			check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["get_accounts",check])
			check.request("http://0.0.0.0:8670/",[],false,HTTPClient.METHOD_POST,'msg='+to_json(msg))
		2:
			websocket_transfer.put_packet(to_json(msg).to_utf8())

func check_mode():
	pass

### Highscore

func set_highscore(_game_id,_user):
	pass

func get_highscores(_game_id):
	pass

### Save/Load games

func save_game_local(_game_id,_user,_data):
	pass

func save_game_cloud(_game_id,_user,_data):
	pass

func load_save_game_local(_game_id,_user,_index):
	pass

func load_save_game_cloud(_game_id,_user,_index):
	pass

### Data store

func save_data_local(_app_id,_user,_data):
	pass

func get_data_local(_app_id,_user,_key):
	pass

func set_data_local(_app_id,_user,_key,_data):
	pass
	
### Hive-Engine

func find_nfts(_key,_user):
	pass

func get_nft(source,app,account,opts = []):
	match connectionType:
		1:
			var check = HTTPRequest.new()
			check.set_timeout(10)
			var message = ""
			if source == "hive-engine":
				if app == "nftshowroom":
					var command = {"act":["get_nftshowroom_art"],
							"account":account,
							"opts":opts,
							"type":app
						}
					message = 'msg='+to_json(command)
			add_child(check)
			check.connect("request_completed",self,"_on_HTTPRequest_request_completed",[app,check])
			check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,message)
		2:
			if source == "hive-engine":
				if app == "nftshowroom":
					var command = {"act":["get_nftshowroom_art"],
							"account":account,
							"opts":opts,
							"type":app
						}
					websocket_transfer.put_packet(to_json(command).to_utf8())
	
	pass

func create_nft():
	pass

### Data storage

func ipfs_load(_id):
	pass

func ipfs_pin(_id):
	pass

func ipfs_get(_id):
	pass
	
func cache_img(img):
	var check = HTTPRequest.new()
	check.set_timeout(10)
	check.use_threads = true
	add_child(check)
	var fullurl = 'msg={"act":["image_retrieval"],"url":"'+img+'"}'
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["cache",check])
	check.request("http://127.0.0.1:8670/",[],true,HTTPClient.METHOD_POST,fullurl)
	pass
	
### Hive General Functions

func claim_hive_rewards(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["claim_hive_rewards",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["claim_hive_rewards"],"account":"'+account+'","type":["all"]}')
	pass

func load_wallet(account = settings["hiveaccount"]):
	print("from Load wallet ",account)
	var check = HTTPRequest.new()
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["wallet",check])
	var msg = {
		"act":["get_account","get_from_hive","get_from_hive_engine"],
		"account":account,
		"params":{"get_account":["profile","followers","following","balances","delegation"],"get_from_hive":["voting_power","RC"],"get_from_hive_engine":["balance"]},
		"opts": []
	}
	#check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_account"],"account":"'+settings["hiveaccount"]+'","type":["profile","followers","following","balances","delegation"]}')
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg='+to_json(msg))
	pass

func get_followers(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["followers",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_account"],"account":"'+account+'","type":["followers"],"opts":[]}')
	pass

func get_following(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["following",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_account"],"account":"'+account+'","type":["following"],"opts":[]}')
	pass

func get_profile(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["profile",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_account"],"account":"'+account+'","type":["profile"],"opts":[]}')
	pass

func get_from_hive(type,account):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_"+type,check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_from_hive"],"account":"'+account+'","type":["'+type+'"],"opts":[]}')
	pass
	
func hive_get_vp(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_vp",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_from_hive"],"account":"'+account+'","type":["voting_power"],"opts":[]}')
	pass

func hive_get_RC(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_rc",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_from_hive"],"account":"'+account+'","type":["RC"],"opts":[]}')
	pass
	
func hive_get_delegation(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_delegation",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_account"],"account":"'+account+'","type":["delegation"],"opts":[]}')
	pass
	
func get_balance(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_balances",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_account"],"account":"'+account+'","type":["balances"],"opts":[]}')
	pass
	
func hive_get_rewards(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_rewards",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_from_hive"],"account":"'+account+'","type":["balances"],"opts":[]}')
	pass
	
func hive_get_dynamic_props():
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_dynamic_props",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_hive_dynamic_props"]}')
	pass


func get_history(author,history_type,return_type = "history"):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(10)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",[return_type,check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_history"],"account":"'+author+'","type":["'+history_type+'"],"opts":[]}')
	pass

### Hive Engine

func get_hive_engine_tokens():
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(2)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_engine_tokens",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_from_hive_engine"],"account":"","type":["tokens"]}')
	pass

func get_hive_engine_balance(account = settings["hiveaccount"]):
	var check = HTTPRequest.new()
	#check.use_threads = true
	check.set_timeout(2)
	add_child(check)
	check.connect("request_completed",self,"_on_HTTPRequest_request_completed",["hive_engine_balance",check])
	check.request("http://127.0.0.1:8670/",[],false,HTTPClient.METHOD_POST,'msg={"act":["get_from_hive_engine"],"account":"'+account+'","type":["balance"]}')
	pass
	
func set_hive_engine_tokens(data):
	hive_engine_tokens = parse_json(data)["honeycomb"]["hive_engine"]["tokens"]

func _on_HTTPRequest_request_completed(_result, response_code, _headers, body,request_type,object):
	#print(response_code," ",request_type)
	if response_code == 0:
		if request_type == "check":
			emit_signal("honeycomb_returns","service",["stopped"])
			OS.execute("./HoneyComb-redistributable/service/honeycomb.py",[],false,[])
			if $service_check.is_stopped():
				$service_check.wait_time +=2
				$service_check.start()
		
	if response_code == 200:
		match request_type:
			"check":
				emit_signal("honeycomb_returns","service",["running"])
				$service_check.stop()
				get_settings()
				get_hive_engine_tokens()
				hive_get_dynamic_props()
				
			"get_settings":
				settings = parse_json(body.get_string_from_ascii())["honeycomb"]["settings"]
				emit_signal("honeycomb_returns","honeycomb_settings",[body.get_string_from_ascii()])
				check_client_registration(settings["hiveaccount"])
			"check_registration":
				set_location()
				emit_signal("honeycomb_returns","honeycomb_registration_status",[body.get_string_from_ascii()])
			"location":
				emit_signal("honeycomb_returns","honeycomb_location",[body.get_string_from_ascii()])
			"profile":
				emit_signal("honeycomb_returns","profile",[body.get_string_from_ascii()])
			"following":
				emit_signal("honeycomb_returns","following",[body.get_string_from_ascii()])
			"followers":
				emit_signal("honeycomb_returns","followers",[body.get_string_from_ascii()])
			"hive_vp":
				emit_signal("honeycomb_returns","hive_vp",[body.get_string_from_ascii()])
			"hive_rc":
				emit_signal("honeycomb_returns","hive_rc",[body.get_string_from_ascii()])
			"hive_delegation":
				emit_signal("honeycomb_returns","hive_delegation",[body.get_string_from_ascii()])
			"hive_balances":
				emit_signal("honeycomb_returns","hive_balances",[body.get_string_from_ascii()])
			"hive_rewards":
				emit_signal("honeycomb_returns","hive_rewards",[body.get_string_from_ascii()])
			"hive_dynamic_props":
				dynamic_props = parse_json(body.get_string_from_ascii())["honeycomb"]["hive"]["misc"]["hive_dgp"]["data"]
			"claim_hive_rewards":
				emit_signal("honeycomb_returns","claim_hive_rewards",[body.get_string_from_ascii()])
			"hive_engine_balance":
				emit_signal("honeycomb_returns","hive_engine_balance",[body.get_string_from_ascii()])
			"hive_engine_tokens":
				set_hive_engine_tokens(body.get_string_from_ascii())
			"history":
				emit_signal("honeycomb_returns","history",[body.get_string_from_ascii()])
			"wallet":
				emit_signal("honeycomb_returns","wallet",[body.get_string_from_ascii()])
			"cache":
				emit_signal("honeycomb_returns","cache",body)
			_:
				emit_signal("honeycomb_returns",request_type,[body.get_string_from_ascii()])
				
		object.queue_free()		
	
	pass # Replace with function body.


func _on_service_check_timeout():
	check_for_service()
	#print("checking for service")
	pass # Replace with function body.
