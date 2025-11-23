{{ config(alias="stg_sku") }}

with source as (
    select * from {{ ref('seed_sku') }}
)

select
    cast(sku_id as text) as sku_id,
    cast(sku_code as text) as sku_code,
    cast(sku_name as text) as sku_name,
    cast(family_id as text) as family_id,
    cast(family_name as text) as family_name,
    cast(shelf_life_days as integer) as shelf_life_days,
    cast(uom as text) as uom
from source
