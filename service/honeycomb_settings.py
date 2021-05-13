#!/usr/bin/env python3

import sys
sys.path.append("..")
sys.path.append("../service")

import json
import os
import sqlite3
import netifaces
from hashlib import sha256

### Create local files

### Checks for the existance of the settings file and folder, creates if needed.
### Needed if statements

### Windows
### Mac

def check_settings_file():
    home = os.environ['HOME']
    if get_platform() == "Linux":
        if not os.path.exists(home+"/.config/HoneyComb"):
            os.mkdir(home+"/.config/HoneyComb")
            
        if os.path.exists(home+"/.config/HoneyComb/honeycomb_settings.json"):
            #print("Found file")
            return "found"
        else:
            #print("No Settings file found")
            return "missing"
            
### Saves settings in OSes default configuration saving area
### Needed if statements

### Windows
### Mac
	
def save_settings(passphrase ="none"):
    home = os.environ['HOME']
    if get_platform() == "Linux":
        if not os.path.exists(home+"/.config/HoneyComb"):
            os.mkdir(home+"/.config/HoneyComb")
            
        settings_file = open(home+"/.config/HoneyComb/honeycomb_settings.json","w")
        settings = {"clientid":generate_client_id(),"passphrase":passphrase,"gateway_port":8080}
        settings_file.write(json.dumps(settings))
        settings_file.close()
        
    return settings
        
### Loads settings from the file and returns them for use in HoneyComb. 
### Needed if statements:

### Windows
### Mac
        
def get_settings():
    home = os.environ['HOME']
    settings = {}
    if get_platform() == "Linux" and check_settings_file() == "found":
        settings_file = open(home+"/.config/HoneyComb/honeycomb_settings.json","r")
        settings = json.loads(settings_file.read())
        settings_file.close()
        
    else:
        settings = {"clientid":generate_client_id(),"passphrase":"none","gateway_port":8675} 
    
    return settings

### We generate the client id using the mac address of the available nics + the users home directory and name.
### This id is used to help route clients to possible private data stores so scrambling the data isn't important 	
def generate_client_id():
    client_id = sha256()
    client_inf = ""
    env = ""
    for inf in netifaces.interfaces():
     client_inf += netifaces.ifaddresses(inf)[17][0]['addr']
    
    env += os.environ["USER"]+"::"
    env += os.environ["HOME"]+"::"
    client_id.update(env.encode())
    client_id.update(client_inf.encode())
    client_id.update(env.encode())
    
    return client_id.hexdigest()

### Just a typical boiler plate platform getter
    
def get_platform():
    platforms = {
        'linux' : 'Linux',
        'linux1' : 'Linux',
        'linux2' : 'Linux',
        'darwin' : 'OS X',
        'win32' : 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]
    
