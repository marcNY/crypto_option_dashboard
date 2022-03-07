
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_graph1(option_data, currency_pair, is_delta_hedged):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Scatter(x=option_data['timestamp'],
                   y=option_data['pnl'], name="PnL"),
        secondary_y=True,
    )

    fig.add_trace(
        go.Scatter(x=option_data['timestamp'],
                   y=option_data['close_spot'], name=currency_pair),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=option_data['timestamp'],
                   y=option_data['strike'], name="STRIKE"),
        secondary_y=False,
    )

    # Add figure title
    fig.update_layout(
        title_text="PnL graph \U0001F4B0 of " +
        ("the delta hedged strategy" if is_delta_hedged else "the unhedged strategy") +
        (" over " + str((option_data['timestamp'].max()-option_data['timestamp'].min()).days)+ " days")
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date", showgrid=False)

    # Set y-axes titles
    fig.update_yaxes(title_text=currency_pair,
                     secondary_y=False, showgrid=True)
    fig.update_yaxes(title_text="$ PnL", secondary_y=True, showgrid=False)
    return fig


def create_delta_graph(option_data):
    # Create figure with secondary y-axis
    fig = go.Figure(
        [go.Scatter(x=option_data['timestamp'], y=option_data['delta_mid'])])

    # Add figure title
    fig.update_layout(
        title_text="Delta graph"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="Delta")

    return fig


def create_graph2(option_data, currency_pair):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=option_data['timestamp'],
                   y=option_data['ivol_mid'], name="Volatility"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Bar(x=option_data['timestamp'],
               y=option_data['volume_option'], name="VOLUME"),
        secondary_y=True,
    )
    #fig.update_layout(yaxis_tickformat = '%',secondary_y=False)

    # Add figure title
    fig.update_layout(
        title_text="Volume and Volatility of " + currency_pair + " options"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date", showgrid=False)

    # Set y-axes titles
    fig.update_yaxes(title_text="Percentage", tickformat=',.0%',
                     secondary_y=False, showgrid=True)
    fig.update_yaxes(title_text="Contracts", secondary_y=True, showgrid=False)
    return fig
