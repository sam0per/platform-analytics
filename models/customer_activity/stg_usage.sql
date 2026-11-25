select
    customer_id,
    cast(usage_date as date) as usage_date,
    sessions,
    minutes
from read_csv('data/raw/usage.csv')
