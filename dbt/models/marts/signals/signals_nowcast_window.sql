{{ config(alias="nowcast_window", schema="signals", materialized="view") }}

with source as (
    select * from {{ ref('signals_stream_raw') }}
),

recent as (
    select
        indicator_id,
        min(event_time) over (partition by indicator_id) as window_start,
        max(event_time) over (partition by indicator_id) as window_end,
        sum(value) over (partition by indicator_id) as window_value
    from source
    where event_time >= now() - interval '7 days'
),

baseline as (
    select
        indicator_id,
        avg(value) as baseline_value
    from source
    where event_time < now() - interval '7 days'
    group by indicator_id
),

agg as (
    select
        r.indicator_id,
        r.window_start,
        r.window_end,
        r.window_value,
        b.baseline_value,
        r.window_value - b.baseline_value as delta_value,
        case when b.baseline_value = 0 then null else (r.window_value - b.baseline_value) / nullif(b.baseline_value, 0) end as delta_pct
    from recent r
    left join baseline b on r.indicator_id = b.indicator_id
)

select distinct * from agg
