{{ config(alias="label_sku_demand_10m_roll") }}

with daily as (
    select * from {{ ref('fct_demand_daily') }}
),

monthly as (
    select
        sku_id,
        date_trunc('month', demand_date)::date as year_month,
        sum(qty) as monthly_qty
    from daily
    group by 1, 2
),

rolling as (
    select
        sku_id,
        year_month,
        monthly_qty,
        sum(monthly_qty) over (
            partition by sku_id
            order by year_month
            rows between 9 preceding and current row
        ) as demand_10m_rolling
    from monthly
)

select
    sku_id,
    year_month,
    demand_10m_rolling
from rolling
