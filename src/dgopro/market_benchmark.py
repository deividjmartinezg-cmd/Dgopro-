from __future__ import annotations
from typing import Any, Mapping

def no_vig_probabilities(decimal_odds: Mapping[str,float]) -> dict[str,float]:
    inv={k:1.0/float(v) for k,v in decimal_odds.items() if float(v)>1.0}
    z=sum(inv.values())
    if not inv or z<=0: raise ValueError("valid decimal odds required")
    return {k:v/z for k,v in inv.items()}

def market_disagreement(model_probability: float, market_probability: float) -> dict[str,Any]:
    gap=float(model_probability)-float(market_probability)
    return {"gap":gap,"absolute_gap":abs(gap),"audit_required":abs(gap)>=.10,"market_is_benchmark_not_target":True}

def clv_decimal(taken_odds: float, closing_odds: float) -> dict[str,float]:
    if taken_odds<=1 or closing_odds<=1: raise ValueError("decimal odds must exceed 1")
    # Positive if the taken price is better than the closing price.
    return {"price_clv":taken_odds/closing_odds-1.0,"implied_probability_shift":1.0/closing_odds-1.0/taken_odds}
