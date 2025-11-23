{{ config(alias="value_impact_summary", schema="analytics", materialized="table") }}

with template as (
    select
        cast(null as text) as run_id,
        cast(null as numeric) as rev_uplift_estimate,
        cast(null as numeric) as scrap_avoidance_estimate,
        cast(null as numeric) as wc_savings_estimate,
        cast(null as numeric) as productivity_savings_estimate,
        cast(null as text) as assumptions_json,
        cast(null as timestamp) as computed_at
    where 1 = 0
)

select * from template
