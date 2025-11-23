
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select timestamp
from "pulsecast"."platform"."api_audit_log"
where timestamp is null



  
  
      
    ) dbt_internal_test