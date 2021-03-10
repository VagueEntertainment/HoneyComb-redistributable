#!/usr/bin/python3
import sys
import os
#import sqlite3
import hashlib
import json
import time
import requests
from hive import amount
from hive import hive
from hive import account
from hive import wallet
from hive import hived
sys.path.append("..")
import honeycomb_settings as Settings
import honeycomb_hive_engine as Hive_Engine
w = wallet.Wallet
fix_thy_self = wallet.Wallet()

def hive_init():

    thenodes = ['https://api.hive.blog',
        'https://api.openhive.network',
        'https://anyx.io',
        'https://api.hivekings.com',
        'https://hived.privex.io',
        'https://rpc.ausbit.dev',
        'https://api.pharesim.me',
        'https://techcoderx.com',
        'https://rpc.esteem.app',
        'https://hive.roelandp.nl',
        'https://hived.emre.sh']
    try:
        h = hive.Hive(nodes=thenodes)
        return True
    except:
        return False
    
### Wallet commands
    
def hive_create_wallet():
    
    if not w.created(fix_thy_self):
        settings = Settings.get_settings()
        os.environ["UNLOCK"] = settings["passphrase"]
        w.newWallet(fix_thy_self)
        os.environ.unsetenv("UNLOCK")
        return '{"wallet":"created"}'
    else:
        return '{"wallet":"exists"}'
        
def hive_unlock_wallet():
    settings = Settings.get_settings()
    w.unlock(fix_thy_self,user_passphrase=settings["passphrase"])
    os.environ["UNLOCK"] = settings["passphrase"]
    postingkey = w().getPostingKeyForAccount('bflanagin')
    activekey = w().getActiveKeyForAccount('bflanagin')
    hive.Hive(keys=[postingkey, activekey])
    os.environ.unsetenv("UNLOCK")
    if w.created(fix_thy_self):
        if not w.locked(fix_thy_self):
            return('{"wallet":"unlocked"}')
        else:
            if not w.locked(fix_thy_self):
                return('{"wallet":"unlocked"}')
            else:
                return('{"wallet":"failed"}')
    else:
        return('{"wallet":"error"}')
        
def hive_lock_wallet():
    if w.created(fix_thy_self):
        if not w.locked(fix_thy_self):
            w.lock(fix_thy_self)
            hive.Hive(keys=[])
        return('{"wallet":"locked"}')
    else:
        return('{"wallet":"error"}')
        
def import_account(accountname,keys=[]):
    test = []
    returns = {'wallet':'imported'}
    if w.created(fix_thy_self):
       unlock = json.loads(hive_unlock_wallet())
       if unlock["wallet"] == "unlocked":
            settings = Settings.get_settings()
            for key in keys:
                if w.getAccountFromPrivateKey(fix_thy_self,key) != accountname:
                    returns = {'wallet':'error,incorrect account/key combo.'}
                    break
                else:
                    try:
                        test.append(w.addPrivateKey(fix_thy_self,key))
                    except:
                        pass
       else:
            returns = {'wallet':'locked'}
    else:
        returns = {'wallet':'error'}
    #print(test) 
    return returns
    
def claim_hive_rewards(accountname,rewardtype):
    if hive_init() == True:
        settings = Settings.get_settings()
        if settings["hiveaccount"] == accountname:
            hive_unlock_wallet()
            balance = get_from_hive(["balances"],accountname)["balances"]["rewards"]
            #print(balance)
            reward_hive = balance["HIVE"]
            reward_hbd = balance["HBD"]
            reward_vests = balance["VESTS"]
            if rewardtype == "all":
                hive.Hive().claim_reward_balance(str(reward_hive)+" HIVE", str(reward_hbd)+" HBD", str(reward_vests)+" VESTS", accountname)
            
            hive_lock_wallet()
            return {"rewards":"claimed"}
        else:
            return {"rewards":"error"}
    else:
        return {"rewards":"error"}
        
