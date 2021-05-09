#!/usr/bin/python3

import subprocess
import sys
import os
import sqlite3
import json
import time
import requests

sys.path.append("..")
import honeycomb_settings as Settings

def create_db():
    home = os.environ['HOME']
    conn = ''
    if Settings.get_platform() == "Linux":
    
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")
            
        if not os.path.exists(home+"/.local/share/HoneyComb/cache"):
            os.mkdir(home+"/.local/share/HoneyComb/cache")
            
        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
        
    conn.execute ('''CREATE TABLE IF NOT EXISTS known_users
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ACCOUNT TEXT NOT NULL,
                            CLIENTID TEXT NOT NULL,
                            APP TEXT,
                            IP  TEXT,
                            LASTSEEN INT);''')
                            
    conn.execute ('''CREATE TABLE IF NOT EXISTS account
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ACCOUNT TEXT NOT NULL UNIQUE,
                            PROFILE TEXT,
                            LAST_TRANSACTION INT,
                            FOLLOWERS TEXT,
                            FOLLOWING TEXT,
                            APP_LIST TEXT,
                            HIVE TEXT,
                            HBD TEXT,
                            VESTS TEXT,
                            DELEGATION TEXT,
                            CLIENT_LIST  TEXT);''')
    
    conn.execute ('''CREATE TABLE IF NOT EXISTS history
                        (ID INTEGER PRIMARY KEY UNIQUE,
                        ACCOUNT TEXT,
                        TYPE TEXT NOT NULL,
                        AUTHOR TEXT,
                        PARENT_AUTHOR TEXT,
                        CURATOR TEXT,
                        VOTER TEXT,
                        TRANSACTION_ID TEXT,
                        BODY TEXT,
                        TITLE TEXT,
                        PERMLINK TEXT,
                        METADATA TEXT);''')
                        
    conn.execute('''CREATE TABLE IF NOT EXISTS misc
                        (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                        ACCOUNT TEXT NOT NULL UNIQUE,
                        SEARCH_KEY TEXT NOT NULL UNIQUE,
                        DATA TEXT NOT NULL
                        );''')
                        
                            
    conn.close()
        

def create_app_db(appname):
    home = os.environ['HOME']
    conn = ''
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")
            
        conn = sqlite3.connect(home+"/.local/share/HoneyComb/"+appname+".db")
    
    # Custom Data, for non-standard honeycomb functions
    conn.execute ('''CREATE TABLE IF NOT EXISTS custom_data
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ENTRY TEXT NOT NULL UNIQUE);''')
    
    # Highscore data                        
    conn.execute ('''CREATE TABLE IF NOT EXISTS high_score
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ENTRY TEXT NOT NULL UNIQUE);''')
    # Saved Games            
    conn.execute ('''CREATE TABLE IF NOT EXISTS saved_game
                            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                            ENTRY TEXT NOT NULL UNIQUE);''')
        
    conn.close()
 
 
def check_latest(dbname,table,search = []):
    home = os.environ['HOME']
    conn = ''
    rowcount = -1
    response = {}
    cursor = None
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/"+dbname+".db")
    
    if conn != '':
        if search == []:
            cursor = conn.execute("SELECT * FROM "+table+" ORDER by ID DESC")
        else:
            cursor = conn.execute("SELECT * FROM "+table+" WHERE "+search[0]+" IS '"+search[1]+"' ORDER by ID DESC")
            
        test = cursor.fetchone()
        if test != None:
            last = test[0]
            response = {"honeycomb":{"database":dbname,"table":table,'data':last}}
        else:
            response = {"honeycomb":{"database":dbname,"table":table,'data':-1}}

        conn.close()
        
    return response

### Add / Update Functions

def add_misc(data):
     #print(data)
     home = os.environ['HOME']
     conn = ''
     #response = {"honeycomb":{"database":"honeycomb","table":"misc","
     if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")
            
        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
        #print("Opened database successfully")
     if conn != '':
        search = "SELECT * FROM misc WHERE SEARCH_KEY IS '"+data[0]+"' AND ACCOUNT IS '"+data[2]+"'"
        query = conn.execute(search)
        test = query.fetchone()
        if test == None:
            vals = [data[2],data[0],data[1]]
            add = "INSERT INTO misc (ACCOUNT,SEARCH_KEY,DATA) VALUES (?,?,?)"
            conn.execute(add,vals)
        else:
            vals = [data[1],data[0],data[2]]
            update = "UPDATE misc SET DATA = ? WHERE SEARCH_KEY IS ? AND ACCOUNT IS ?"
            conn.execute(update,vals)
            
        conn.commit()
        conn.close()

