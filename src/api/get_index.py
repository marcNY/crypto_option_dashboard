import asyncio
from operator import index
import websockets
import json


async def call_api(msg):
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        await websocket.send(msg)
        while websocket.open:
            response = await websocket.recv()
            return response


def async_loop(api, message):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return asyncio.get_event_loop().run_until_complete(api(message))


def retrieve_index_price(index_name):
    msg = \
        {"jsonrpc": "2.0",
         "method": "public/get_index",
         "id": 42,
         "params": {
             "currency": index_name}
         }

    # print(msg)
    resp = async_loop(call_api, json.dumps(msg))
    return resp


def json_to_float(resp,index_name):
    resp_dict=json.loads(resp)
    return resp_dict["result"][index_name]


def get_index_price(index_name):
    resp = retrieve_index_price(index_name)
    df = json_to_float(resp,index_name)
    return df


if __name__ == "__main__":
    index_name = "BTC"

    json_resp = get_index_price(index_name)
    print(json_resp)
