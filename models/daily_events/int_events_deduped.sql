-- Current duplicate rule: drop exact re-deliveries (rows with the same event_id).
select *
from {{ ref('stg_events') }}
qualify row_number() over (partition by event_id order by event_ts) = 1
