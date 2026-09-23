from __future__ import annotations
from math import asin, cos, radians, sin, sqrt
from typing import Any, Mapping

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r=6371.0088; p1=radians(lat1); p2=radians(lat2); dp=radians(lat2-lat1); dl=radians(lon2-lon1)
    a=sin(dp/2)**2+cos(p1)*cos(p2)*sin(dl/2)**2
    return 2*r*asin(sqrt(a))

def context_features(*, rest_days: float|None=None, travel_km: float|None=None, timezone_shift_hours: float|None=None, altitude_change_m: float|None=None, matches_last_14d: int|None=None) -> dict[str,Any]:
    rest=None if rest_days is None else max(0.0,float(rest_days)); travel=None if travel_km is None else max(0.0,float(travel_km)); tz=None if timezone_shift_hours is None else abs(float(timezone_shift_hours)); alt=None if altitude_change_m is None else float(altitude_change_m)
    congestion=None if matches_last_14d is None else max(0,int(matches_last_14d))
    components=[]
    if rest is not None: components.append(min(1.0,max(0.0,(5.0-rest)/5.0)))
    if travel is not None: components.append(min(1.0,travel/5000.0))
    if tz is not None: components.append(min(1.0,tz/8.0))
    if alt is not None: components.append(min(1.0,max(0.0,alt)/2500.0))
    if congestion is not None: components.append(min(1.0,max(0,congestion-2)/4.0))
    burden=sum(components)/len(components) if components else None
    return {"rest_days":rest,"travel_km":travel,"timezone_shift_hours":tz,"altitude_change_m":alt,"matches_last_14d":congestion,"context_burden":burden,"effect_on_performance_calibrated":False}
