select
    cast(event_ts as date) as event_date,
    source,
    count(*) as event_count
from {{ ref('int_events_deduped') }}
group by 1, 2
order by 1, 2
