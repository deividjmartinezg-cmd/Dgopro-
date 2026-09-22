from __future__ import annotations
from math import exp, factorial
from typing import Any

def poisson_pmf(mu: float, k: int) -> float:
    if mu < 0 or k < 0: raise ValueError("invalid Poisson parameters")
    return exp(-mu)*(mu**k)/factorial(k)

def count_distribution(mu: float, max_count: int=30) -> dict[int,float]:
    probs={k:poisson_pmf(mu,k) for k in range(max_count+1)}
    tail=max(0.0,1.0-sum(probs.values())); probs[max_count]=probs[max_count]+tail
    return probs

def over_probability(distribution: dict[int,float], line: float) -> float:
    return sum(p for k,p in distribution.items() if k>line)

def under_probability(distribution: dict[int,float], line: float) -> float:
    return sum(p for k,p in distribution.items() if k<line)

def quantile(distribution: dict[int,float], q: float) -> int:
    acc=0.0
    for k,p in sorted(distribution.items()):
        acc+=p
        if acc>=q: return k
    return max(distribution)

def summarize(mu: float, lines: tuple[float,...], max_count: int=30) -> dict[str,Any]:
    d=count_distribution(mu,max_count)
    return {"mean":mu,"q10":quantile(d,.10),"median":quantile(d,.50),"q90":quantile(d,.90),"lines":{str(x):{"over":over_probability(d,x),"under":under_probability(d,x)} for x in lines},"distribution":"poisson_challenger","calibrated":False}
