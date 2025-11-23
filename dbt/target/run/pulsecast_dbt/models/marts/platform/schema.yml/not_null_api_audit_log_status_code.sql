
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select status_code
from "pulsecast"."platform"."api_audit_log"
where status_code is null



  
  
      
    ) dbt_internal_test