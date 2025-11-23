{{ config(alias="stream_raw", schema="signals", materialized="table") }}

with template as (
    select
        cast(null as uuid) as event_id,
        cast(null as text) as indicator_id,
        cast(null as timestamp) as event_time,
        cast(null as text) as geo,
        cast(null as numeric) as value,
        cast(null as text) as source_system,
        cast(null as timestamp) as ingested_at,
        cast(null as text) as payload_json
    where 1 = 0
)

select * from template
