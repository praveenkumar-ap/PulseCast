{{ config(alias="header", schema="scenarios", materialized="table") }}

with template as (
    select
        cast(null as uuid) as scenario_id,
        cast(null as text) as name,
        cast(null as text) as description,
        cast(null as text) as status,
        cast(null as text) as base_run_id,
        cast(null as numeric) as uplift_percent,
        cast(null as text) as created_by,
        cast(null as timestamp) as created_at,
        cast(null as timestamp) as updated_at
    where 1 = 0
)

select * from template
