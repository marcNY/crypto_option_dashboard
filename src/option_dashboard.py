from logging import raiseExceptions
from operator import index
from traceback import format_exc
import streamlit as st
import api
import pandas as pd
import numpy as np

# using these library
import graphs
import pricing

import time
import datetime



st.set_page_config(layout="wide")


# Output
# Data columns (total 22 columns):
#  #   Column                  Non-Null Count  Dtype
# ---  ------                  --------------  -----
#  0   tick_size               246 non-null    float64
#  1   taker_commission        246 non-null    float64
#  2   strike                  246 non-null    float64
#  3   settlement_period       246 non-null    object
#  4   settlement_currency     246 non-null    object
#  5   rfq                     246 non-null    bool
#  6   quote_currency          246 non-null    object
#  7   option_type             246 non-null    object
#  8   min_trade_amount        246 non-null    float64
#  9   maker_commission        246 non-null    float64
#  10  kind                    246 non-null    object
#  11  is_active               246 non-null    bool
#  12  instrument_name         246 non-null    object
#  13  expiration_timestamp    246 non-null    int64
#  14  creation_timestamp      246 non-null    int64
#  15  counter_currency        246 non-null    object
#  16  contract_size           246 non-null    float64
#  17  block_trade_commission  246 non-null    float64
#  18  base_currency           246 non-null    object
#  19  creation_time           246 non-null    datetime64[ns]
#  20  expiration_time         246 non-null    datetime64[ns]
#  21  expiration_date_string  246 non-null    object
@st.cache
def get_instrument_list(crypto_analyzed, option_type_selected):
    instrument_list = api.get_instruments(crypto_analyzed, kind="option")
    instrument_list["strike"] = instrument_list['strike'].astype('int')
    filt_inst_list = instrument_list.loc[instrument_list.option_type ==
                                         option_type_selected].sort_values(by=["expiration_time", "strike"])
    # filt_inst_list.strike=filt_inst_list.strike.apply(round)
    # filt_inst_list.expiration_time=filt_inst_list.expiration_time.dt.date
    return filt_inst_list


@st.cache
def get_data_compute_pnl(instrument_dict, time_period, qty=1, mul=1, delta_hedged=True,day_past=None):
    data = pricing.get_historical_data(instrument_dict, time_period,day_past)
    data = pricing.compute_pnl(instrument_dict, data, qty, mul, delta_hedged)
    return data



@st.cache
def get_option_data(instrument_dict, time_period):
    data = pricing.get_historical_data(instrument_dict, time_period)
    return data


# Data columns (total 20 columns):
#  #   Column            Non-Null Count  Dtype          
# ---  ------            --------------  -----          
#  0   volume_option     38 non-null     float64        
#  1   ticks             38 non-null     int64          
#  2   status_option     38 non-null     object         
#  3   open_option       38 non-null     float64        
#  4   low_option        38 non-null     float64        
#  5   high_option       38 non-null     float64        
#  6   cost_option       38 non-null     float64        
#  7   close_option      38 non-null     float64        
#  8   volume_spot       38 non-null     float64        
#  9   status_spot       38 non-null     object         
#  10  open_spot         38 non-null     float64        
#  11  low_spot          38 non-null     float64        
#  12  high_spot         38 non-null     float64        
#  13  cost_spot         38 non-null     float64        
#  14  close_spot        38 non-null     float64        
#  15  timestamp         38 non-null     datetime64[ns] 
#  16  close_option_usd  38 non-null     float64        
#  17  time_to_expiry    38 non-null     timedelta64[ns]
#  18  days_to_expiry    38 non-null     int64          
#  19  strike            38 non-null     int64  
def filter_and_compute_pnl(instrument_dict, historical_data, qty=1, mul=1, delta_hedged=True, day_past=None):
    if day_past:
        ts_start = int((datetime.datetime.now() +
                       datetime.timedelta(days=-day_past)).timestamp() * 1000)
        historical_data = historical_data.loc[historical_data.ticks > ts_start]
    data = pricing.compute_pnl(
        instrument_dict, historical_data, qty, mul, delta_hedged)
    return data


