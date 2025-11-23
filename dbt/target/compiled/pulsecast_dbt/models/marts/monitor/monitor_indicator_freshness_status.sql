

with cat as (
    select indicator_id, name, provider, sla_freshness_hours
    from "pulsecast"."indicators"."catalog"
),
fresh as (
    select indicator_id, last_data_time, lag_hours
    from "pulsecast"."indicators"."freshness"
)

select
    c.indicator_id,
    c.name as indicator_name,
    c.provider,
    f.last_data_time,
    f.lag_hours,
    c.sla_freshness_hours,
    case
        when f.lag_hours is null or c.sla_freshness_hours is null then null
        when f.lag_hours <= c.sla_freshness_hours then true
        else false
    end as is_within_sla
from cat c
left join fresh f on c.indicator_id = f.indicator_id