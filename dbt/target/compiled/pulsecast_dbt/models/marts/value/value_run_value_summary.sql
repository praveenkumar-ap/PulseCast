

with run_metrics as (
    select
        run_id,
        run_type,
        horizon_start_month as period_start,
        horizon_end_month as period_end,
        skus_covered,
        mape,
        wape,
        bias,
        mae,
        mape_vs_baseline_delta,
        wape_vs_baseline_delta
    from "pulsecast"."analytics"."forecast_run_summary"
),
run_value as (
    select
        rm.run_id,
        rm.run_type,
        rm.period_start,
        rm.period_end,
        rm.skus_covered,
        rm.mape,
        rm.wape,
        rm.bias,
        rm.mae,
        rm.mape_vs_baseline_delta,
        rm.wape_vs_baseline_delta,
        v.rev_uplift_estimate,
        v.scrap_avoidance_estimate,
        v.wc_savings_estimate,
        v.productivity_savings_estimate,
        v.assumptions_json,
        v.computed_at as value_computed_at
    from run_metrics rm
    left join "pulsecast"."analytics"."value_impact_summary" v on rm.run_id = v.run_id
),
scored as (
    select
        run_id,
        run_type,
        null::text as family_id,
        null::text as family_name,
        period_start,
        period_end,
        case
            when mape_vs_baseline_delta is not null then -1 * mape_vs_baseline_delta
            else null
        end as forecast_accuracy_uplift_pct,
        rev_uplift_estimate as revenue_uplift_estimate,
        scrap_avoidance_estimate,
        wc_savings_estimate as working_capital_savings_estimate,
        productivity_savings_estimate as planner_productivity_hours_saved,
        coalesce(rev_uplift_estimate, 0)
            + coalesce(scrap_avoidance_estimate, 0)
            + coalesce(wc_savings_estimate, 0)
            + coalesce(productivity_savings_estimate, 0) as total_value_estimate,
        value_computed_at as computed_at,
        case
            when coalesce(rev_uplift_estimate, 0)
                + coalesce(scrap_avoidance_estimate, 0)
                + coalesce(wc_savings_estimate, 0)
                + coalesce(productivity_savings_estimate, 0) >= 50000 then 'STRETCH'
            when coalesce(rev_uplift_estimate, 0)
                + coalesce(scrap_avoidance_estimate, 0)
                + coalesce(wc_savings_estimate, 0)
                + coalesce(productivity_savings_estimate, 0) >= 10000 then 'BASE'
            else 'CONSERVATIVE'
        end as case_label
    from run_value
)

select * from scored