def add_history(account,data):
    home = os.environ['HOME']
    conn = ''
    rowcount = -1
    response = {}
    
    ID = data[0]
    TYPE = data[1]["op"][0]
    AUTHOR = ""
    PARENT_AUTHOR = ""
    CURATOR = ""
    VOTER = ""
    TRANSACTION_ID = ""
    BODY = "" 
    TITLE = ""
    PERMLINK = ""
    METADATA = ""
    ACCOUNT = account
    
    if "author" in data[1]["op"][1]:
        AUTHOR = data[1]["op"][1]["author"]
    if "parent_author" in data[1]["op"][1]:
        PARENT_AUTHOR = data[1]["op"][1]["parent_author"]
    if "comment_author" in data[1]["op"][1]:
        PARENT_AUTHOR = data[1]["op"][1]["comment_author"]
    if "curator" in data[1]["op"][1]:
        CURATOR = data[1]["op"][1]["curator"]
    if "voter" in data[1]["op"][1]:
        VOTER = data[1]["op"][1]["voter"]
    if "id" in data[1]["op"][1]:
        TRANSACTION_ID = data[1]["op"][1]["id"]
    if "body" in data[1]["op"][1]:
        BODY = data[1]["op"][1]["body"]
    if "title" in data[1]["op"][1]: 
        TITLE = data[1]["op"][1]["title"]
    if "permlink" in data[1]["op"][1]:
        PERMLINK = data[1]["op"][1]["permlink"]
    if "comment_permlink" in data[1]["op"][1]:
        PERMLINK = data[1]["op"][1]["comment_permlink"]
    if "metadata" in data[1]["op"][1]:
        METADATA = data[1]["op"][1]["metadata"]
    if "json" in data[1]["op"][1]:
        METADATA = data[1]["op"][1]["json"]
    if "json_metadata" in data[1]["op"][1]:
        METADATA = data[1]["op"][1]["json_metadata"]
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
        #print("Opened database successfully")
    if conn != '':
        vals = [ID,ACCOUNT,TYPE,AUTHOR,PARENT_AUTHOR,CURATOR,VOTER,TRANSACTION_ID,BODY,TITLE,PERMLINK,METADATA]
        conn.execute("INSERT INTO history (ID,ACCOUNT,TYPE,AUTHOR,PARENT_AUTHOR,CURATOR,VOTER,TRANSACTION_ID,BODY,TITLE,PERMLINK,METADATA) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",vals)
        conn.commit()
        conn.close()
        try:
            jsoned = json.loads(METADATA)
        except:
            pass
        else:
           # print(jsoned)
            if jsoned is dict:
                if "image" in jsoned.keys():
                    cache_img(jsoned["image"])
            else:
                if "image" in jsoned:
                    cache_img(jsoned["image"])


def set_app_data(accountname,field,data):
    home = os.environ['HOME']
    conn = ''
    rowcount = -1
    response = {}
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
        #print("Opened database successfully")
    if conn != '':
        vals = [ID,TYPE,AUTHOR,PARENT_AUTHOR,CURATOR,VOTER,TRANSACTION_ID,BODY,TITLE,PERMLINK,METADATA]
        conn.execute("INSERT INTO history (ID,TYPE,AUTHOR,PARENT_AUTHOR,CURATOR,VOTER,TRANSACTION_ID,BODY,TITLE,PERMLINK,METADATA) VALUES (?,?,?,?,?,?,?,?,?,?,?)",vals)
        conn.commit()
        conn.close()
    
    return response

def set_account_info(accountname,field,data):
    home = os.environ['HOME']
    conn = ''
    rowcount = -1
    response = {}
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
        #print("Opened database successfully")
    if conn != '':
    
        search = "SELECT ? FROM account WHERE ACCOUNT = ?"
        cursor = conn.execute(search,[field,accountname])
        test = cursor.fetchone()
        if test == None:
            vals = [accountname,data]
            conn.execute("INSERT INTO account (ACCOUNT,"+field.upper()+") VALUES (?,?)",vals)
        else:
            vals = [data,accountname]
            conn.execute("UPDATE account SET "+field.upper()+" = ? WHERE ACCOUNT = ?",vals)
        conn.commit()
        conn.close()
    
    return response

### Retrieval Functions

