

import datetime as dt
import pandas as pd
#pricing libraries
import py_vollib_vectorized
from py_vollib.black_scholes.implied_volatility import implied_volatility
from py_vollib.black_scholes.greeks.analytical import delta

import api

## Output
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

def compute_pnl(instrument_dict, data, qty=1, mult=1, is_delta_hedged = True):
    strike = instrument_dict['strike']

    if instrument_dict['option_type'] == 'call':
        option_type = 'c'
    else:
        option_type = 'p'

    r = 0.01 # This is the risk-free interest rate. For short-dated options it doesn't matter much

    
    data['ivol_mid'] = implied_volatility(price=data['close_option'],
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
