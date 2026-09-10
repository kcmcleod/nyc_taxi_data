with

source as (

    select * from {{ source('raw_nyc_taxi', 'green') }}

),

renamed as (

    select

        ---------- ids
        VendorID as vendor_id,
        RatecodeID as rate_code_id,
        PULocationID as pick_up_location_id,
        DOLocationID as drop_off_location_id,
        payment_type as payment_type_id,
        trip_type as trip_type_id,
        
        ---------- numerics
        passenger_count,
        trip_distance as trip_distance_miles,
        fare_amount,
        extra as extra_charges,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,        
        congestion_surcharge,
        cbd_congestion_fee,
        cast(null as numeric) as airport_fee, 
        total_amount,
        store_and_fwd_flag, 

        ---------- timestamps
        lpep_pickup_datetime as pick_up_date_time,
        lpep_dropoff_datetime as drop_off_date_time

    from source

)

select * from renamed