def get_from_history(cat,account,limit = -1):
    home = os.environ['HOME']
    conn = ''
    response = {}
    history_list = []
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
    
    if conn != '':
        for c in cat:
            if limit == -1:
                cursor = conn.execute("SELECT BODY,METADATA FROM history WHERE TYPE = ? AND ACCOUNT = ? ORDER by ID DESC",[c,account])
            form_DB = cursor.fetchall()
            for row in form_DB:
                history_list.append({"body":row[0],"metadata":row[1]})
            
    conn.close()
    response = {"history":history_list}    
    return response
    
def get_from_account(accountname,fields):
    home = os.environ['HOME']
    conn = ''
    response = {"account":{"name":accountname}}
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
    
    if conn != '':
        for field in fields:
            if field.split(" ")[0].upper() != "BALANCES":
                try:
                    cursor = conn.execute("SELECT "+field.split(" ")[0].upper()+" FROM account WHERE ACCOUNT IS ?",[accountname])
                    from_DB = cursor.fetchall()[0][0]
                    if field.split(" ")[0].upper() == "PROFILE":
                        response["account"].update({field.split(" ")[0]:json.loads(from_DB)})
                    elif field.split(" ")[0].upper() == "FOLLOWING" or field.split(" ")[0].upper() == "FOLLOWERS":
                        response["account"].update({field.split(" ")[0]:from_DB.split(",")})
                    elif field.split(" ")[0].upper() == "DELEGATION":
                        response["account"].update({field.split(" ")[0]:json.loads(from_DB)})
                except:
                    pass
            else:
                cursor = conn.execute("SELECT HIVE,HBD,VESTS FROM account WHERE ACCOUNT IS ?",[accountname])
                from_DB = cursor.fetchall()[0]     
                response.update({field.split(" ")[0]:
                            {"totals":
                              {"HIVE":json.loads(from_DB[0]),
                               "HBD":json.loads(from_DB[1]),
                               "VESTS":json.loads(from_DB[2])}             
                            }
                       })
            
        conn.close()
        
    return response
    
    
def get_from_misc(types):
    home = os.environ['HOME']
    conn = ''
    response = {"misc":{}}
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
    
    if conn != '':
     for typename in types:
        cursor = conn.execute("SELECT DATA FROM misc WHERE ? IS NOT NULL ORDER by ID DESC",[typename])
        from_DB = cursor.fetchall()[0]
        #print(from_DB)
        response["misc"].update({typename:
                        {"data":json.loads(from_DB[0])           
                        }
                     }
                    )
    conn.close()
    return response

def get_from_app(appname,field):
    home = os.environ['HOME']
    conn = ''
    response = {}
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/"+appname+".db")
    
    if conn != '':
        cursor = conn.execute("SELECT * FROM "+appname+" WHERE ? IS NOT NULL ORDER by ID DESC",[field])
        print(cursor.fetchall())
    
    return response
    
def get_accounts():
    home = os.environ['HOME']
    conn = ''
    response = {}
    
    if Settings.get_platform() == "Linux":
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")

        conn = sqlite3.connect(home+"/.local/share/HoneyComb/honeycomb.db")
    
    if conn != '':
        cursor = conn.execute("SELECT ACCOUNT,PROFILE FROM account WHERE 1")
        from_DB = cursor.fetchall()
        for a in from_DB:
            profile = json.loads(a[1])["name"]
            account = a[0]
            response.update({account:{"name":profile}})
    return response

### Utilties

#def add_account(name):
    
    

def cache_img(url):
    home = os.environ['HOME']
    cachedir = ""
    if Settings.get_platform() == "Linux":
        cachedir = home+"/.local/share/HoneyComb/cache"
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")
            
        if not os.path.exists(cachedir):
            os.mkdir(cachedir)
    for u in url:
        try:        
            with requests.get(u) as r:
                data = r.content
                filename = u.split("/")[-1]
                file = open(cachedir+"/"+str(filename),"wb")
                file.write(data)
                file.close()
        except:
            pass
       
def image_retrieval(url):

    home = os.environ['HOME']
    cachedir = ""
    if Settings.get_platform() == "Linux":
        cachedir = home+"/.local/share/HoneyComb/cache"
        if not os.path.exists(home+"/.local/share/HoneyComb"):
            os.mkdir(home+"/.local/share/HoneyComb")
            
        if not os.path.exists(cachedir):
            os.mkdir(cachedir)
    
    filename = url.split("/")[-1]
    if os.path.exists(cachedir+"/"+str(filename)):
        opened = open(cachedir+"/"+str(filename),"rb")
        o = opened.read()
        opened.close()
        return(o)
    else:
        try:        
          with requests.get(url) as r:
               data = r.content
               file = open(cachedir+"/"+str(filename),"wb")
               file.write(data)
               file.close()
               return(data)
        except:
          pass

