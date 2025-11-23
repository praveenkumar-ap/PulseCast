{{ config(alias="forecast_accuracy_by_sku_month", schema="analytics", materialized="table") }}

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

final as (
    select
        run_id,
        sku_id,
        year_month,
        actual_units,
        forecast_p50_units,
        abs(forecast_p50_units - actual_units) as abs_error,
        case when actual_units = 0 then null else abs(forecast_p50_units - actual_units) / nullif(actual_units, 0) end as ape
    from joined
)

select * from final
