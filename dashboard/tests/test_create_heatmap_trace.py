import pandas as pd
import plotly.graph_objects as go
import pytest
from components.comp_heatmap import create_heatmap_trace


@pytest.fixture
def valid_chart_df():
    """Provides a standard valid dataframe for happy-path testing."""
    return pd.DataFrame(
        {
            "agg_trip_date": pd.to_datetime(["2023-01-01", "2023-01-02"]),
            "pick_up_borough": ["Manhattan", "EWR"],
            "drop_off_borough": ["Brooklyn", "Queens"],
            "total_trip_count": [1, 2],
            "total_passenger_count": [10.0, 2.0],
            "total_trip_distance_miles": [5.5, 12.0],
            "total_fare_amount": [25.0, 45.0],
            "total_amount_charged": [30.0, 50.0],
        }
    )


def test_create_heatmap_trace(valid_chart_df):
    # Call your isolated function directly
    boroughs = ["Manhattan", "Brooklyn", "Queens", "EWR"]
    trace = create_heatmap_trace(
        df_subset=valid_chart_df,
        borough_list=boroughs,
        metric_to_plot="total_trip_count",
        metric_fancy="Total Trip Count",
        show_legend=True,
    )

    assert isinstance(trace, go.Heatmap)
    assert trace.colorscale[1][1] == "#1E6B9B"
    assert trace.colorbar.title.text == "Total Trip Count (Log Scale)"

    trace = create_heatmap_trace(
        df_subset=valid_chart_df,
        borough_list=boroughs,
        metric_to_plot="total_passenger_count",
        metric_fancy="Total Passenger Count",
        show_legend=True,
    )

    assert isinstance(trace, go.Heatmap)
    assert trace.colorscale[1][1] == "#1E6B9B"
    assert trace.colorbar.title.text == "Total Passenger Count (Log Scale)"
