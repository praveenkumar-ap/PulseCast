{{ config(alias="dim_sku") }}

with source as (
    select * from {{ ref('stg_sku') }}
)

select
    sku_id,
    sku_code,
    sku_name,
    family_id,
    family_name,
    shelf_life_days,
    uom
from source
