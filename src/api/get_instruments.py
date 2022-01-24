import asyncio
import websockets
import json
import pandas as pd
import datetime as dt
import certifi, ssl

# msg = \
# {
#   "jsonrpc" : "2.0",
#   "id" : 7617,
#   "method" : "public/get_instruments",
#   "params" : {
#     "currency" : "BTC",
#     "kind" : "future",
#     "expired" : False
#   }
# }


async def call_api(msg):
    ssl_context = ssl.create_default_context()
    ssl_context.load_verify_locations(certifi.where())
    async with websockets.connect(
        "wss://test.deribit.com/ws/api/v2", ssl=ssl_context
    ) as websocket:
        await websocket.send(msg)
        while websocket.open:
            response = await websocket.recv()
            # do something with the response...
            return response


def async_loop(api, message):
    return asyncio.get_event_loop().run_until_complete(api(message))


def retrieve_instruments(currency, kind=None, expired=False):
    if kind:
        params = {"currency": currency, "kind": kind, "expired": False}
    else:
        params = {"currency": currency, "expired": False}
    msg = {
        "jsonrpc": "2.0",
        "id": 7617,
        "method": "public/get_instruments",
        "params": params,
    }
    resp = async_loop(call_api, json.dumps(msg))
    return resp


def json_to_dataframe(json_resp):
    res = json.loads(json_resp)
    df = pd.DataFrame(res["result"])
    df["creation_time"] = df["creation_timestamp"].apply(
        lambda x: dt.datetime.fromtimestamp(x / 1000)
    )
    df["expiration_time"] = df["expiration_timestamp"].apply(
        lambda x: dt.datetime.fromtimestamp(x / 1000)
    )
    return df


def get_instruments(currency, kind=None, expired=False):
    resp = retrieve_instruments(currency, kind, expired)
    df = json_to_dataframe(resp)
    return df

if __name__ == "__main__":
    json_resp = retrieve_instruments("BTC")
    df = json_to_dataframe(json_resp)
    print(
        df[
            [
                "instrument_name",
                "is_active",
                "creation_time",
                "expiration_time",
                "creation_timestamp",
                "expiration_timestamp",
            ]
        ].head(100)
    )
