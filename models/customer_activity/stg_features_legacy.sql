select
    customer_id,
    plan_tier,
    seats,
    support_tickets,
    cast(snapshot_date as date) as snapshot_date
from read_csv('data/raw/features_legacy.csv')
