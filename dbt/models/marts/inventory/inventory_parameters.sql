{{ config(alias="parameters", schema="inventory", materialized="table") }}

with template as (
    select
        cast(null as text) as sku_id,
        cast(null as text) as location_id,
        cast(null as numeric) as service_level_target,
        cast(null as integer) as lead_time_days,
        cast(null as integer) as review_period_days,
        cast(null as numeric) as min_order_qty,
        cast(null as numeric) as max_order_qty
    where 1 = 0
)

select * from template
