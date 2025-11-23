{{ config(
    schema="analytics",
    materialized="table",
    alias="sku_forecasts"
) }}

with template as (
    select
        cast(null as text) as sku_id,
        cast(null as date) as year_month,
        cast(null as numeric) as p10,
        cast(null as numeric) as p50,
        cast(null as numeric) as p90,
        cast(null as text) as run_id,
        cast(null as timestamp) as created_at
    from {{ ref('dim_sku') }}
    where 1 = 0
)

select * from template
