{{ config(alias="ledger_latest", schema="scenarios", materialized="view") }}

with ranked as (
    select
        scenario_id,
        action_type,
        actor,
        actor_role,
        comments,
        created_at,
        row_number() over (partition by scenario_id order by created_at desc) as rn
    from {{ ref('scenarios_ledger') }}
)

select
    scenario_id,
    action_type as last_action_type,
    actor as last_actor,
    actor_role as last_actor_role,
    comments as last_comments,
    created_at as last_event_at
from ranked
where rn = 1
