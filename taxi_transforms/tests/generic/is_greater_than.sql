{% test is_greater_than(model, column_name, compare_column) %}

with validation as (

    select 
        {{ column_name }} as test_val,
        {{ compare_column }} as compare_val
    from {{ model }}

)

select *
from validation
where test_val <= compare_val

{% endtest %}