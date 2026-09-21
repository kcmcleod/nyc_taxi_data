{{
    config(
        materialized='incremental',
        incremental_strategy = 'merge',
        on_schema_change = 'append_new_columns',
        unique_key = ['taxi_trip_id']
    )
}}


with unioned_data as (
    select * 
    from {{ ref('int_nyc_taxi__unioned') }}
    {% if is_incremental() %}
        where drop_off_date_time >= (select coalesce(max(drop_off_date_time), cast('2022-01-01' as timestamp)) from {{ this }} )
    {% endif %}

)

select
    * exclude (
        ehail_fee,
        is_airport_fee_missing,
        is_cbd_congestion_fee_missing,
        is_congestion_surcharge_missing,
        is_passenger_count_missing,
        service_type,
        store_and_fwd_flag
    ),
    {{ dbt_utils.generate_surrogate_key(['service_type', 'store_and_fwd_flag', 'is_airport_fee_missing', 'is_passenger_count_missing', 'is_cbd_congestion_fee_missing', 'is_congestion_surcharge_missing']) }} as trip_indicators_id
from unioned_data
