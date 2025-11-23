
  
    

  create  table "pulsecast"."platform"."api_audit_log__dbt_tmp"
  
  
    as
  
  (
    

with template as (
    select
        cast(null as uuid) as id,
        cast(null as text) as tenant_id,
        cast(null as text) as user_id,
        cast(null as text) as user_role,
        cast(null as text) as path,
        cast(null as text) as method,
        cast(null as integer) as status_code,
        cast(null as timestamp) as timestamp,
        cast(null as text) as action,
        cast(null as text) as entity_type,
        cast(null as text) as entity_id,
        cast(null as text) as payload_hash
    where 1 = 0
)

select * from template
  );
  