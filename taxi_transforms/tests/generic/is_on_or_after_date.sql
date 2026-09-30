{% test is_on_or_after_date(model, column_name, min_date) %}

with validation as (
    select {{ column_name }} as test_date
    from {{ model }}
)

select *
from validation
where test_date < cast('{{ min_date }}' as timestamp)

{% endtest %}