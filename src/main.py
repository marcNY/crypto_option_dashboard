from api.get_instruments import get_instruments
from api.get_historical_data import get_historical_data
import pandas as pd

# Starting currency BTC ETH

# Get all the active options on BTC
# kind can take the argument option or future
instruments = None
DEBUG = False
if not DEBUG:
    instruments = get_instruments("BTC", kind="option", expired=False)
    print("\n instruments fields available\n")


if DEBUG and instruments != None:
    instruments.to_csv("././files/BTC_OPTION.csv")

if DEBUG:
    instruments = pd.read_csv("././files/BTC_OPTION.csv")


print(instruments.info())
print(instruments.head())
# get all settlements time
print("\n All the option expiration date available\n")
print(instruments.expiration_time.unique())


# get all options type for a settlement time: '2021-10-29 10:00:00'
date_of_interest = "2021-10-29 10:00:00"
print("\n Option Type available for the expiration date of {date_of_interest}\n")
print(
    instruments.loc[
        instruments.expiration_time == date_of_interest
    ].option_type.unique()
)


# get the strike of all calls for a settlement time: '2021-10-29 10:00:00'
option_type_of_interest = "call"
print(
    "\n All the strikes available for a {option_type_of_interest} expiring on {date_of_interest}\n"
)
print(
    instruments.loc[
        (instruments.expiration_time == date_of_interest)
        & (instruments.option_type == option_type_of_interest)
    ].strike.unique()
)

# using the three selector we are able to get the instrument name
strike_of_interest = 60000

print(
    "\n Instrument name creation and expiration for a {option_type_of_interest} expiring on {date_of_interest}\n"
)

instrument_data = instruments.loc[
    (instruments.expiration_time == date_of_interest)
    & (instruments.option_type == option_type_of_interest)
    & (instruments.strike == strike_of_interest)
]
instrument_dict = instrument_data.to_dict("records")[0]
print(instrument_dict["instrument_name"])
print(instrument_dict["creation_time"])
print(instrument_dict["expiration_time"])


time_period = "1D"

option_data = get_historical_data(
    instrument_dict["creation_timestamp"],
    instrument_dict["expiration_timestamp"],
    instrument_dict["instrument_name"],
    time_period,
)
print("\option data:\n")
print(option_data.head())

# if we are using BTC the underlying will be BTC-PERPETUAL if we are using ETH the underlying will be ETH-PERPETUAL

spot_data = get_historical_data(
    instrument_dict["creation_timestamp"],
    instrument_dict["expiration_timestamp"],
    "BTC-PERPETUAL",
    time_period,
)
print("\spot data:\n")
print(spot_data.head())


# For the rest of the logic please refer to notebooks/bactesting.ipynb
