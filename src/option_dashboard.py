from logging import raiseExceptions
import streamlit as st
import api
import pandas as pd
import numpy as np

#using these library
import graphs
import pricing

import time
import datetime

@st.cache
## Output
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
def get_instrument_list(crypto_analyzed, option_type_selected):
    instrument_list = api.get_instruments(crypto_analyzed, kind="option")
    instrument_list["expiration_date_string"]=instrument_list.expiration_time.dt.strftime('%Y-%m-%d')
    filt_inst_list = instrument_list.loc[instrument_list.option_type ==
                                         option_type_selected].sort_values(by=["expiration_time", "strike"])
    # filt_inst_list.strike=filt_inst_list.strike.apply(round)
    # filt_inst_list.expiration_time=filt_inst_list.expiration_time.dt.date
    print(instrument_list.info())
    return filt_inst_list

@st.cache
def get_data_compute_pnl(instrument_dict, time_period,qty=1,mul=1,delta_hedged=True):
    data = pricing.get_historical_data(instrument_dict, time_period="1D")
    data = pricing.compute_pnl(instrument_dict, data,qty,mul,delta_hedged)
    return data


st.set_page_config(layout="wide")

col1, col2 = st.columns([3,1])



col2.title("Option Dashboard")


crypto_analyzed = col2.selectbox("Bitcoin or Ethereum", ["BTC", "ETH"])
option_type_selected = col2.selectbox("Call or Put", ["call", "put"])

instrument_list = get_instrument_list(crypto_analyzed, option_type_selected)

date_selected=col2.selectbox("Which expiration date?", instrument_list.expiration_date_string.unique())

strike_list=instrument_list.loc[instrument_list.expiration_date_string==date_selected].strike.unique().tolist()

strike_selected=col2.selectbox("Which Strike?",strike_list)

instrument_selected = instrument_list.loc[(instrument_list.expiration_date_string==date_selected) & (instrument_list.strike==strike_selected)].instrument_name.iloc[0]

col2.write("instrument selected:  "+instrument_selected)

is_delta_hedged=col2.checkbox('Delta Hedge',value=True)
show_delta_graph=col2.checkbox('Show Delta Graph',value=False)

instrument_dict = instrument_list.loc[instrument_list.instrument_name ==
                                      instrument_selected].to_dict('records')[0]


option_data = get_data_compute_pnl(instrument_dict, "1D", delta_hedged=is_delta_hedged)                         

print(option_data.head())

fig = graphs.create_graph1(option_data)
col1.plotly_chart(fig, use_container_width=True)
if show_delta_graph:
    fig = graphs.create_delta_graph(option_data)
    col1.plotly_chart(fig, use_container_width=True)
fig2 = graphs.create_graph2(option_data)
col1.plotly_chart(fig2, use_container_width=True)