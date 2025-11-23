
  
    

  create  table "pulsecast"."indicators"."catalog__dbt_tmp"
  
  
    as
  
  (
    

with seed as (
    select
        cast(indicator_id as text) as indicator_id,
        cast(name as text) as name,
        cast(description as text) as description,
        cast(category as text) as category,
        cast(frequency as text) as frequency,
        cast(provider as text) as provider,
        cast(owner_team as text) as owner_team,
        cast(owner_contact as text) as owner_contact,
        cast(geo_scope as text) as geo_scope,
        cast(unit as text) as unit,
        cast(nullif(btrim(is_leading_indicator::text), '') as boolean) as is_leading_indicator,
        cast(nullif(btrim(default_lead_months::text), '') as numeric) as default_lead_months,
        cast(nullif(btrim(sla_freshness_hours::text), '') as integer) as sla_freshness_hours,
        cast(sla_coverage_notes as text) as sla_coverage_notes,
        cast(license_type as text) as license_type,
        cast(cost_model as text) as cost_model,
        cast(nullif(btrim(cost_estimate_per_month::text), '') as numeric) as cost_estimate_per_month,
        cast(status as text) as status,
        cast(nullif(btrim(is_external::text), '') as boolean) as is_external,
        cast(nullif(btrim(is_byo::text), '') as boolean) as is_byo,
        cast(tags as text) as tags,
        cast(connector_type as text) as connector_type,
        cast(connector_config as text) as connector_config,
        cast(nullif(btrim(created_at::text), '') as timestamp) as created_at,
        cast(nullif(btrim(updated_at::text), '') as timestamp) as updated_at
    from "pulsecast"."seed"."seed_indicators_catalog"
)

select * from seed
  );
  