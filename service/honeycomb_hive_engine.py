#!/usr/bin/python3
import sys
import os
import json
import requests
sys.path.append("..")

def get_from_hive_engine(data_type,accountname,opts = []):
    response = {}
    for data in data_type:
        if data == "tokens":
            response.update({"tokens":get_hive_tokens_info()})
        if data == "balance":
            response.update({"balance":get_balance(accountname)})
        
    return response


def find_on_hive_engine(query, symbol, m):                                                          
    url = 'https://api.hive-engine.com/rpc/contracts'
    params = {'contract':'nft', 'table':f'{symbol}instances', 'query':query, 'limit':1000, 'offset':0, 'indexes':[]}
    j = {'jsonrpc':'2.0', 'id':1, 'method':m, 'params':params}

    with requests.post(url, json=j) as r:
       # print("From find on hive engine ",r.text)
        data = r.json()
    return data['result']

### NFTSR sample.
    
def get_nftshowroom_art(accountname,col_type):
    url = 'https://nftshowroom.com/api/arts/info?series='
    art = find_on_hive_engine({'account':accountname},'NFTSR','find')
    returns = []
    for a in art:
        with requests.get(url+a["properties"]["artSeries"]) as r:
            data = r.json()
            for col in col_type:
                print(col)
                print(data)
                if "gallery" == col:
                    if data["creator"] == accountname:
                        returns.append(data)
                if "collection" == col:
                    if data["creator"] != accountname:
                        returns.append(data)
    return returns
    
def get_hive_tokens_info():
    url = "https://api.hive-engine.com/rpc/contracts"
    params = {"jsonrpc":"2.0","id":14,"method":"find","params":{"contract":"tokens","table":"tokens","query":{},"limit":1000,"offset":0,"indexes":""}}
    
    with requests.post(url, json=params) as t:
       data = t.json()
    return data["result"]
    
def get_balance(accountname):
    url = "https://api.hive-engine.com/rpc/contracts"
    params = {"jsonrpc":"2.0","id":14,"method":"find","params":{"contract":"tokens","table":"balances","query":{"account":accountname},"limit":1000,"offset":0,"indexes":""}}
    
    with requests.post(url, json=params) as t:
       data = t.json()
    return data["result"]

