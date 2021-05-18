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
pid_recorded = False

def launch_html():
    
    subprocess.DETACHED_PROCESS = True
    try:
       HTML_PROCESS = subprocess.Popen(['./HoneyComb-redistributable/service/honeycomb_html.py'],stdout=subprocess.PIPE, stderr=subprocess.PIPE,start_new_session=True)
    except:
       HTML_PROCESS = subprocess.Popen(['/app/bin/HoneyComb-redistributable/service/honeycomb_html.py'],stdout=subprocess.PIPE, stderr=subprocess.PIPE,start_new_session=True)
    
    print("Html Launched ",HTML_PROCESS.pid)

    return HTML_PROCESS

def launch_WebSocket():
    subprocess.DETACHED_PROCESS = True
    try:
        WebSocket_PROCESS = subprocess.Popen(['./HoneyComb-redistributable/service/honeycomb_websocket.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,start_new_session=True)
    except:
        WebSocket_PROCESS = subprocess.Popen(['/app/bin/HoneyComb-redistributable/service/honeycomb_websocket.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,start_new_session=True)
        
    print("WebSocket Launched ",WebSocket_PROCESS.pid)

    return WebSocket_PROCESS


def honeycomb_update(account = "none"):

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
        #print("running update")
        if lastrecord == -1:
            #print("first time, building complete index, This may take a while")
            for i in Hive.get_history(account,-1): 
                DataBase.add_history(account,i)
        else:
            #print("updating the database by",lastchain-lastrecord,"records")
            for i in Hive.get_history(account,lastchain-lastrecord):
                #print("On Hive",i[0])
                latest = DataBase.check_latest("honeycomb","history")["honeycomb"]["data"]
               # print("In Database",latest)
                if i[0] > latest:
                    DataBase.add_history(account,i)
       
    return 1
    
def gather_profile_data(account = "none", update = False):
    
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

def pid_record(pid1,pid2):
    home = os.environ['HOME']
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.config/HoneyComb"):
            os.mkdir(home+"/.config/HoneyComb")
        clear = open(home+"/.config/HoneyComb/honeycomb_pids","w")
        clear.write("")
        clear.close()
        pid_file = open(home+"/.config/HoneyComb/honeycomb_pids","a")
        p = os.getpid()
        pids = {"pids":{"service":p,"html":pid1,"websocket":pid2}}
        pid_file.write(json.dumps(pids))
        pid_file.close()
  
if __name__ == "__main__":   
    try:
        while True:
            uptime +=10
            #print(uptime)
            if HTML_PROCESS == '':
                HTML_PROCESS = launch_html()
           
            if WebSocket_PROCESS == '':
                WebSocket_PROCESS = launch_WebSocket()
                #pid_record(WebSocket_PROCESS.pid)
          
            if HTML_PROCESS != '' and WebSocket_PROCESS != '':
       
                if not pid_recorded:
                    pid_record(HTML_PROCESS.pid,WebSocket_PROCESS.pid)
                    pid_recorded = True
                
                if timeoffset == 3:
                    gather_dynamic_props(True)
                    accounts = DataBase.get_accounts()
                    for a in accounts.keys():
                        gather_profile_data(a,True)
                        if sys.argv[1] == "no_db":
                            honeycomb_update(a)
                    timeoffset = 10
                else:
                    if uptime % 2400 == 0:
                        #print("Updating Dynamic Props")
                        gather_dynamic_props(True)
           
                    elif uptime % 1200 == 0:
                        #print("Updating Profile")
                        accounts = DataBase.get_accounts()
                        for a in accounts.keys():
                            gather_profile_data(a,True)
                            if sys.argv[1] == "no_db":
                                honeycomb_update(a)
            time.sleep(timeoffset)
       
    except KeyboardInterrupt:

        HTML_PROCESS.kill()
        WebSocket_PROCESS.kill()
        sys.exit()

