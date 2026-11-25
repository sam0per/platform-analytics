-- One row per customer. Active means the customer used the product in the last 30 days of the data.
select
    a.customer_id,
    a.signup_date,
    a.plan_tier,
    u.days_active_90d,
    u.days_active_last_30,
    u.minutes_90d,
    u.last_active_date,
    u.days_active_last_30 > 0 as is_active
from {{ ref('stg_accounts') }} as a
inner join {{ ref('int_customer_usage') }} as u on u.customer_id = a.customer_id
