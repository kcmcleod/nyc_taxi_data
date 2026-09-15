
with trip_data as (
    select * from {{ ref('fct_nyc_taxi__trips') }}
),

vendor_data as (
    select * from {{ ref('vendor_lookup') }}
),

payment_type_data as (
    select * from {{ ref('payment_type_lookup') }}
),

rate_code_data as (
    select * from {{ ref('rate_code_lookup') }}
),

trip_type_data as (
    select * from {{ ref('trip_type_lookup') }}
),

location_data as (
    select * from {{ ref('taxi_zone_lookup') }}
),

junk_data as (
    select * from {{ ref('dim_nyc_taxi__trip_indicators')}}
),

joined_data as (
   select 
        -- basic trip info
        t.taxi_trip_id,
        jd.service_type,
        tt.trip_type_name,        

        -- costs/charges
        rc.rate_code_name,
        t.airport_fee,
        jd.is_airport_fee_missing,
        t.cbd_congestion_fee,
        jd.is_cbd_congestion_fee_missing,
        t.congestion_surcharge,
        jd.is_congestion_surcharge_missing,
        t.extra_charges,
        t.fare_amount,
        t.improvement_surcharge,
        t.mta_tax,
        t.tip_amount,
        t.tolls_amount,
        t.total_amount,
        
        -- journey metrics
        t.trip_distance_miles,
        t.passenger_count,
        jd.is_passenger_count_missing,

        -- payment details
        v.vendor_name,
        pt.payment_type_name,

        -- pick up 
        t.pick_up_date_time,
        pu.borough_name as pick_up_borough,
        pu.service_zone as pick_up_service_zone,
        pu.zone_name as pick_up_zone,

        -- drop off 
        t.drop_off_date_time,
        dof.borough_name as drop_off_borough,
        dof.service_zone as drop_off_service_zone,
        dof.zone_name as drop_off_zone,

   from trip_data as t
   left join vendor_data as v using(vendor_id)
   left join payment_type_data as pt using(payment_type_id)
   left join rate_code_data as rc using(rate_code_id)
   left join trip_type_data as tt using(trip_type_id)
   left join location_data as pu on t.pick_up_location_id = pu.location_id
   left join location_data as dof on t.drop_off_location_id = dof.location_id
   left join junk_data as jd using(trip_indicators_id)
)


select *
from joined_data





