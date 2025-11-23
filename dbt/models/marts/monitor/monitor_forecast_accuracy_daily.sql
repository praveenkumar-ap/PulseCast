{{ config(alias="forecast_accuracy_daily", schema="monitor", materialized="view") }}

with acc as (
    select
        year_month,
        null::text as family_id,
        null::text as family_name,
        avg(ape) as accuracy_metric,
        null::numeric as baseline_accuracy_metric
    from {{ ref('forecast_accuracy_by_sku_month') }}
    group by year_month
)

select
    year_month,
    family_id,
    family_name,
    accuracy_metric,
    baseline_accuracy_metric,
    case
        when baseline_accuracy_metric is null then null
        when baseline_accuracy_metric = 0 then null
        else (baseline_accuracy_metric - accuracy_metric) / baseline_accuracy_metric * 100
    end as accuracy_uplift_pct
from acc
