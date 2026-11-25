select
    customer_id,
    cast(signup_date as date) as signup_date,
    plan_tier,
    region,
    churned
from read_csv('data/raw/accounts.csv')
