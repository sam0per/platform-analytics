-- Duplicate rule: drop exact re-deliveries (same event_id), then keep one event
-- per source, event_type and device in each minute, so a retrying source counts once.
with redeliveries_removed as (
    select *
    from {{ ref('stg_events') }}
    qualify row_number() over (partition by event_id order by event_ts) = 1
)

select *
from redeliveries_removed
qualify row_number() over (
    partition by source, event_type, device, date_trunc('minute', event_ts)
    order by event_ts, event_id
) = 1
