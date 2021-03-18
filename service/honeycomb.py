#!/usr/bin/env python3

import subprocess
import sys
import os
import json
import time
import requests
import asyncio

sys.path.append("..")

import honeycomb_settings as Settings
import honeycomb_db as DataBase
import honeycomb_hive as Hive

settings = Settings.get_settings()

HTML_PROCESS = ''
WebSocket_PROCESS = ''
uptime = 0
timeoffset = 3

def launch_html():
    
    subprocess.DETACHED_PROCESS = True
    HTML_PROCESS = subprocess.Popen(['./HoneyComb-redistributable/service/honeycomb_html.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,start_new_session=True)
    print("Process Launched")

    return HTML_PROCESS

def launch_WebSocket():
    subprocess.DETACHED_PROCESS = True
    WebSocket_PROCESS = subprocess.Popen(['./HoneyComb-redistributable/service/honeycomb_websocket.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,start_new_session=True)
    print("Process Launched")

    return WebSocket_PROCESS

def honeycomb_update(account = settings["hiveaccount"]):

    DataBase.create_db()
    # Get the latest recorded transaction for account in database
    hive = ""
    latest = DataBase.check_latest("honeycomb","history")
    lastrecord = 0
    lastchain = 0
    if latest["honeycomb"]["table"] == "history":
        lastrecord =latest["honeycomb"]["data"]

    # Get the latest recorded transaction for the account on the chain
        
    lastchain = Hive.get_transaction_count(account)
      
    if lastrecord < lastchain:
        print("running update")
        if lastrecord == -1:
            print("first time, building complete index")
            for i in Hive.get_history(account,-1): 
                DataBase.add_history(i)
        else:
            print("updating the database by",lastchain-lastrecord,"records")
            for i in Hive.get_history(account,lastchain-lastrecord):
                print("On Hive",i[0])
                latest = DataBase.check_latest("honeycomb","history")["honeycomb"]["data"]
                print("In Database",latest)
                if i[0] > latest:
                    DataBase.add_history(i)
       
    return 1
    
def gather_profile_data(account = settings["hiveaccount"], update = False):
    
    DataBase.create_db()
    userinfo = DataBase.check_latest("honeycomb","account",["ACCOUNT",account])

    if userinfo["honeycomb"]["data"] == -1 or update == True:
        profile = Hive.get_from_hive(["full_account"],account)
        balances = Hive.get_from_hive(["balances"],account)
        followers = Hive.get_from_hive(["followers"],account)
        following = Hive.get_from_hive(["following"],account)
        delegation = Hive.get_from_hive(["delegation"],account)
        DataBase.set_account_info(account,"profile",json.dumps(profile["account"]["json_metadata"]["profile"]))
        
        available = balances["balances"]['available']
        savings = balances["balances"]['savings']
        
        print(account)
        print(update)
        print(available)
        
        DataBase.set_account_info(account,"HBD",json.dumps({"available":available["HBD"],"savings":savings["HBD"]}))
        DataBase.set_account_info(account,"HIVE",json.dumps({"available":available["HIVE"],"savings":savings["HIVE"]}))
        DataBase.set_account_info(account,"VESTS",json.dumps({"available":available["VESTS"],"savings":0}))
        DataBase.set_account_info(account,"LAST_TRANSACTION",Hive.get_transaction_count(account))
        DataBase.set_account_info(account,"FOLLOWERS",str(followers["followers"]).split("[")[1].split("]")[0].replace("'",""))
        DataBase.set_account_info(account,"FOLLOWING",str(following["following"]).split("[")[1].split("]")[0].replace("'",""))
        DataBase.set_account_info(account,"DELEGATION",json.dumps(delegation["delegation"]))
        
    return 1
    
def gather_dynamic_props(update = False):
    DataBase.create_db()
    exists = DataBase.check_latest("honeycomb","misc",["SEARCH_KEY",'hive_dgp'])
    if exists["honeycomb"]["data"] == -1 or update == True:
        dynamic_ops = Hive.get_dynamic_global_properties()
        #print(dynamic_ops)
        DataBase.add_misc(["hive_dgp",dynamic_ops,"global"])
   
try:
    while True:
       uptime +=30
       DataBase.create_db()
       if HTML_PROCESS == '' or WebSocket_PROCESS == '':
            print("Launching Process")
            #HTML_PROCESS = launch_html()
            HTML_PROCESS = 1
            #print(HTML_PROCESS.pid)
            #WebSocket_PROCESS = launch_WebSocket()
            WebSocket_PROCESS = 2
            #print(WebSocket_PROCESS.pid)
       else:
        honeycomb_update()
        if timeoffset == 3:
          gather_dynamic_props(True)
          accounts = DataBase.get_accounts()
          for a in accounts.keys():
             gather_profile_data(a,True)
             timeoffset = 300
        else:
            if uptime % 240 == 0:
               print("Updating Dynamic Props")
               gather_dynamic_props(True)
           
            elif uptime % 60 == 0:
               print("Updating Profile")
               accounts = DataBase.get_accounts()
               for a in accounts.keys():
                   gather_profile_data(a,True)
           
       time.sleep(timeoffset)
       
except KeyboardInterrupt:
        #os.kill(HTML_PROCESS,signal.SIGKILL)
        #os.kill(WebSocket_PROCESS,signal.SIGKILL)
        sys.exit()
        