### General data gathering

def get_transaction_count(account):
    hive_init()
    settings = Settings.get_settings()
    try:
        data = hived.Hived().get_account_history(account,-1,1)
        transaction_count = data[0][0]
    except:
        transaction_count = -1
        
    return transaction_count

def get_dynamic_global_properties():
    hive_init()
    url = "https://api.hive.blog"
    props = {"jsonrpc":"2.0", "method":"condenser_api.get_dynamic_global_properties", "params":[], "id":1}
    data = ""
    try:
       with requests.post(url, json=props) as t:
        data = t.text
        dynamic_props = t.json()
    except:
        pass
        
    return data
    
def get_from_hive(data_type,accountname,opts = []):
    response = {}
    if hive_init() == True:
        for data in data_type:
            if data == "balances":balance = {"balances":account.Account(accountname).get_balances()};response.update({"balances":account.Account(accountname).get_balances()})
            if data == "voting_power":response.update({"vp":account.Account(accountname).voting_power()})
            if data == "reputation":response.update({"rep":account.Account(accountname).reputation()})
            if data == "followers":response.update({"followers":account.Account(accountname).get_followers()})
            if data == "following":response.update({"following":account.Account(accountname).get_following()})
            if data == "rewards":response.update({"rewards":{"HIVE":account.Account(accountname)["reward_hive_balance"],"HBD":account.Account(accountname)["reward_hbd_balance"],"HP":account.Account(accountname)["reward_vesting_hive"]}})
            if data == "profile":response.update({"profile":account.Account(accountname).profile})
            if data == "full_account":response.update({"account":account.Account(accountname)})
            if data == "history":response.update({"history":hived.Hived().get_account_history(accountname,opts[0],opts[1])})
            if data == "RC":response.update(calculate_RC(accountname))
            if data == "delegation":response.update(calculate_delegation(accountname))
            if data == "hivebuzz":response.update({"hivebuzz":hive_buzz_achievements()})
    
    return response

def calculate_RC(account):
    settings = Settings.get_settings()
    global_props = get_dynamic_global_properties()
    fullaccount = get_from_hive(["full_account"],account)["account"]
    totalShares = float(fullaccount["vesting_shares"].split(" ")[0]) + float(fullaccount["received_vesting_shares"].split(" ")[0]) - float(fullaccount["delegated_vesting_shares"].split(" ")[0])
    maxMana = totalShares * 1000000
    elapsed = time.time() - fullaccount["voting_manabar"]["last_update_time"]
    currentMana = float(fullaccount["voting_manabar"]["current_mana"]) + elapsed * maxMana / 432000;

    if currentMana > maxMana:
        currentMana = maxMana
    
    currentManaPerc = currentMana * 100 / maxMana
    
    return {"RC":{"maxRC":maxMana,"currentRC":currentMana,"percentage":currentManaPerc}}

def calculate_delegation(account):
    settings = Settings.get_settings()
    dynamic_props = ""
    try:
        dynamic_props = json.loads(get_dynamic_global_properties())
        fullaccount = get_from_hive(["full_account"],account)["account"]
        delegatedshares = float(fullaccount["received_vesting_shares"].split(" ")[0]) - float(fullaccount["delegated_vesting_shares"].split(" ")[0])
        total_vesting_fund = float(dynamic_props["result"]["total_vesting_fund_hive"].split(" ")[0])
        total_vesting_shares = float(dynamic_props["result"]["total_vesting_shares"].split(" ")[0])
        total = (total_vesting_fund * delegatedshares) / total_vesting_shares
        hiveout = (total_vesting_fund * float(fullaccount["delegated_vesting_shares"].split(" ")[0])) / total_vesting_shares
        hivein = (total_vesting_fund * float(fullaccount["received_vesting_shares"].split(" ")[0])) / total_vesting_shares
    
        return {"delegation":{"out":hiveout,"in":hivein,"total":total}}   
    except:
        return {"delegation":{"out":"error","in":"error","total":"error"}}

