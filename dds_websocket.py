#!/usr/bin/env python
import json
import time
import hmac
import asyncio
import hmac
import random
import requests
import json
#import ssl
import websockets
from hashlib import sha1
from uuid import uuid4
from hashlib import sha1
alias = "prod"
audioFile = "8k.wav"

# 使用自己产品的相关参数替换下列参数
#productId      = "278583390"
#apikey         = "69e213e728244fbdaa4de7eb6332122c"
registerServer = "https://auth.dui.ai"
productSecret  = "47b31295e4f6eb44828f8c8b3759cb73"
productKey     = "1044fd38345a86edcd55bf68b8c306d7"
format         = "plain"
productId      = "278579737"
deviceName     = "aispeech_test_5"
header         = "Content-Type: application/json\n"
headers        = "{\'content-type\': \"application/json\"}"
body           = "{\"deviceName\": \"aispeech_test_5\",\"platform\": \"linux\"}"

def hash_hmac(key, code, sha1):
    hmac_code = hmac.new(key.encode(), code.encode(), sha1)
    return hmac_code.hexdigest()

def deviceSecret_get():	
    nonce = random.randint(100000000,999999999)
    print(nonce)
    timestamp = str(time.time())		
    sigstr = f"{productKey}{format}{nonce}{productId}{timestamp}"
    print(sigstr)
    sig = hash_hmac(productSecret, sigstr, sha1)
    print(sig)
    httpurl = f"{registerServer}/auth/device/register?productKey={productKey}&format={format}&productId={productId}&timestamp={timestamp}&nonce={nonce}&sig={sig}"
    print(httpurl)
    response  = requests.post(httpurl, body, headers)
     
    # 返回信息
    print(response.text)
    # 返回响应头
    print(response.status_code)
    
    
    data = json.loads(response.text)
    print ("data['deviceSecret']: ", data['deviceSecret'])
    print ("data['productId']: ", data['productId'])

    return data['deviceSecret']
    
async def textRequest(ws):
    content = {
        "aiType":"dm",
        "topic": 'nlu.input.text',
        "recordId": uuid4().hex,
        "refText": "我想听歌",
		"asrParams.enableNBest":"true",
		"asrParams.nbest":"2"
    }
    try:
        await ws.send(json.dumps(content))
        resp = await ws.recv()
        print(resp)
    except websockets.exceptions.ConnectionClosed as exp:
        print(exp)


async def triggerIntent(ws):
    content = {
        "aiType":"dm",
        'topic': 'dm.input.intent',
        'recordId': uuid4().hex,
        'skillId': '2018040200000004',
        'intent': '查询天气',
        'task': "天气",
        'slots': {
            '国内城市': "苏州"
        }
    }
    try:
        await ws.send(json.dumps(content))
        resp = await ws.recv()
        print(resp)
    except websockets.exceptions.ConnectionClosed as exp:
        print(exp)


async def audioRequest(ws):
    content = {
        "aiType":"dm",
        "topic": "recorder.stream.start",
        "recordId": uuid4().hex,
        "audio": {
            "audioType": "wav",
            "sampleRate": 8000,
            "channel": 1,
            "sampleBytes": 2
        }
    }
    try:
        await ws.send(json.dumps(content))
        with open(audioFile, 'rb') as f:
            while True:
                chunk = f.read(3200)
                if not chunk:
                    await ws.send(bytes("", encoding="utf-8"))
                    break
                await ws.send(chunk)
        async for message in ws:
            print(message)
            resp = json.loads(message)
            if 'dm' in resp:
                break
    except websockets.exceptions.ConnectionClosed as exp:
        print(exp)
        ws.close()


async def dds_demo():
    # 云端对云端。
    #url = f"wss://dds.dui.ai/dds/v2/{alias}?serviceType=websocket&productId={productId}&apikey={apikey}"
    deviceSecret = deviceSecret_get()
    nonce = random.randint(100000000,999999999)
    print(nonce)
    wsstr = f"{deviceName}{nonce}{productId}"
    print(wsstr)
    wssig = hash_hmac(deviceSecret, wsstr, sha1)
    print(wssig)
    
    wsurl = f"wss://dds.dui.ai/dds/v2/test?serviceType=websocket&productId={productId}&deviceName={deviceName}&nonce={nonce}&sig={wssig}"
    print(wsurl)
    
    #print(url) 
    async with websockets.connect(wsurl) as websocket:
        #await textRequest(websocket)
        # await triggerIntent(websocket)
         await audioRequest(websocket)


asyncio.get_event_loop().run_until_complete(dds_demo())