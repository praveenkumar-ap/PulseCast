{{ config(alias="ledger", schema="scenarios", materialized="table") }}

with template as (
    select
        cast(null as uuid) as ledger_id,
        cast(null as uuid) as scenario_id,
        cast(null as integer) as version_seq,
        cast(null as text) as action_type,
        cast(null as text) as actor,
        cast(null as text) as actor_role,
        cast(null as text) as assumptions,
        cast(null as text) as comments,
        cast(null as timestamp) as created_at
    where 1 = 0
)

select * from template
