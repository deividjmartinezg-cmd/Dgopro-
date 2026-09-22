from __future__ import annotations
from math import exp
from typing import Any, Mapping

def _sigmoid(z: float) -> float: return 1.0/(1.0+exp(-max(-35.0,min(35.0,z))))

def contextual_xg(shot: Mapping[str,Any]) -> dict[str,Any]:
    # Transparent challenger baseline; coefficients must be learned OOS before production use.
    distance=max(0.0,float(shot.get("distance_m",18.0))); angle=max(0.0,min(3.14159,float(shot.get("angle_rad",.55))))
    pressure=float(bool(shot.get("under_pressure",False))); header=float(shot.get("body_part") == "head")
    through_ball=float(bool(shot.get("through_ball",False))); transition=float(bool(shot.get("transition",False)))
    defenders=max(0.0,float(shot.get("defenders_goal_side",2.0)))
    z=0.4-.095*distance+1.15*angle-.32*pressure-.25*header+.22*through_ball+.18*transition-.12*defenders
    p=_sigmoid(z)
    return {"xg":p,"model":"contextual_xg_challenger","coefficients_fitted":False,"features_used":["distance_m","angle_rad","under_pressure","body_part","through_ball","transition","defenders_goal_side"]}

def post_shot_xg(base_xg: float, *, placement_quality: float, goalkeeper_position_quality: float=.5) -> dict[str,Any]:
    b=min(1-1e-9,max(1e-9,float(base_xg))); placement=max(0,min(1,float(placement_quality))); keeper=max(0,min(1,float(goalkeeper_position_quality)))
    logit=__import__("math").log(b/(1-b)); p=_sigmoid(logit+1.1*(placement-.5)-.8*(keeper-.5))
    return {"psxg":p,"model":"psxg_challenger","coefficients_fitted":False}
