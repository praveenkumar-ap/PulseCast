
  
    

  create  table "pulsecast"."indicators"."freshness__dbt_tmp"
  
  
    as
  
  (
    

with template as (
    select
        cast(null as text) as indicator_id,
        cast(null as timestamp) as snapshot_time,
        cast(null as timestamp) as last_data_time,
        cast(null as numeric) as lag_hours,
        cast(null as boolean) as is_within_sla,
        cast(null as numeric) as miss_count,
        cast(null as numeric) as late_count,
        cast(null as timestamp) as updated_at
    where 1 = 0
)

select * from template
  );
  