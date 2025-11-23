
  create view "pulsecast"."indicators"."trust_scores__dbt_tmp"
    
    
  as (
    

with catalog as (
    select * from "pulsecast"."indicators"."catalog"
),
latest_quality as (
    select distinct on (indicator_id)
        indicator_id,
        metric_date,
        correlation_score,
        correlation_stability_score,
        importance_score,
        causality_score,
        data_completeness_pct,
        lead_quality_score,
        last_correlation_range,
        last_eval_at,
        is_recommended,
        notes
    from "pulsecast"."indicators"."quality"
    order by indicator_id, metric_date desc nulls last
),
latest_freshness as (
    select distinct on (indicator_id)
        indicator_id,
        snapshot_time,
        last_data_time,
        lag_hours,
        is_within_sla,
        miss_count,
        late_count,
        updated_at
    from "pulsecast"."indicators"."freshness"
    order by indicator_id, snapshot_time desc nulls last
),
components as (
    select
        c.indicator_id,
        coalesce(q.correlation_score, 0) as correlation_score,
        coalesce(q.correlation_stability_score, 0) as correlation_stability_score,
        coalesce(q.importance_score, 0) as importance_score,
        coalesce(q.causality_score, 0) as causality_score,
        coalesce(q.lead_quality_score, 0) as lead_quality_score,
        coalesce(q.data_completeness_pct, 0) as data_completeness_pct,
        coalesce(q.last_correlation_range, '') as last_correlation_range,
        q.last_eval_at,
        q.is_recommended,
        q.notes,
        f.snapshot_time,
        f.last_data_time,
        f.lag_hours,
        f.is_within_sla,
        f.miss_count,
        f.late_count,
        -- Components scaled 0-100 for simplicity
        round(coalesce(q.correlation_stability_score, 0) * 100, 2) as stability_component,
        round(coalesce(q.lead_quality_score, coalesce((q.correlation_score + q.importance_score + q.causality_score) / nullif(3,0), 0)) * 100, 2) as lead_quality_component,
        case
            when f.is_within_sla then 100
            when f.lag_hours is not null and c.sla_freshness_hours is not null and c.sla_freshness_hours > 0
                then greatest(0, 100 - round((f.lag_hours / c.sla_freshness_hours) * 100, 2))
            else 0
        end as freshness_component
    from catalog c
    left join latest_quality q on c.indicator_id = q.indicator_id
    left join latest_freshness f on c.indicator_id = f.indicator_id
)

select
    indicator_id,
    stability_component,
    lead_quality_component as lead_quality_score,
    freshness_component,
    round((coalesce(stability_component, 0) + coalesce(lead_quality_component, 0) + coalesce(freshness_component, 0)) / 3.0, 2) as trust_score,
    correlation_score,
    correlation_stability_score,
    importance_score,
    causality_score,
    data_completeness_pct,
    last_correlation_range,
    last_eval_at,
    is_recommended,
    notes,
    snapshot_time,
    last_data_time,
    lag_hours,
    is_within_sla,
    miss_count,
    late_count
from components
  );