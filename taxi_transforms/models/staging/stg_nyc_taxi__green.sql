with source as (
    select *
    from {{ source('raw_nyc_taxi', 'green') }}
),

renamed as (
    select * exclude (
            VendorID,
            RatecodeID,
            PULocationID,
            DOLocationID,
            payment_type,
            trip_type,
            passenger_count,
            trip_distance,
            fare_amount,
            extra,
            mta_tax,
            tip_amount,
            tolls_amount,
            improvement_surcharge,
            congestion_surcharge,
            cbd_congestion_fee,
            -- airport_fee is not in green data
            -- ehail_fee is present but seems to be null in later years
            total_amount,
            store_and_fwd_flag,
            lpep_pickup_datetime,
            lpep_dropoff_datetime
        ),

        -- check for drift in data types; error will stop forward progress

        ---------- ids
        cast(VendorID as integer) as vendor_id,
        coalesce(cast(RatecodeID as integer), 99) as rate_code_id,
        cast(PULocationID as integer) as pick_up_location_id,
        cast(DOLocationID as integer) as drop_off_location_id,
        coalesce(cast(payment_type as integer), 5) as payment_type_id,
        coalesce(cast(trip_type as integer), 99) as trip_type_id,

        ---------- numerics
        passenger_count is NULL as is_passenger_count_missing,
        coalesce(cast(passenger_count as integer), 1) as passenger_count,
        cast(trip_distance as float) as trip_distance_miles,
        cast(fare_amount as float) as fare_amount,
        cast(extra as float) as extra_charges,
        cast(mta_tax as float) as mta_tax,
        cast(tip_amount as float) as tip_amount,
        cast(tolls_amount as float) as tolls_amount,
        cast(improvement_surcharge as float) as improvement_surcharge,
        congestion_surcharge is NULL as is_congestion_surcharge_missing,
        coalesce(cast(congestion_surcharge as float), 0) as congestion_surcharge,
        cbd_congestion_fee is NULL as is_cbd_congestion_fee_missing,
        coalesce(cast(cbd_congestion_fee as float), 0) as cbd_congestion_fee,
        TRUE as is_airport_fee_missing,
        cast(NULL as float) as airport_fee,
        cast(total_amount as float) as total_amount,

        ---------- string
        coalesce(cast(store_and_fwd_flag as character), 'M') as store_and_fwd_flag,

        ---------- timestamps
        cast(lpep_pickup_datetime as timestamp) as pick_up_date_time,
        case
            when lpep_dropoff_datetime < pick_up_date_time then cast(NULL as timestamp)
            else cast(lpep_dropoff_datetime as timestamp)
        end as drop_off_date_time

    from source

    {% if target.name == 'dev' %}
        limit 100000
    {% endif %}

)

select * from renamed
-- filter out 0 duration trips
where pick_up_date_time != drop_off_date_time or drop_off_date_time is NULL
