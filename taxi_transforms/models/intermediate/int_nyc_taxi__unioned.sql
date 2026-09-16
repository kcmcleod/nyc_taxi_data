with unioned_data as (
    -- fancy macro instead of union all by name
    {{ dbt_utils.union_relations(
        relations=[
            ref('stg_nyc_taxi__yellow'),
            ref('stg_nyc_taxi__green')
        ],
        source_column_name='raw_service_type'
    ) }}
),

cleaned_data as (
    select
        case
            when raw_service_type like '%yellow%' then 'yellow'
            when raw_service_type like '%green%' then 'green'
        end as service_type,
        * exclude (raw_service_type)
    from unioned_data
)

{% if target.name == 'dev' %}
    -- set up for duckdb
    select
        {{ dbt_utils.generate_surrogate_key(['service_type', 'vendor_id', 'rate_code_id', 'pick_up_location_id', 'drop_off_location_id', 'payment_type_id', 'trip_type_id', 'pick_up_date_time', 'drop_off_date_time', 'fare_amount', 'total_amount', 'trip_distance_miles']) }} as taxi_trip_id,
        ANY_VALUE(columns(*))
    from cleaned_data
    group by taxi_trip_id -- stops dups
{% else %}
     -- set up for analytics awarehouse
        select 
        {{ dbt_utils.generate_surrogate_key(['service_type', 'vendor_id', 'rate_code_id', 'pick_up_location_id', 'drop_off_location_id', 'payment_type_id', 'trip_type_id', 'pick_up_date_time', 'drop_off_date_time', 'fare_amount', 'total_amount', 'trip_distance_miles']) }} as taxi_trip_id,
        *
    from cleaned_data
    qualify row_number() over (partition by taxi_trip_id order by pick_up_date_time desc) = 1
{% endif %}
