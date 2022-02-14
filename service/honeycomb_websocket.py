#!/usr/bin/env python3

import asyncio
import websockets
import json
import time
import subprocess
import sys
import os
import honeycomb_core as Core
import logging

async def to_core(websocket, path):
   
    async for message in websocket:
        themessage = message.decode()
        #print(themessage)
        #await websocket.send(themessage.encode("utf8"))
        if themessage.find("msg=") !=-1:
            appId = themessage.split("msg=")[1].split("<::>")[0]
            message = themessage.split("msg=")[1].split("<::>")[1]
            if len(themessage.split("msg=")[1].split("<::>")) == 3:
                key = Account.get_priv_from_pub(appId,"App")
                decrypted = Seed.simp_decrypt(key,message)
                response = Core.message(decrypted)
                encrypt = Seed.simp_crypt(key,response)
                #print(Seed.simp_decrypt(key,encrypt))
                await websocket.send(encrypt)
            else:
                logging.info('{"server":"error incomplete message"}')
                loggin.info(themessage)
                await websocket.send(str('{"server":"error incomplete message"}').encode("utf8"))
        else:
            if themessage != None:
                    jsoned = json.loads(themessage)
                    if jsoned["act"][0] != "image_retrieval":
                        msg = Core.message("service",themessage).encode("utf8")
                        await websocket.send(msg)
                    else:
                        await websocket.send(Core.message("service",themessage))

asyncio.get_event_loop().run_until_complete(websockets.serve(to_core, '0.0.0.0', 9501,max_size=1048576))
asyncio.get_event_loop().run_forever()
