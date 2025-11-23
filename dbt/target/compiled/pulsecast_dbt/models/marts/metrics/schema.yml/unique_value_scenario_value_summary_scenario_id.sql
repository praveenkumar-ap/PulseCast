
    
    

select
    scenario_id as unique_field,
    count(*) as n_records

from "pulsecast"."value"."scenario_value_summary"
where scenario_id is not null
group by scenario_id
having count(*) > 1


