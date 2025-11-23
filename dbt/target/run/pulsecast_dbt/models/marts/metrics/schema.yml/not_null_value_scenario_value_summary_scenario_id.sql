
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select scenario_id
from "pulsecast"."value"."scenario_value_summary"
where scenario_id is null



  
  
      
    ) dbt_internal_test