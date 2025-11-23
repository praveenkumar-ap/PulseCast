{{ config(alias="recommendations", schema="inventory", materialized="table") }}

with template as (
    select
        cast(null as uuid) as policy_id,
        cast(null as text) as sku_id,
        cast(null as text) as location_id,
        cast(null as date) as year_month,
        cast(null as text) as source_type,
        cast(null as text) as source_id,
        cast(null as numeric) as service_level_target,
        cast(null as numeric) as safety_stock_units,
        cast(null as numeric) as cycle_stock_units,
        cast(null as numeric) as target_stock_units,
        cast(null as timestamp) as created_at
    where 1 = 0
)

select * from template
