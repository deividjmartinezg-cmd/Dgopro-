from __future__ import annotations
from typing import Any, Mapping

def tactical_matchup(home: Mapping[str,float], away: Mapping[str,float]) -> dict[str,Any]:
    # Dimensionless signals; learned mapping remains a challenger task.
    home_pressure=float(home.get("pressing",.5))-float(away.get("press_resistance",.5))
    away_pressure=float(away.get("pressing",.5))-float(home.get("press_resistance",.5))
    home_width=float(home.get("width",.5))-float(away.get("wide_defense",.5))
    away_width=float(away.get("width",.5))-float(home.get("wide_defense",.5))
    transition_bias=(float(home.get("transition_attack",.5))+float(away.get("transition_attack",.5)))/2
    return {"home_press_edge":home_pressure,"away_press_edge":away_pressure,"home_wide_edge":home_width,"away_wide_edge":away_width,"transition_bias":transition_bias,"mapping_fitted":False}

def game_state_adjustment(base_rate: float, *, score_diff: int=0, minute: int=0, red_card_diff: int=0, knockout_urgency: float=0.0) -> dict[str,Any]:
    rate=max(0.0,float(base_rate)); m=max(0,min(120,int(minute))); urgency=max(-1,min(1,float(knockout_urgency)))
    trailing=max(0,-score_diff); leading=max(0,score_diff)
    factor=1+.06*trailing-.04*leading+.12*red_card_diff+.10*urgency*(m/90 if m else 0)
    return {"adjusted_rate":max(0.0,rate*factor),"factor":factor,"coefficients_fitted":False,"state":{"score_diff":score_diff,"minute":m,"red_card_diff":red_card_diff,"knockout_urgency":urgency}}
