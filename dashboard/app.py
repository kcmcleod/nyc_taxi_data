import streamlit as st
from components import comp_availability, comp_line, comp_table  # tab_heatmap
from data_access import get_dataset_date_bounds

st.set_page_config(page_title="NYC Taxi Dashboard", layout="wide")
st.title("NYC Taxi Data dashboard")

with st.container(border=True):
    st.subheader("About this Dashboard")
    st.write(
        "This application provides high-speed, interactive analytics for New York City's Yellow Taxi network. Powered by an Apache Arrow and Parquet backend, it rapidly queries partitioned data to visualise journey volumes, financial metrics, and geographic trip patterns without the overhead of a traditional database."
    )
    st.markdown(
        "[Data from the NYC Taxi and Limousine Commission (TLC)](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page 'Data from the NYC Taxi and Limousine Commission (TLC).')"
    )

min_date, max_date = get_dataset_date_bounds()
with st.container(border=True):
    st.subheader("Date Range")
    date_selection = st.date_input(
        label="Controls the date range for all the charts/tables in this page",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

if len(date_selection) != 2:
    st.warning("Please select both a start and end date to load the dashboard.")
    st.stop()

start_date, end_date = date_selection


# Create the tab titles
tab_line, tab_heatmap, tab_table, tab_availability = st.tabs(
    ["Line Chart", "Heatmaps", "Table", "Histogram"]
)

with tab_line:
    st.write(f"Dates {start_date} - {end_date}")
    comp_line.render(start_date, end_date)

with tab_heatmap:
    st.header("Data Section")
    st.write("Here is where your data tables or charts go.")

with tab_table:
    st.write(
        "Summary metrics for the date range chosen above. Select your aggregation level and boroughs of interest."
    )
    comp_table.render(start_date, end_date)

with tab_availability:
    comp_availability.render(start_date, end_date, min_date, max_date)
