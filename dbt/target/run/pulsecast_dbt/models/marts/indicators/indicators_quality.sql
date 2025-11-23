
  
    

  create  table "pulsecast"."indicators"."quality__dbt_tmp"
  
  
    as
  
  (
    

with template as (
    select
        cast(null as text) as indicator_id,
        cast(null as date) as metric_date,
        cast(null as numeric) as correlation_score,
        cast(null as numeric) as correlation_stability_score,
        cast(null as numeric) as importance_score,
        cast(null as numeric) as causality_score,
        cast(null as numeric) as data_completeness_pct,
        cast(null as numeric) as lead_quality_score,
        cast(null as text) as last_correlation_range,
        cast(null as timestamp) as last_eval_at,
        cast(null as boolean) as is_recommended,
        cast(null as text) as notes
    where 1 = 0
)

select * from template
  );
  