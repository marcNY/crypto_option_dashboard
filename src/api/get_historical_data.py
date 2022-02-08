import asyncio
import websockets
import json
import pandas as pd
import datetime as dt
import certifi, ssl

msg = {
    "jsonrpc": "2.0",
    "id": 833,
    "method": "public/get_tradingview_chart_data",
    "params": {
        "instrument_name": "BTC-5APR19",
        "start_timestamp": 1554373800000,
        "end_timestamp": 1554376800000,
        "resolution": "30",
    },
}


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
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return asyncio.get_event_loop().run_until_complete(api(message))


def retrieve_historic_data(start, end, instrument, timeframe):
    msg = {
        "jsonrpc": "2.0",
        "id": 833,
        "method": "public/get_tradingview_chart_data",
        "params": {
            "instrument_name": instrument,
            "start_timestamp": start,
            "end_timestamp": end,
            "resolution": timeframe,
        },
    }
    #print(msg)
    resp = async_loop(call_api, json.dumps(msg))
    return resp


def json_to_dataframe(json_resp):
    res = json.loads(json_resp)
    #print(res)
    df = pd.DataFrame(res["result"])
    df["timestamp"] = [dt.datetime.fromtimestamp(date / 1000) for date in df.ticks]
    return df


def get_historical_data(start, end, instrument, timeframe):
    resp = retrieve_historic_data(start, end, instrument, timeframe)
    df = json_to_dataframe(resp)
    return df


if __name__ == "__main__":
    start = 1632384002000
    end = 1634284800000
    instrument = "BTC-PERPETUAL"
    timeframe = "1D"

    json_resp = retrieve_historic_data(start, end, instrument, timeframe)
    df = json_to_dataframe(json_resp)
    df.to_csv("././files/" + instrument + ".csv")
    print(df.head(20))
