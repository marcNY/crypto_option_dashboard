import asyncio
import websockets
import json

msg = \
{
  "jsonrpc" : "2.0",
  "id" : 9929,
  "method" : "public/auth",
  "params" : {
    "grant_type" : "client_credentials",
    "client_id" : "fo7WAPRm4P",
    "client_secret" : "W0H6FJW4IRPZ1MOQ8FP6KMC5RZDUUKXS"
  }
}

async def call_api(msg):
   async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
       await websocket.send(msg)
       while websocket.open:
           response = await websocket.recv()
           # do something with the response...
           return response

def async_loop(api,message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return asyncio.get_event_loop().run_until_complete(api(message))

def authenticate(credentials_file='./credentials.json'):
    with open(credentials_file) as json_file:
        data = json.load(json_file)
    client_id=data['client_id']
    client_secret=data['client_secret']

    msg = \
    {
    "jsonrpc" : "2.0",
    "id" : 9929,
    "method" : "public/auth",
    "params" : {
        "grant_type" : "client_credentials",
        "client_id" : client_id,
        "client_secret" : client_secret
    }
    }
    print(msg)
    resp=async_loop(call_api,json.dumps(msg))
    return resp

if __name__=="__main__":
    authenticate()