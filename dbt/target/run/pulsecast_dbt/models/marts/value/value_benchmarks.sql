
  create view "pulsecast"."value"."benchmarks__dbt_tmp"
    
    
  as (
    

with runs as (
    select * from "pulsecast"."value"."run_value_summary"
),
agg as (
    select
        'RUN_REV_UPLIFT_MEDIAN' as metric_name,
        'GLOBAL' as scope,
        null::text as scope_key,
        percentile_cont(0.5) within group (order by coalesce(revenue_uplift_estimate,0)) as value_numeric,
        null::text as value_text,
        current_timestamp as as_of_date
    from runs
    union all
    select
        'RUN_TOTAL_VALUE_AVG' as metric_name,
        'GLOBAL' as scope,
        null::text as scope_key,
        avg(total_value_estimate) as value_numeric,
        null::text as value_text,
        current_timestamp as as_of_date
    from runs
    union all
    select
        'RUN_TOTAL_VALUE_P90' as metric_name,
        'GLOBAL' as scope,
        null::text as scope_key,
        percentile_cont(0.9) within group (order by coalesce(total_value_estimate,0)) as value_numeric,
        null::text as value_text,
        current_timestamp as as_of_date
    from runs
)

select * from agg
  );