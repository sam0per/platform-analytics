-- Some customer_id values arrive with trailing whitespace; trim so joins keep every customer.
select
    trim(customer_id) as customer_id,
    plan_tier,
    monthly_fee,
    seats,
    support_tickets_90d,
    exit_survey_sent
from read_csv('data/raw/features_v2.csv')
