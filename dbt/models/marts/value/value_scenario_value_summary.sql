{{ config(alias="scenario_value_summary", schema="value", materialized="table") }}

with header as (
    select
        scenario_id,
        name,
        status,
        base_run_id,
        uplift_percent,
        created_at
    from {{ ref('scenarios_header') }}
),
results as (
    select
        scenario_id,
        sum(p50) as total_p50
    from {{ ref('scenarios_results') }}
    group by scenario_id
),
inventory as (
    select
        source_id::uuid as scenario_id,
        count(*) as rec_count
    from {{ ref('inventory_recommendations') }}
    where source_type = 'SCENARIO'
    group by source_id
),
scored as (
    select
        h.scenario_id,
        h.name as scenario_name,
        h.base_run_id,
        h.status,
        null::text as family_id,
        null::text as family_name,
        coalesce(h.uplift_percent, 0) as uplift_percent,
        coalesce(r.total_p50, 0) as total_p50_forecast,
        -- simple heuristic estimates based on uplift percent and total volume
        coalesce(r.total_p50, 0) * coalesce(h.uplift_percent, 0) / 100.0 * 10 as expected_revenue_uplift_estimate,
        coalesce(r.total_p50, 0) * 0.02 as expected_scrap_avoidance_estimate,
        coalesce(r.total_p50, 0) * 0.01 as expected_working_capital_effect,
        coalesce(h.uplift_percent, 0) as expected_service_level_change,
        coalesce(r.total_p50, 0) * coalesce(h.uplift_percent, 0) / 100.0 * 10
            + coalesce(r.total_p50, 0) * 0.02
            + coalesce(r.total_p50, 0) * 0.01 as total_expected_value_estimate,
        case
            when coalesce(r.total_p50, 0) * coalesce(h.uplift_percent, 0) / 100.0 * 10 >= 50000 then 'STRETCH'
            when coalesce(r.total_p50, 0) * coalesce(h.uplift_percent, 0) / 100.0 * 10 >= 10000 then 'BASE'
            else 'CONSERVATIVE'
        end as case_label,
        i.rec_count,
        h.created_at
    from header h
    left join results r on h.scenario_id = r.scenario_id
    left join inventory i on h.scenario_id = i.scenario_id
)

select * from scored
