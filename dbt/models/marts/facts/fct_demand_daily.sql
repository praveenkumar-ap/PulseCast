{{ config(alias="fct_demand_daily") }}

with demand as (
    select
        sku_id,
        demand_date,
        sum(qty) as qty
    from {{ ref('stg_demand') }}
    group by 1, 2
),

joined as (
    select
        d.sku_id,
        d.demand_date,
        d.qty,
        ds.family_id
    from demand d
    left join {{ ref('dim_sku') }} ds
      on d.sku_id = ds.sku_id
)

select * from joined
