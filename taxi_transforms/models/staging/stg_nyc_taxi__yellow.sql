with source as (
    select * from {{ source('raw_nyc_taxi', 'yellow') }}
),

renamed as (

    select
        ---------- ids
        VendorID as vendor_id,
        coalesce(RatecodeID, 99) as rate_code_id,
        PULocationID as pick_up_location_id,
        DOLocationID as drop_off_location_id,
        payment_type as payment_type_id,
        cast(99 as integer) as trip_type_id,

        ---------- numerics
        passenger_count is NULL as is_passenger_count_missing,
        coalesce(passenger_count, 1) as passenger_count,
        trip_distance as trip_distance_miles,
        fare_amount,
        extra as extra_charges,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        congestion_surcharge is NULL as is_congestion_surcharge_missing,
        coalesce(congestion_surcharge, 0) as congestion_surcharge,
        cbd_congestion_fee is NULL as is_cbd_congestion_fee_missing,
        coalesce(cbd_congestion_fee, 0) as cbd_congestion_fee,
        airport_fee is NULL as is_airport_fee_missing,
        coalesce(airport_fee, 0) as airport_fee,
        total_amount,

        ---------- string
        coalesce(store_and_fwd_flag, 'M') as store_and_fwd_flag,

        ---------- timestamps
        tpep_pickup_datetime as pick_up_date_time,
        case
            when tpep_dropoff_datetime < pick_up_date_time then cast(NULL as timestamp)
            else tpep_dropoff_datetime
        end as drop_off_date_time

    from source

    {% if target.name == 'dev' %}
    limit 100000
    {% endif %}
)

select * from renamed
where pick_up_date_time != drop_off_date_time or drop_off_date_time is NULL
