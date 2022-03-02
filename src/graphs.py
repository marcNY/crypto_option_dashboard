
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_graph1(option_data):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Scatter(x=option_data['timestamp'],
                   y=option_data['pnl'], name="PNL"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=option_data['timestamp'],
                   y=option_data['close_spot'], name="BTC PRICE"),
        secondary_y=True,
    )
    fig.add_trace(
        go.Scatter(x=option_data['timestamp'],
                   y=option_data['strike'], name="STRIKE"),
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


def create_graph2(option_data):
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

    # Add figure title
    fig.update_layout(
        title_text="Vol and Volatility"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="Percentage", secondary_y=False)
    fig.update_yaxes(title_text="Contracts", secondary_y=True)
    return fig