col1, col2 = st.columns([3, 1])


col2.title("Option Dashboard")


crypto_analyzed = col2.selectbox("Bitcoin or Ethereum", ["BTC", "ETH"])
option_type_selected = col2.selectbox("Call or Put", ["call", "put"])

instrument_list = get_instrument_list(crypto_analyzed, option_type_selected)

## Expiration Time selected
def get_first_day_next_month(dt):
    return (dt.replace(day=1) + datetime.timedelta(days=32)).replace(day=1)


def last_timestamp_this_month(instrument_list):
    first_day_next_month = get_first_day_next_month(datetime.datetime.now())
    max_this_month = instrument_list.expiration_time.loc[instrument_list.expiration_time < first_day_next_month].max(
    )
    return max_this_month


expiration_timestamps_arr = instrument_list.expiration_time.unique()
index_max_this_month = int(np.where(
    expiration_timestamps_arr == last_timestamp_this_month(instrument_list))[0][0])

expiration_timestamp_selected = col2.selectbox("Expiration date",
                                               instrument_list.expiration_timestamp.unique(),
                                               index=index_max_this_month,
                                               format_func=lambda x: datetime.datetime.fromtimestamp(x/1000).strftime("%d %b %Y"))

## Strike selected
def get_closest_strike_index(instrument_list, crypto_analyzed, expiration_timestamp_selected):
    crypto_price = api.get_index_price(crypto_analyzed)
    strikes = instrument_list.loc[instrument_list.expiration_timestamp ==
                                  expiration_timestamp_selected].strike.unique()
    desired_strike = min(strikes, key=lambda x: abs(x-crypto_price))
    strike_index = int(np.where(
        strikes == desired_strike)[0][0])
    return (strikes, strike_index)


(strike_list, strike_index) = get_closest_strike_index(
    instrument_list, crypto_analyzed, expiration_timestamp_selected)
strike_selected = col2.selectbox(
    "Strike of the option", strike_list, index=strike_index)
## initial investment?
initial_quantity_usd = col2.number_input("Initial Investment in USD", min_value=1, value=10000, step=1)
initial_quantity = initial_quantity_usd/api.get_index_price(crypto_analyzed)
## instrument selected
instrument_selected = instrument_list.loc[(instrument_list.expiration_timestamp==expiration_timestamp_selected) & (instrument_list.strike==strike_selected)].instrument_name.iloc[0]




## different opton necessary
previous_day_selected = col2.selectbox("How many days in the past?",[None,30,60,90],index=2,format_func=lambda x: str(x) + " days" if x else "all")
is_delta_hedged = col2.checkbox('Delta Hedge',value=True)
show_delta_graph = col2.checkbox('Show Delta Graph',value=False)
col2.write("instrument selected:  "+instrument_selected)


instrument_dict = instrument_list.loc[instrument_list.instrument_name ==
                                      instrument_selected].to_dict('records')[0]
## pricing
#if_runner = col1.image('images/loading.gif')
option_data = get_data_compute_pnl(instrument_dict, "1D", qty=initial_quantity, mul=1, delta_hedged=is_delta_hedged,day_past=previous_day_selected)


fig = graphs.create_graph1(option_data, instrument_dict["quote_currency"]+instrument_dict["counter_currency"],is_delta_hedged)
col1.plotly_chart(fig, use_container_width=True)
if show_delta_graph:
    fig = graphs.create_delta_graph(option_data)
    col1.plotly_chart(fig, use_container_width=True)
fig2 = graphs.create_graph2(option_data, instrument_dict["quote_currency"]+instrument_dict["counter_currency"])
col1.plotly_chart(fig2, use_container_width=True)


#gif_runner.empty()