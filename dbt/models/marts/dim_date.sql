select distinct
    event_date as date_day,
    extract(year from event_date) as year,
    extract(month from event_date) as month,
    extract(day from event_date) as day,
    extract(dow from event_date) as day_of_week,
    to_char(event_date, 'Day') as day_name,
    to_char(event_date, 'Month') as month_name
from {{ ref('stg_events') }}