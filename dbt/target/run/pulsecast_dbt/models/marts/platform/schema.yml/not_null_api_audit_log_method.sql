
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select method
from "pulsecast"."platform"."api_audit_log"
where method is null



  
  
      
    ) dbt_internal_test