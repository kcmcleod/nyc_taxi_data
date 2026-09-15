with unioned_data as (
    select * from {{ ref('int_nyc_taxi__unioned') }}
),

all_trips as (
    select *
    from unioned_data
)

select 
    taxi_trip_id,
    airport_fee,
    cbd_congestion_fee,
    congestion_surcharge,
    drop_off_date_time,
    drop_off_location_id,
    extra_charges,
    fare_amount,
    improvement_surcharge,
    mta_tax,
    passenger_count,
    payment_type_id,
    pick_up_date_time,
    pick_up_location_id,
    rate_code_id,
    tip_amount,
    tolls_amount,
    total_amount,
    trip_distance_miles,
    {{ dbt_utils.generate_surrogate_key(['service_type', 'store_and_fwd_flag', 'is_airport_fee_missing', 'is_passenger_count_missing', 'is_cbd_congestion_fee_missing', 'is_congestion_surcharge_missing']) }} as trip_indicators_id, 
    trip_type_id,
    vendor_id    
from all_trips
