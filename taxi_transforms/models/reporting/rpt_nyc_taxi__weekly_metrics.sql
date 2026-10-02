{{
    config(
        materialized='view'
    )
}}

SELECT
    CAST(date_trunc('week', pick_up_date_time) AS DATE) AS agg_trip_date,
    pick_up_borough,
    drop_off_borough,
    vendor_name,
    rate_code_name,
    service_type,
    COUNT(*) AS total_trip_count,
    SUM(passenger_count) AS total_passenger_count,
    SUM(trip_distance_miles) AS total_trip_distance_miles,
    SUM(fare_amount) AS total_fare_amount,
    SUM(total_amount) AS total_amount_charged
FROM {{ ref('obt_nyc_taxi__trips') }}
GROUP BY 1, 2, 3, 4, 5, 6
