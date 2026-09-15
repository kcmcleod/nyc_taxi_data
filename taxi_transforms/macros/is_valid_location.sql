{% test is_valid_location(model, column_name) %}

with validation as (

    select 
        {{ column_name }} as test_val,
    from {{ model }}

)

select *
from validation
where test_val < 1
   or test_val > 265
   or test_val is null

{% endtest %}