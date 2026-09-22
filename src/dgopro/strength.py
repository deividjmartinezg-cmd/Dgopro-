from __future__ import annotations
from dataclasses import dataclass
from math import exp
from typing import Mapping

@dataclass(frozen=True)
class StrengthInputs:
    elo: float
    xg_rating: float
    player_xi_rating: float = 0.0
    league_strength: float = 0.0
    home_advantage: float = 0.0
    rest_adjustment: float = 0.0

@dataclass(frozen=True)
class StrengthWeights:
    elo: float = 0.55
    xg: float = 0.25
    xi: float = 0.10
    league: float = 0.05
    rest: float = 0.05


def global_strength(x: StrengthInputs, w: StrengthWeights=StrengthWeights()) -> float:
    # Initial challenger weights are hypotheses, never production constants.
    return (w.elo*x.elo + w.xg*x.xg_rating + w.xi*x.player_xi_rating +
            w.league*x.league_strength + w.rest*x.rest_adjustment + x.home_advantage)

def expected_score_probability(home: StrengthInputs, away: StrengthInputs, scale: float=400.0) -> float:
    diff=global_strength(home)-global_strength(away)
    return 1.0/(1.0+10.0**(-diff/scale))

def exponential_decay(days_ago: float, half_life_days: float) -> float:
    if half_life_days <= 0: raise ValueError("half_life_days must be positive")
    return exp(-0.6931471805599453*max(0.0,days_ago)/half_life_days)

def validate_weights(weights: Mapping[str,float]) -> bool:
    return bool(weights) and all(float(v)>=0 for v in weights.values()) and abs(sum(float(v) for v in weights.values())-1.0)<1e-6
