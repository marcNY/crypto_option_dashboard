from logging import raiseExceptions
import streamlit as st
import api
import pandas as pd


#using these library
import graphs
import pricing


@st.cache
def get_instrument_list(crypto_analyzed, option_type_selected):
    instrument_list = api.get_instruments(crypto_analyzed, kind="option")
    filt_inst_list = instrument_list.loc[instrument_list.option_type ==
                                         option_type_selected].sort_values(by=["expiration_time", "strike"])
    # filt_inst_list.strike=filt_inst_list.strike.apply(round)
    # filt_inst_list.expiration_time=filt_inst_list.expiration_time.dt.date

    return filt_inst_list



@st.cache
def get_data_compute_pnl(instrument_dict, time_period):
    data=pricing.get_historical_data(instrument_dict, time_period="1D")
    data=pricing.compute_pnl(instrument_dict, data)
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

print(option_data.head())

fig=graphs.create_graph1(option_data)
st.plotly_chart(fig, use_container_width=True)

fig2=graphs.create_graph2(option_data)
st.plotly_chart(fig2, use_container_width=True)