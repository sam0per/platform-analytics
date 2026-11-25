-- Only non-personal columns leave the raw file: names, emails and birth dates stay out.
select
    customer_id,
    year(cast(birth_date as date)) as birth_year,
    state
from read_csv('data/raw/customers.csv', header = true, all_varchar = true)
