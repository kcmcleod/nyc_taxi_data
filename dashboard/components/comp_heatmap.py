from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from data_access import get_table_data, list_all_boroughs
from plotly.subplots import make_subplots


def render(start_date: date, end_date: date):
    """
    Tab that displays heatmaps showing the "frequency" of travel between boroughs.
    Allows user to select the metric displayed and the granulairity of the heatmaps.

    Args:
        start_date(date): Start of user selected date range
        end_date(date): End of user selected date range
    """

    borough_list = list_all_boroughs()

    with st.popover("⚙️ Configure Heatmap"):
        agg_level = st.selectbox("Granularity", options=["Total", "Monthly", "Weekly"])

        metric_to_plot = st.selectbox(
            "Metric to Plot",
            options=["total_trip_count", "total_passenger_count", "total_fare_amount"],
            format_func=lambda x: x.replace("_", " ").title(),
        )

    try:
        # If 'Total', query Monthly and roll it all up locally.
        db_agg = "Monthly" if agg_level == "Total" else agg_level

        df = get_table_data(start_date, end_date, borough_list, borough_list, db_agg)
    except Exception:  # noqa: BLE001
        st.error("Failed to load data mart. Please verify dbt build status.")
        return

    if df.empty:
        st.info("No trips found for this date range.")
        return

    all_col_names = list(df.columns.values)
    required_cols = [
        "agg_trip_date",
        "pick_up_borough",
        "drop_off_borough",
        metric_to_plot,
    ]

    if not set(required_cols).issubset(all_col_names):
        st.error("Failed to load required data.")
        return

    df.fillna(
        {"pick_up_borough": "Unknown", "drop_off_borough": "Unknown"}, inplace=True
    )

    # Aggregate based on chosen granularity
    if agg_level == "Total":
        group_cols = ["pick_up_borough", "drop_off_borough"]
    else:
        df["period"] = df["agg_trip_date"].astype(str)
        group_cols = ["period", "pick_up_borough", "drop_off_borough"]

    heatmap_data = df.groupby(group_cols, as_index=False)[metric_to_plot].sum()

    # Render Chart(s)
    metric_fancy = metric_to_plot.replace("_", " ").title()

    if agg_level == "Total":
        fig = go.Figure(
            data=create_heatmap_trace(
                heatmap_data,
                borough_list,
                metric_to_plot,
                metric_fancy,
                show_legend=True,
            )
        )
        fig.update_layout(
            title=f"Location Heatmap: {metric_fancy} (Combined)",
            xaxis_title="Pick-up Borough",
            yaxis_title="Drop-off Borough",
            xaxis_tickangle=90,
            height=500,
        )
    else:
        periods = sorted(heatmap_data["period"].unique())
        n_facets = len(periods)
        n_cols = min(n_facets, 3)
        n_rows = int(np.ceil(n_facets / 3))

        fig = make_subplots(
            rows=n_rows,
            cols=n_cols,
            subplot_titles=periods,
            shared_yaxes=True,  # Hides duplicate y-axis labels on columns 2 and 3
            vertical_spacing=0.25,
            horizontal_spacing=0.05,
        )

        for i, period in enumerate(periods):
            subset = heatmap_data[heatmap_data["period"] == period]
            trace = create_heatmap_trace(
                subset, borough_list, metric_to_plot, metric_fancy, show_legend=(i == 0)
            )
            fig.add_trace(trace, row=(i // 3) + 1, col=(i % 3) + 1)

        fig.update_layout(
            title=f"Location Heatmap: {metric_fancy} by {agg_level}",
            height=max(500, n_rows * 400),
        )
        fig.update_xaxes(tickangle=90)

    st.plotly_chart(fig, use_container_width=True)


def create_heatmap_trace(
    df_subset: pd.DataFrame,
    borough_list: list[str],
    metric_to_plot: str,
    metric_fancy: str,
    show_legend=False,
) -> go.Heatmap:
    """
    Returns a single heatmap from given data.

    Args:
        df_subset(np.DataFrame): Data for heatmap. Should have 3 cols: pick_up_borough, drop_off_borough and 'metric_to_plot'
        borough_list(list[str]): Names of all boroughs
        metric_to_plot(str): The actual name of column to be used as values in chart. A log will be created from this col.
        metric_fancy(str): The printable version of `metric_to_plot`
        show_legend: Show/hide depending on position of chart in the group.

    Returns:
        A single heatmap that can be displayed.
    """

    matrix_df = df_subset.pivot(
        index="drop_off_borough", columns="pick_up_borough", values=metric_to_plot
    ).fillna(0)

    # Lock factor levels globally so axes align perfectly across all subplots
    matrix_df = matrix_df.reindex(
        index=borough_list, columns=borough_list, fill_value=0
    )

    z_raw = matrix_df.values
    z_log = np.log10(z_raw + 1)

    return go.Heatmap(
        z=z_log,
        x=matrix_df.columns,
        y=matrix_df.index,
        customdata=z_raw,
        hovertemplate="<b>Pick-up:</b> %{x}<br><b>Drop-off:</b> %{y}<br><b>Volume:</b> %{customdata:,.0f}<extra></extra>",
        colorscale=["#FFFFFF", "#1E6B9B", "#79833D", "#DAA520"],
        showscale=show_legend,
        colorbar={
            "title": f"{metric_fancy} (Log Scale)",
            "tickvals": [0, 1, 2, 3, 4, 5, 6],
            "ticktext": ["0", "10", "100", "1k", "10k", "100k", "1M"],
            "lenmode": "pixels",
            "len": 300,
            "yanchor": "top",
            "y": 1,
        }
        if show_legend
        else None,
    )


if __name__ == "__main__":  # pragma: no cover
    render(date(2023, 1, 1), date(2023, 1, 31))
