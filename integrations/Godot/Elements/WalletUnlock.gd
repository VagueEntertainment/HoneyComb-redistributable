extends Control


# Declare member variables here. Examples:
# var a = 2
# var b = "text"


# Called when the node enters the scene tree for the first time.
func _ready():
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
#func _process(delta):
#	pass


func _on_Unlock_pressed():
	HoneyComb.settings["passphrase"] = $PanelContainer/VBoxContainer/HBoxContainer/Passphrase.text
	HoneyComb.passphrase = HoneyComb.settings["passphrase"]
	print(HoneyComb.settings)
	hide()
	HoneyComb.emit_signal("wallet",["unlocked"])
	pass # Replace with function body.


func _on_Cancel_pressed():
	hide()
	pass # Replace with function body.
