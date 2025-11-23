{{ config(alias="alerts", schema="alerts", materialized="table") }}

with template as (
    select
        cast(null as uuid) as alert_id,
        cast(null as text) as indicator_id,
        cast(null as text) as sku_id,
        cast(null as text) as geo_id,
        cast(null as text) as alert_type,
        cast(null as text) as severity,
        cast(null as text) as status,
        cast(null as text) as message,
        cast(null as timestamp) as triggered_at,
        cast(null as timestamp) as acknowledged_at,
        cast(null as timestamp) as created_at,
        cast(null as timestamp) as updated_at
    where 1 = 0
)

select * from template