def find_type(accountname,post_type,query = [],limit = -1):
    
    settings = Settings.get_settings()
    start = -1
    response = []
    count = 0
    end = 0
    while True:
        if limit != -1 and limit > 1000:
        
            if count + 1000 < limit:
                count += 1000
                output = get_from_hive(["history"],accountname,[start,1000])["history"]
            else:
                end = limit - count 
                output = get_from_hive(["history"],accountname,[start,end])["history"]
                
            for i in output:
                if str(i[1]["op"][0]) == post_type:
                    response.append(i[1]["op"][1])
                                 
            start = output[0][0]-1000
            if end + count >= limit:
                break
            if start < 0:
                break
            else:
                time.sleep(5)
                
        elif limit == -1:
            if start == -1 or start > 1000:
                output = get_from_hive(["history"],accountname,[start,1000])["history"]
            elif start > 0:
                output = get_from_hive(["history"],accountname,[start,start])["history"]
                
          #  print("countdown",output[0][0])
          #  print("complete in ~",((output[0][0] / 1000) * 5) / 60," Minutes")
            for i in output:
                if str(i[1]["op"][0]) == post_type:
                    response.append(i[1]["op"][1])       
            start = output[0][0]-1000
            if start <= 0:
                break
            else:
                time.sleep(5)
                
        elif limit <= 1000:
     
            output = get_from_hive(["history"],accountname,[start,limit])["history"]
            for i in output:
                if str(i[1]["op"][0]) == post_type:         
                    response.append(i[1]["op"][1])
            break
            
    return response
    
    
def get_history(accountname,limit = -1):
    
    settings = Settings.get_settings()
    start = -1
    response = []
    count = 0
    end = 0
    while True:
        if limit != -1 and limit > 1000:
        
            if count + 1000 < limit:
                count += 1000
                output = get_from_hive(["history"],accountname,[start,1000])["history"]
            else:
                end = limit - count 
                output = get_from_hive(["history"],accountname,[start,end])["history"]
                
            for i in output:
                response.append(i)
                                 
            start = output[0][0]-1000
            if end + count >= limit:
                break
            if start < 0:
                break
            else:
                time.sleep(5)
                
        elif limit == -1:
            if start == -1 or start > 1000:
                output = get_from_hive(["history"],accountname,[start,1000])["history"]
            elif start > 0:
                output = get_from_hive(["history"],accountname,[start,start])["history"]
                
          #  print("countdown",output[0][0])
          #  print("complete in ~",((output[0][0] / 1000) * 5) / 60," Minutes")
            for i in output:
                response.append(i)
                       
            start = output[0][0]-1000
            if start <= 0:
                break
            else:
                time.sleep(5)
                
        elif limit <= 1000:
     
            output = get_from_hive(["history"],accountname,[start,limit])["history"]
            for i in output:      
                response.append(i)
                
            break
            
    return response
    
def hive_buzz_achievements(accountname):
    comments = find_type(accountname,"comment",[],-1)
    posts = []
    achievements = []
    for c in comments:
        if c["author"] == 'hivebuzz' or c["author"] == 'steemitboard':
            achievements.append(c)
        if c["parent_author"] == "" and c["author"] == accountname:
            posts.append(c)
            
    return achievements

######################################################
#
# HoneyComb specfic commands
#
######################################################

            
#### To Hive

### Registers client to the projecthoneycomb account.
def register_client(account):
    hive_init()
    settings = Settings.get_settings()
    balances = get_from_hive(["balances"],account)
    HBD = balances["available"]["HBD"]
    HIVE = balances["available"]["HIVE"]
    hive_unlock_wallet()
    if HIVE > 0.001:
        recipient = "projecthoneycomb"
        amount = 0.001
        asset = "HIVE"
        memo = json.dumps({"clientid":settings["clientid"],"action":"register","version":"1.0"})
        connection_points = find_connection_point(username,app="com.vagueentertainment.honeycomb") 
        if not registration_check():
            hive.Commit().transfer(recipient, float(amount), asset, memo, account)
                       
    hive_lock_wallet()
    
    return {"user":'registered'}

    
