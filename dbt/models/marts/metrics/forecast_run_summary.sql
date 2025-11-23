{{ config(alias="forecast_run_summary", schema="analytics", materialized="table") }}

with forecasts as (
    select
        run_id,
        date_trunc('month', year_month)::date as year_month,
        sku_id,
        p50
    from analytics.sku_forecasts
),

actuals as (
    select
        sku_id,
        date_trunc('month', demand_date)::date as year_month,
        sum(qty) as actual_units
    from {{ ref('stg_demand') }}
    group by 1,2
),

joined as (
    select
        f.run_id,
        f.sku_id,
        f.year_month,
        f.p50 as forecast_p50_units,
        a.actual_units
    from forecasts f
    join actuals a
      on f.sku_id = a.sku_id
     and f.year_month = a.year_month
),

agg as (
    select
        run_id,
        min(year_month) as horizon_start_month,
        max(year_month) as horizon_end_month,
        count(distinct sku_id) as skus_covered,
        avg(case when actual_units is null or actual_units = 0 then null else abs(forecast_p50_units - actual_units) / nullif(actual_units, 0) end) as mape,
        sum(abs(forecast_p50_units - actual_units)) / nullif(sum(actual_units), 0) as wape,
        avg(case when actual_units is null or actual_units = 0 then null else (forecast_p50_units - actual_units) / nullif(actual_units, 0) end) as bias,
        avg(abs(forecast_p50_units - actual_units)) as mae
    from joined
    group by 1
),

final as (
    select
        run_id,
        'BASE_FORECAST'::text as run_type,
        horizon_start_month,
        horizon_end_month,
        skus_covered,
        mape,
        wape,
        bias,
        mae,
        null::numeric as mape_vs_baseline_delta,
        null::numeric as wape_vs_baseline_delta,
        now() as computed_at
    from agg
)

select * from final
