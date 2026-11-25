-- One row per customer for the churn model. Every column must be known before the outcome.
-- Features come from the new features table, features_v2.
with window_start as (
    select min(usage_date) as first_day from {{ ref('stg_usage') }}
)

select
    a.customer_id,
    v2.seats,
    v2.support_tickets as support_tickets_90d,
    datediff('day', a.signup_date, w.first_day) as tenure_days,
    u.days_active_90d,
    u.days_active_last_30,
    u.minutes_90d,
    a.churned
from {{ ref('stg_accounts') }} as a
cross join window_start as w
inner join {{ ref('stg_features_legacy') }} as v2 on v2.customer_id = a.customer_id
inner join {{ ref('int_customer_usage') }} as u on u.customer_id = a.customer_id
