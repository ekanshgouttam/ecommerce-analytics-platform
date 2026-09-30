select
    experiment_name,
    control_n,
    treatment_n,
    round(control_rate::numeric, 4) as control_rate,
    round(treatment_rate::numeric, 4) as treatment_rate,
    round(relative_lift::numeric, 4) as relative_lift,
    round(p_value::numeric, 4) as p_value,
    is_significant,
    round(ci_low::numeric, 4) as ci_low,
    round(ci_high::numeric, 4) as ci_high
from experiment_analysis