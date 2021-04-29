extends Control


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var save = false
# Called when the node enters the scene tree for the first time.
func _ready():
	HoneyComb.connect("honeycomb_returns",self,"_on_honeycomb_returns")
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass


func _on_Cancel_pressed():
	pass # Replace with function body.


func _on_Create_pressed():
	var passphrase = $PanelContainer/VBoxContainer/HBoxContainer/Passphrase.text
	HoneyComb.create_wallet(passphrase)
	
		
	pass # Replace with function body.


func _on_CheckBox_pressed():
	
	pass # Replace with function body.

func _on_honeycomb_returns(type,data):
	var passphrase = $PanelContainer/VBoxContainer/HBoxContainer/Passphrase.text
	if type == "create_wallet":
		var status = parse_json(data[0])
		if $PanelContainer/VBoxContainer/CheckBox.pressed:
			HoneyComb.set_settings(passphrase)
			print("Saving key")
		else:
			HoneyComb.set_settings("ask")
			print("User will be asked")
		hide()
		HoneyComb.emit_signal("wallet",["created"])
