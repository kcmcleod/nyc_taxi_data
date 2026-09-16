with unioned_data as (
    select * from {{ ref('int_nyc_taxi__unioned') }}
),

trip_indicators as (

    select distinct 
        is_airport_fee_missing,
        is_cbd_congestion_fee_missing,
        is_congestion_surcharge_missing,
        is_passenger_count_missing,
        service_type,
        store_and_fwd_flag
    from unioned_data
)

select 
    {{ dbt_utils.generate_surrogate_key(['service_type', 'store_and_fwd_flag', 'is_airport_fee_missing', 'is_passenger_count_missing', 'is_cbd_congestion_fee_missing', 'is_congestion_surcharge_missing']) }} as trip_indicators_id, 
    is_airport_fee_missing,
    is_cbd_congestion_fee_missing,
    is_congestion_surcharge_missing,
    is_passenger_count_missing,
    service_type,
    store_and_fwd_flag
from trip_indicators
