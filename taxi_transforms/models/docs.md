<!-- 
  Centralised dbt Column Documentation
  Reference these using {{ doc('column_name') }} in the schema.yml files
-->

{% docs airport_fee %}
For pick up only at LaGuardia and John F. Kennedy Airports.
{% enddocs %}

{% docs borough_name %}
Name of NYC Borough that will be either the pick up or drop off location.
{% enddocs %}

{% docs cbd_congestion_fee %}
Per-trip charge for MTA's Congestion Relief Zone starting Jan. 5, 2025.
{% enddocs %}

{% docs congestion_surcharge %}
Total amount collected in trip for NYS congestion surcharge.
{% enddocs %}

{% docs drop_off_borough %}
The borough in which the meter was disengaged.
{% enddocs %}

{% docs drop_off_date_time %}
The date and time when the meter was disengaged.
{% enddocs %}

{% docs drop_off_location_id %}
Numeric code for TLC Taxi Zone in which the taximeter was disengaged.
{% enddocs %}

{% docs drop_off_zone %}
Name for NYC Zone in which the taximeter was engaged.
{% enddocs %}

{% docs drop_off_service_zone %}
Name for TLC Taxi Zone in which the taximeter was engaged.
{% enddocs %}

{% docs extra_charges %}
Miscellaneous extras and surcharges.
{% enddocs %}

{% docs fare_amount %}
The time-and-distance fare calculated by the meter. 
{% enddocs %}

{% docs improvement_surcharge %}
Improvement surcharge assessed trips at the flag drop. The improvement surcharge began being levied in 2015.
{% enddocs %}

{% docs location_id %}
Numeric code identifying a location within the NYC Taxi map.
{% enddocs %}

{% docs mta_tax %}
Tax that is automatically triggered based on the metered rate in use.
{% enddocs %}

{% docs passenger_count %}
The number of passengers in the vehicle. 
{% enddocs %}

{% docs payment_type_id %}
A numeric code signifying how the passenger paid for the trip.
{% enddocs %}

{% docs payment_type_name %}
Name of method for how the passenger paid for the trip.
{% enddocs %}

{% docs pick_up_borough %}
The borough in which the meter was engaged.
{% enddocs %}

{% docs pick_up_date_time %}
The date and time when the meter was engaged.
{% enddocs %}

{% docs pick_up_location_id %}
Numeric code for TLC Taxi Zone in which the taximeter was engaged.
{% enddocs %}

{% docs pick_up_zone %}
Name for NYC Zone in which the taximeter was engaged.
{% enddocs %}

{% docs pick_up_service_zone %}
Name for TLC Taxi Zone in which the taximeter was engaged.
{% enddocs %}

{% docs rate_code_id %}
Numeric code for the final rate code in effect at the end of the trip.
{% enddocs %}

{% docs rate_code_name %}
Numeric code of the final rate code in effect at the end of the trip.
{% enddocs %}

{% docs service_type %}
The operational classification of the taxi. Indicates whether the record belongs to a 'green' or 'yellow' medallion trip.
{% enddocs %}

{% docs service_zone %}
The NYC Taxi zone in which the trip started or ended.
{% enddocs %}

{% docs store_and_fwd_flag %}
This flag indicates whether the trip record was held in vehicle memory before sending to the vendor, aka "store and forward," because the vehicle did not have a connection to the server.
{% enddocs %}

{% docs taxi_trip_id %}
A generated surrogate key representing a single taxi trip. 

**Grain:** Hashed combination of `service_type`, `vendor_id`, `rate_code_id`, `pick_up_location_id`, `drop_off_location_id`, `payment_type_id`, `trip_type_id`, `pick_up_date_time`, `drop_off_date_time`, `fare_amount`, `total_amount`, and `trip_distance_miles`.
{% enddocs %}

{% docs tip_amount %}
Tip amount – This field is automatically populated for credit card tips. Cash tips are not included.
{% enddocs %}

{% docs tolls_amount %}
Total amount of all tolls paid in trip.
{% enddocs %}

{% docs total_amount %}
The total amount charged to passengers. Does not include cash tips.
{% enddocs %}

{% docs trip_distance_miles %}
The elapsed trip distance in miles reported by the taximeter.
{% enddocs %}

{% docs trip_indicators_id %}
A generated ID for each row in junk dim, with a row being a unique combination of the following fields (service_type, is_airport_fee_missing)
{% enddocs %}

{% docs trip_type_id %}
A code indicating whether the trip was a street-hail or a dispatch that is automatically assigned based on the metered rate in use but can be altered by the driver. Green taxi data only. 
{% enddocs %}


{% docs trip_type_name %}
<!-- Add description for trip_type_name here -->
{% enddocs %}

{% docs vendor_id %}
A code indicating the TPEP provider that provided the record. 
{% enddocs %}

{% docs vendor_name %}
Name of the TPEP provider that provided the record. 
{% enddocs %}

{% docs zone_name %}
Name of the NYC zone that will be the pick up or drop off location.
{% enddocs %}

{% docs is_airport_fee_missing %}
For the field "airport_fee" was a missing value replaced with a default value (0) during the ETL? True for yes and False for no.
{% enddocs %}

{% docs is_cbd_congestion_fee_missing %}
For the field "cbd_congestion_fee" was a missing value replaced with a default value (0) during the ETL? True for yes and False for no.
{% enddocs %}

{% docs is_congestion_surcharge_missing %}
For the field "congestion_surcharge" was a missing value replaced with a default value (0) during the ETL? True for yes and False for no.
{% enddocs %}

{% docs is_passenger_count_missing %}
For the field "passenger_count" was a missing value replaced with a default value (1) during the ETL? True for yes and False for no.
{% enddocs %}