### To help others find you we update them everytime your public_IP changes. We should move this to the clients p2p features.
def update_client_loc(account,app="com.vagueentertainment.honeycomb"):
    hive_init()
    public_IP = requests.get("https://www.wikipedia.org").headers["X-Client-IP"]
    settings = Settings.get_settings()
    custom_json = {"ip":public_IP,"timestamp":time.time(),"clientid":settings["clientid"],"app":app}
    wallet = json.loads(hive_unlock_wallet())
    if wallet["wallet"] == "unlocked":
        points = find_connection_point(account,app)
        same_ip = False
        for p in points:
            if p["data"]["ip"] == public_IP:
                same_ip = True
                break
            if same_ip == False:        
                hive.Commit().custom_json("honeycomb-app-ping",custom_json,required_posting_auths=[account])
                
        hive_lock_wallet()
        
    return {"client_loc":"updated","ip":public_IP}
    
### From Hive

# Check user registration

def registration_check(account):
    hive_init()
    find = find_type("projecthoneycomb","transfer")
    found = False
    settings = Settings.get_settings()
    memo = {"honeycomb":"error"}
    for transfer in find:
       
        try:
            memo = json.loads(transfer["memo"])
        except:
            pass
        if memo["honeycomb"] != "error":
        
            if transfer["from"] == account: 
                if memo["honeycomb"]["clientid"] == settings["clientid"]:
                    if "action" in memo["honeycomb"].keys() and memo["honeycomb"]["action"] == "register":
                        found = True
                        break
        
    return found
    
# Find other users

def find_users(account):
    hive_init()
    find = find_type("projecthoneycomb","transfer")
    settings = Settings.get_settings()
    user_list = []
    memo = {"honeycomb":"error"}
    for users in find:
    
        try:
            memo = json.loads(transfer["memo"])
        except:
            pass
        if memo["honeycomb"] != "error":
            if users["from"] != account:
                if "action" in memo["honeycomb"].keys() and memo["honeycomb"]["action"] == "register":
                    user_list.append(user)
                    
    return {"userlist":user_list}
   
# Find other clients for selected user. Clients are other computers registered to an account.

def find_user_clients(useraccount,account):
    hive_init()
    find = find_type("projecthoneycomb","transfer")
    settings = Settings.get_settings()
    clients_list = []
    memo = {"honeycomb":"error"}
    for clients in find:
    
        try:
            memo = json.loads(transfer["memo"])
        except:
            pass
        if memo["honeycomb"] != "error":
            if users["from"] == account:
                if "action" in memo["honeycomb"].keys() and memo["honeycomb"]["action"] == "register":
                    user_list.append(user)
                    
    return {"clients_list":clients_list}

# gather client ips for remote user

def find_connection_point(username,app="com.vagueentertainment.honeycomb"):
    hive_init()
    find = find_type(username,"custom_json",[],1000)
    settings = Settings.get_settings()
    client_list = []
    custom_json = {"honeycomb":"error"}
    for clients in find:
        if clients["id"] == "honeycomb-app-ping":
            try:
                custom_json = json.loads(clients["json"])
            except:
                pass
        if custom_json["honeycomb"] != "error":
            if custom_json["honeycomb"]["app"] == app:
                if {'account':username,'data':{'clientid':custom_json["honeycomb"]["clientid"],"ip":custom_json["honeycomb"]["ip"]}} not in client_list:
                    client_list.append({'account':username,'data':{'clientid':custom_json["honeycomb"]["clientid"],"ip":custom_json["honeycomb"]["ip"]}})
                    
    return client_list


