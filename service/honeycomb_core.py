#!/usr/bin/python3

import subprocess
import sys
import os
import sqlite3
import json
import time

sys.path.append("..")

import honeycomb_hive as Hive
import honeycomb_settings as Settings
import honeycomb_hive_engine as Hive_Engine
import honeycomb_db as Database


from bottle import route, run, template, request, static_file

settings = Settings.get_settings()


def message(interface,data):
    response = {"honeycomb":{"code":100,"msg":"Please issue a command to continue"}}
    #print(interface,data)
    try:
        from_client = json.loads(data)
    except:
        print("failed to parse "+data)
        return json.dumps({"honeycomb":{"code":101,"msg":"messages must be in json formated string"}})
    else:
        act = from_client["act"]
        response ={"honeycomb":{"code":200}}
        for a in act:
        
        # From local stores
        
        # Settings file
            if a == "get_settings" and interface == "service":
                if "settings" not in response:
                    response["honeycomb"]["settings"] = {}
                response["honeycomb"]["settings"].update(Settings.get_settings())
            elif a == "check_settings" and interface == "service":
                if "settings" not in response:
                    response["honeycomb"]["settings"] = {}
                response["honeycomb"]["settings"]["file"] = Settings.check_settings_file()
            elif a == "save_settings" and interface == "service":
                response["honeycomb"]["settings"].update(Settings.save_settings(from_client["account"],from_client["passphrase"]))
            
        # Database functions
        
            if a == "get_history" and interface == "service":
                response["honeycomb"]["database"] = Database.get_from_history(from_client["type"],from_client["account"])
           
            elif a == "get_app_data" and interface == "service":
                response["honeycomb"]["database"] = Database.get_from_app()
                
        # Account functions
        
            elif a == "add_account" and interface == "service":
                wallet = Hive.import_account(from_client["account"],from_client["keys"])
                #print(wallet)
                profile = Hive.get_from_hive(["profile"],from_client["account"],[])
               # print(profile)
                if wallet["wallet"] == "imported":
                    Database.set_account_info(from_client["account"],"profile",json.dumps(profile["profile"]))
                    
            elif a == "get_accounts" and interface == "service":
                response["honeycomb"]["accounts"] = Database.get_accounts()
                
            elif a == "get_account" and interface == "service":
                if "params" in from_client.keys():
                    types = from_client["params"]["get_account"]
                    response["honeycomb"]["database"] = Database.get_from_account(from_client["account"],types)
                else:
                    response["honeycomb"]["database"] = Database.get_from_account(from_client["account"],from_client["type"])
            
        # Direct from Hive
        
            elif a ==  "create_wallet" and interface == "service":
                response["honeycomb"]["hive"] = Hive.hive_create_wallet()
            elif a == "import_account" and interface == "service":
                response["honeycomb"]["hive"] = Hive.import_account(from_client["account"],from_client["keys"])
            elif a == "get_from_hive" and interface == "service":
                 if "params" in from_client.keys():
                    types = from_client["params"]["get_from_hive"]
                    response["honeycomb"]["hive"] = Hive.get_from_hive(types,from_client["account"],from_client["opts"])
                 else:
                    response["honeycomb"]["hive"] = Hive.get_from_hive(from_client["type"],from_client["account"],from_client["opts"])
            elif a == "get_hive_dynamic_props" and interface == "service":
                #response = Hive.get_dynamic_global_properties()
                response["honeycomb"]["hive"] = Database.get_from_misc(['hive_dgp'])
            elif a == "claim_hive_rewards" and interface == "service":
                response["honeycomb"]["hive"] = Hive.claim_hive_rewards(from_client["account"],from_client["type"])
            
        # Direct from Hive Engine
        
            elif a == "hive_engine_search" and interface == "service":
                response["honeycomb"]["hive_engine"] = Hive_Engine.find_on_hive_engine(from_client["query"],from_client["token"],from_client["opt"])
            elif a == "get_nftshowroom_art" and interface == "service":
                response["honeycomb"]["hive_engine"] = {"nftshowroom":Hive_Engine.get_nftshowroom_art(from_client["account"],from_client["type"])}
                #print(response)
            elif a == "get_from_hive_engine" and interface == "service":
                if "params" in from_client.keys():
                    types = from_client["params"]["get_from_hive_engine"]
                    response["honeycomb"]["hive_engine"]= Hive_Engine.get_from_hive_engine(types,from_client["account"])
                else:
                    response["honeycomb"]["hive_engine"]= Hive_Engine.get_from_hive_engine(from_client["type"],from_client["account"])
        
        # HoneyComb Specific
            
        # To Hive
        
            elif a == "register_client" and interface == "service":
                response["honeycomb"]["to_hive"] = Hive.register_client()
            elif a == "update_loc" and interface == "service":
                response["honeycomb"]["to_hive"] = Hive.update_client_loc(from_client["appname"])
            
        # From Hive
        
            elif a == "registration_check" and interface == "service":
                if Hive.registration_check(from_client["account"]):
                    response["honeycomb"]["registration"] = True
                else:
                    response["honeycomb"]["registration"] = False
        
            elif a == "image_retrieval" and interface == "service":
                response = Database.image_retrieval(from_client["url"])        
        if a != "image_retrieval":
            return json.dumps(response)
        else:
            return response
