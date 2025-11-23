
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select indicator_id
from "pulsecast"."monitor"."indicator_freshness_status"
where indicator_id is null



  
  
      
    ) dbt_internal_test