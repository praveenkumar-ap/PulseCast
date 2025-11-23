
    
    

select
    id as unique_field,
    count(*) as n_records

from "pulsecast"."platform"."api_audit_log"
where id is not null
group by id
having count(*) > 1


