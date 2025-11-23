
    
    

select
    run_id as unique_field,
    count(*) as n_records

from "pulsecast"."value"."run_value_summary"
where run_id is not null
group by run_id
having count(*) > 1


