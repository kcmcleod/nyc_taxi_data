
with yellow_data as (
    select * from {{ ref('stg_nyc_taxi__yellow') }}
),

green_data as (
    select * from {{ ref('stg_nyc_taxi__green') }}
),

unioned_data as (

    select 
        'yellow' as service_type, 
        yellow_data.*     
    from yellow_data
    
    union all

    select 
    'green' as service_type,
        green_data.*
    from green_data
)


   {% if target.name == 'dev' %}
    -- set up for duckdb
    select 
        {{ dbt_utils.generate_surrogate_key(['service_type', 'vendor_id', 'rate_code_id', 'pick_up_location_id', 'drop_off_location_id', 'payment_type_id', 'trip_type_id', 'pick_up_date_time', 'drop_off_date_time', 'fare_amount', 'total_amount', 'trip_distance_miles']) }} as taxi_trip_id,
        ANY_VALUE(COLUMNS(*))
    from unioned_data
    group by taxi_trip_id -- stops dups
   {% else %}
     -- set up for analytics awarehouse
        select 
        {{ dbt_utils.generate_surrogate_key(['service_type', 'vendor_id', 'rate_code_id', 'pick_up_location_id', 'drop_off_location_id', 'payment_type_id', 'trip_type_id', 'pick_up_date_time', 'drop_off_date_time', 'fare_amount', 'total_amount', 'trip_distance_miles']) }} as taxi_trip_id,
        *
    from unioned_data
    qualify row_number() over (partition by taxi_trip_id order by pick_up_date_time desc) = 1
   {% endif %}





