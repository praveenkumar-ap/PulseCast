{{ config(alias="stg_demand") }}

with source as (
    select * from {{ ref('seed_demand') }}
),

filtered as (
    select
        cast(sku_id as text) as sku_id,
        cast(demand_date as date) as demand_date,
        cast(qty as numeric) as qty
    from source
    where sku_id is not null
      and demand_date is not null
      and qty is not null
      and qty >= 0
)

select * from filtered
