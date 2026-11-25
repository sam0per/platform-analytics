-- Usage per customer over the 90-day window. "Last 30 days" counts back from the newest usage date.
with bounds as (
    select max(usage_date) as last_day from {{ ref('stg_usage') }}
)

select
    a.customer_id,
    count(u.usage_date) as days_active_90d,
    count(u.usage_date) filter (where u.usage_date > b.last_day - interval 30 day) as days_active_last_30,
    coalesce(sum(u.minutes), 0) as minutes_90d,
    max(u.usage_date) as last_active_date
from {{ ref('stg_accounts') }} as a
cross join bounds as b
left join {{ ref('stg_usage') }} as u on u.customer_id = a.customer_id
group by a.customer_id
