
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select year_month
from "pulsecast"."monitor"."forecast_accuracy_daily"
where year_month is null



  
  
      
    ) dbt_internal_test