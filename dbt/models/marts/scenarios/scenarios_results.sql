{{ config(alias="results", schema="scenarios", materialized="table") }}

with template as (
    select
        cast(null as uuid) as scenario_id,
        cast(null as text) as sku_id,
        cast(null as date) as year_month,
        cast(null as text) as base_run_id,
        cast(null as numeric) as p10,
        cast(null as numeric) as p50,
        cast(null as numeric) as p90,
        cast(null as timestamp) as created_at
    where 1 = 0
)

select * from template
