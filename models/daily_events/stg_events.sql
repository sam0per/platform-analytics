select
    event_id,
    cast(event_ts as timestamp) as event_ts,
    source,
    event_type,
    severity,
    device
from read_csv('data/raw/events.csv', types = {'event_ts': 'TIMESTAMP'})
