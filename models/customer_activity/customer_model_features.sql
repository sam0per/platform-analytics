-- One row per customer for the churn model. Every column must be known before the outcome.
with window_start as (
    select min(usage_date) as first_day from {{ ref('stg_usage') }}
)

select
    a.customer_id,
    f.monthly_fee,
    f.seats,
    f.support_tickets_90d,
    f.exit_survey_sent,
    datediff('day', a.signup_date, w.first_day) as tenure_days,
    u.days_active_90d,
    u.days_active_last_30,
    u.minutes_90d,
    a.churned
from {{ ref('stg_accounts') }} as a
cross join window_start as w
inner join {{ ref('stg_features_v2') }} as f on f.customer_id = a.customer_id
inner join {{ ref('int_customer_usage') }} as u on u.customer_id = a.customer_id
