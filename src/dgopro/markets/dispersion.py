from __future__ import annotations
from math import exp, lgamma, log
from typing import Any

def dixon_coles_tau(home: int, away: int, lambda_home: float, lambda_away: float, rho: float) -> float:
    if home==0 and away==0: return 1-lambda_home*lambda_away*rho
    if home==0 and away==1: return 1+lambda_home*rho
    if home==1 and away==0: return 1+lambda_away*rho
    if home==1 and away==1: return 1-rho
    return 1.0

def poisson_pmf(mu: float, k: int) -> float:
    return exp(-mu+k*log(mu)-lgamma(k+1)) if mu>0 else (1.0 if k==0 else 0.0)

def dixon_coles_matrix(lambda_home: float, lambda_away: float, rho: float=-0.08, max_goals: int=10) -> dict[str,float]:
    raw={}
    for h in range(max_goals+1):
        for a in range(max_goals+1):
            raw[f"{h}-{a}"]=max(0.0,poisson_pmf(lambda_home,h)*poisson_pmf(lambda_away,a)*dixon_coles_tau(h,a,lambda_home,lambda_away,rho))
    z=sum(raw.values())
    return {k:v/z for k,v in raw.items()} if z else raw

def negative_binomial_pmf(mu: float, dispersion: float, k: int) -> float:
    if mu<0 or dispersion<=0 or k<0: raise ValueError("invalid negative-binomial parameters")
    r=dispersion
    if mu==0: return 1.0 if k==0 else 0.0
    p=r/(r+mu)
    return exp(lgamma(k+r)-lgamma(r)-lgamma(k+1)+r*log(p)+k*log(1-p))

def negative_binomial_distribution(mu: float, dispersion: float, max_count: int=60) -> dict[int,float]:
    d={k:negative_binomial_pmf(mu,dispersion,k) for k in range(max_count+1)}
    z=sum(d.values())
    return {k:v/z for k,v in d.items()}

def variance_from_nb(mu: float, dispersion: float) -> float:
    return mu+(mu*mu/dispersion)
