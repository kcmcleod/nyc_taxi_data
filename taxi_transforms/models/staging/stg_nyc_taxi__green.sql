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
)

select * exclude (total_amount),
    -- Reconstruct the total amount to fix upstream meter addition bugs
    (
        fare_amount + extra_charges + mta_tax + tip_amount + tolls_amount +
        improvement_surcharge + congestion_surcharge + cbd_congestion_fee +
        coalesce(airport_fee, 0)
    ) as total_amount
from renamed
where pick_up_date_time >= '2023-01-01'
    and trip_distance_miles >= 0
    and passenger_count between 0 and 8
    -- Keep trips that are still open or have a valid duration
    and (drop_off_date_time is NULL or pick_up_date_time != drop_off_date_time)
    -- Filter out false meter drops (under 60 seconds AND 0 passengers)
    and not (
        date_diff('second', pick_up_date_time, drop_off_date_time) < 60
        and coalesce(passenger_count, 0) = 0
    )
    -- Filter junk mta
    and mta_tax between 0 and 1.5
    -- Filter out refunds, disputes, and voided trips
    and fare_amount > 0
    and total_amount > 0
    and (airport_fee is null or airport_fee >= 0)
    -- Filter out ghost trips: fare charged but no distance recorded
    and not (trip_distance_miles = 0 and fare_amount > 0)
    -- Short trips (< 1 mile): Allow high CPM due to fixed base fares and traffic idling
    and not (trip_distance_miles < 1 and (fare_amount / nullif(trip_distance_miles, 0)) > 100)
    -- Standard trips (1 to 10 miles): Cap at a reasonable heavy traffic rate ($20/mile)
    and not (trip_distance_miles >= 1 and trip_distance_miles <= 10 and (fare_amount / nullif(trip_distance_miles, 0)) > 20)
    -- Long hauls (> 10 miles): Cap at $10/mile 
    and not (trip_distance_miles > 10 and (fare_amount / nullif(trip_distance_miles, 0)) > 10)
    -- Filter out really low CPM
    and not (trip_distance_miles > 5 and (fare_amount / nullif(trip_distance_miles, 0)) < 0.50)
    -- Filter out jounerys longer than 6 hours
    and date_diff('hour', pick_up_date_time, drop_off_date_time) <= 6

{% if target.name == 'dev' %}
    limit 100000
{% endif %}

