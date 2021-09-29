extends Control


# Declare member variables here. Examples:
# var a = 2
# var b = "text"
var page1
var page2
var page3
var page4
var currentpage = 0
signal current_change(view)

var account = ""
var postingkey = ""
var activekey = ""

var WindowHeight
var WindowWidth

# Called when the node enters the scene tree for the first time.
func _ready():
	WindowHeight = OS.get_window_size().y
	WindowWidth = OS.get_window_size().x
	HoneyComb.connect("honeycomb_returns",self,"_on_honeycomb_returns")
	page1 = $NewAccountWizard/VBoxContainer/HBoxContainer/Page1
	page2 = $NewAccountWizard/VBoxContainer/HBoxContainer/Page2
	page3 = $NewAccountWizard/VBoxContainer/HBoxContainer/Page3
	#page4 = $NewAccountWizard/VBoxContainer/HBoxContainer/Page4
	page1.pressed = true
	emit_signal("current_change",0)
	pass # Replace with function body.


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	if WindowHeight != OS.get_window_size().y or WindowWidth != OS.get_window_size().x:
		var scaleShiftY = OS.get_window_size().y / WindowHeight
		var scaleShiftX =  OS.get_window_size().x / WindowWidth
		self.rect_scale = Vector2(scaleShiftX,scaleShiftY)
		self.rect_pivot_offset = Vector2(WindowWidth/2,WindowHeight/2)

	
	if currentpage == 0:
		$NewAccountWizard/Control/Back.hide()
	else:
		if !$NewAccountWizard/Control/Back.visible:
			$NewAccountWizard/Control/Back.show()
	if currentpage == 2:
		$NewAccountWizard/Control/Next.hide()
	else:
		if !$NewAccountWizard/Control/Next.visible:
			$NewAccountWizard/Control/Next.show()
	pass


func _on_Page1_pressed():
	
	emit_signal("current_change",0)
	currentpage = 0
	pass # Replace with function body.


func _on_Page2_pressed():
	
	emit_signal("current_change",1)
	currentpage = 1
	pass # Replace with function body.


func _on_Page3_pressed():
	
	emit_signal("current_change",2)
	currentpage = 2
	pass # Replace with function body.

func _on_Page4_pressed():
	emit_signal("current_change",3)
	currentpage = 3
	pass # Replace with function body.


func _on_Login_current_change(view):
	match view:
		0:
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer1.show()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer2.hide()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer3.hide()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer4.hide()
			page1.get_node("active").show()
			page1.pressed = true
			if page2.is_pressed():
				page2.pressed = false
				page2.get_node("active").hide()
			if page3.is_pressed():
				page3.pressed = false
				page3.get_node("active").hide()
			#if page4.is_pressed():
			#	page4.pressed = false
			#	page4.get_node("active").hide()
	
		1:
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer1.hide()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer2.show()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer3.hide()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer4.hide()
			page2.get_node("active").show()
			page2.pressed = true
			if page1.is_pressed():
				page1.pressed = false
				page1.get_node("active").hide()
			if page3.is_pressed():
				page3.pressed = false
				page3.get_node("active").hide()
			#if page4.is_pressed():
			#	page4.pressed = false
			#	page4.get_node("active").hide()
			#	
		2:
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer1.hide()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer2.hide()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer3.show()
			$NewAccountWizard/VBoxContainer/Panel/PanelContainer4.hide()
			page3.get_node("active").show()
			page3.pressed = true
			if page1.is_pressed():
				page1.pressed = false
				page1.get_node("active").hide()
			if page2.is_pressed():
				page2.pressed = false
				page2.get_node("active").hide()
			#if page4.is_pressed():
			#	page4.pressed = false
			#	page4.get_node("active").hide()
		#3:
		#	$NewAccountWizard/VBoxContainer/Panel/PanelContainer1.hide()
		#	$NewAccountWizard/VBoxContainer/Panel/PanelContainer2.hide()
		#	$NewAccountWizard/VBoxContainer/Panel/PanelContainer3.hide()
		#	$NewAccountWizard/VBoxContainer/Panel/PanelContainer4.show()
		#	page4.get_node("active").show()
		#	page4.pressed = true
		#	if page1.is_pressed():
		#		page1.pressed = false
		#		page1.get_node("active").hide()
		#	if page2.is_pressed():
		#		page2.pressed = false
		#		page2.get_node("active").hide()
		#	if page3.is_pressed():
		#		page3.pressed = false
		#		page3.get_node("active").hide()
				
			
			
	pass # Replace with function body.


func _unhandled_key_input(event):
	if visible:
		if event.pressed and event.scancode == KEY_LEFT:
			if currentpage > 0:
				currentpage -= 1
				emit_signal("current_change",currentpage)
						
		if event.pressed and event.scancode == KEY_RIGHT:
			if currentpage < 2:
				currentpage += 1
				emit_signal("current_change",currentpage)
				


func _on_Login_visibility_changed():
	if visible:
		grab_click_focus()
		grab_focus()
	pass # Replace with function body.


func _on_Label3_meta_clicked(meta):
	print(meta)
	OS.execute("xdg-open", [meta], false)
	pass # Replace with function body.


func _on_Close_pressed():
	hide()
	pass # Replace with function body.


func _on_connect_pressed():
	account = $NewAccountWizard/VBoxContainer/Panel/PanelContainer3/VBoxContainer/HBoxContainer/VBoxContainer/account.text
	activekey = $NewAccountWizard/VBoxContainer/Panel/PanelContainer3/VBoxContainer/HBoxContainer/VBoxContainer/activekey.text
	postingkey = $NewAccountWizard/VBoxContainer/Panel/PanelContainer3/VBoxContainer/HBoxContainer/VBoxContainer/postingkey.text
	HoneyComb.add_account(account,{"posting":postingkey,"active":activekey})
	#hide()
	pass # Replace with function body.





func _on_Next_pressed():
	if currentpage < 2:
		currentpage += 1
		emit_signal("current_change",currentpage)
	pass # Replace with function body.


func _on_Back_pressed():
	if currentpage > 0:
		currentpage -= 1
		emit_signal("current_change",currentpage)
	pass # Replace with function body.

func _on_honeycomb_returns(type,data):
	if type == "add_account":
		var returned = parse_json(data[0])
		print(returned)
		if returned["honeycomb"]["hive"]["wallet"] == "imported":
			hide()
			HoneyComb.emit_signal("wallet",["imported",account])
	pass
