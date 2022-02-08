from logging import raiseExceptions
import streamlit as st
import api
import pandas as pd
import asyncio
import datetime as dt
import altair as alt

#pricing libraries
import py_vollib_vectorized
from py_vollib.black_scholes.implied_volatility import implied_volatility
from py_vollib.black_scholes.greeks.analytical import delta


import plotly.graph_objects as go




@st.cache
def get_instrument_list(crypto_analyzed, option_type_selected):
    instrument_list = api.get_instruments(crypto_analyzed, kind="option")
    filt_inst_list = instrument_list.loc[instrument_list.option_type ==
                                         option_type_selected].sort_values(by=["expiration_time", "strike"])
    # filt_inst_list.strike=filt_inst_list.strike.apply(round)
    # filt_inst_list.expiration_time=filt_inst_list.expiration_time.dt.date

    return filt_inst_list



def get_historical_data(instrument_dict, time_period="1D"):
    ts_creation = instrument_dict["creation_timestamp"]
    ts_expiration = instrument_dict["expiration_timestamp"]

    option_data = api.get_historical_data(ts_creation,
                                      ts_expiration,
                                      instrument_dict["instrument_name"],
                                      time_period)
                                    

    if instrument_dict["quote_currency"] == "BTC":
        spot_name = "BTC-PERPETUAL"
    elif instrument_dict["quote_currency"] == "ETH":
        spot_name = "ETH-PERPETUAL"
    else:
        raise(NotImplementedError("The currency has not been implemented yet"))

    spot_data = api.get_historical_data(ts_creation,
                                    ts_expiration,
                                    spot_name,
                                    time_period)
    data = pd.merge(option_data,spot_data,how="left",on="ticks",suffixes=("_option","_spot"))
    unwanted = data.columns[data.columns.str.startswith('Unnamed')]
    data.drop(unwanted, axis=1, inplace=True)
    data.drop(["timestamp_option","timestamp_spot"],axis=1, inplace=True)
    data['timestamp'] = data.ticks.apply(lambda x:dt.datetime.fromtimestamp(x/1000))
    expiry=dt.datetime.fromtimestamp(ts_expiration/1000)
    data["time_to_expiry"] = data.timestamp.apply(lambda x:expiry-x)
    data["days_to_expiry"] = data["time_to_expiry"].apply(lambda x: x.days)
    data['strike']=instrument_dict["strike"] 
    return data

def compute_pnl(instrument_dict, data):
    strike = instrument_dict['strike']

    if instrument_dict['option_type'] == 'call':
        option_type = 'c'
    else:
        option_type = 'p'

    r = 0.01 # This is the risk-free interest rate. For short-dated options it doesn't matter much
    qty = 1277
    mult = 1
    is_delta_hedged = True
    data['ivol_mid'] = implied_volatility(price=data['close_option'] * data['close_spot'],
                                      S=data['close_spot'],
                                      K=strike,
                                      t=data['days_to_expiry']/365,
                                      r=r,
                                      flag=option_type, 
                                      return_as="series")
    data['delta_mid'] = py_vollib_vectorized.greeks.delta(option_type, data['close_spot'], 
            strike,data['days_to_expiry']/365, r, data[ 'ivol_mid'])
    data['daily_pnl_option'] = data['close_option'].diff() * qty * mult
    data["daily_pnl_spot"] = data['close_spot'].diff() * data['delta_mid'].shift() * qty * mult
    ts = data['daily_pnl_option'] - data["daily_pnl_spot"] * is_delta_hedged
    data['pnl'] = ts.cumsum()
    return data

@st.cache
def get_data_compute_pnl(instrument_dict, time_period):
    data=get_historical_data(instrument_dict, time_period="1D")
    data=compute_pnl(instrument_dict, data)
    return data


st.title("Option Dashboard")

st.subheader("Instrument list")

crypto_analyzed = st.selectbox("Bitcoin or Ethereum", ["BTC", "ETH"])
option_type_selected = st.selectbox("Call or Put", ["call", "put"])

instrument_list = get_instrument_list(crypto_analyzed, option_type_selected)
instrument_selected = st.selectbox("Which instrument to analyze?", instrument_list.instrument_name.to_list())
instrument_dict = instrument_list.loc[instrument_list.instrument_name ==
                                      instrument_selected].to_dict('records')[0]

st.subheader("data list") 
option_data=get_data_compute_pnl(instrument_dict, "1D")                         
#option_data.info()
#Data columns (total 23 columns):
# #   Column            Non-Null Count  Dtype          
# ---  ------            --------------  -----          
#  0   volume_option     63 non-null     float64        
#  1   ticks             63 non-null     int64          
#  2   status_option     63 non-null     object         
#  3   open_option       63 non-null     float64        
#  4   low_option        63 non-null     float64        
#  5   high_option       63 non-null     float64        
#  6   cost_option       63 non-null     float64        
#  7   close_option      63 non-null     float64        
#  8   volume_spot       63 non-null     float64        
#  9   status_spot       63 non-null     object         
#  10  open_spot         63 non-null     float64        
#  11  low_spot          63 non-null     float64        
#  12  high_spot         63 non-null     float64        
#  13  cost_spot         63 non-null     float64        
#  14  close_spot        63 non-null     float64        
#  15  timestamp         63 non-null     datetime64[ns] 
#  16  time_to_expiry    63 non-null     timedelta64[ns]
#  17  days_to_expiry    63 non-null     int64          
#  18  ivol_mid          63 non-null     float64        
#  19  delta_mid         63 non-null     float64        
#  20  daily_pnl_option  62 non-null     float64        
#  21  daily_pnl_spot    62 non-null     float64        
#  22  pnl               62 non-null     float64   
print(option_data.head())



import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_graph1(option_data):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=option_data['timestamp'], y=option_data['pnl'], name="PNL"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=option_data['timestamp'], y=option_data['close_spot'], name="BTC PRICE"),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(x=option_data['timestamp'], y=option_data['strike'], name="STRIKE"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
        title_text="PNL graph"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="USD", secondary_y=False)
    fig.update_yaxes(title_text="USD", secondary_y=True)
    return fig
fig=create_graph1(option_data)
st.plotly_chart(fig, use_container_width=True)