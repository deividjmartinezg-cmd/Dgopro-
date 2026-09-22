# DGOPRO 3.0 Validation Protocol

## Objective
Promote predictive components only when they improve frozen, temporally out-of-sample forecasts. High displayed probability is not an objective.

## Required sequence
1. Validate T-1 provenance and reject temporal leakage.
2. Freeze every prediction before the outcome is known.
3. Split chronologically with walk-forward evaluation; never random-shuffle future observations into training.
4. Evaluate each competition x market x line when sample size permits; use hierarchical pooling when it does not.
5. Report Brier and log loss for binary markets, RPS for 1X2, ECE/reliability, and distributional diagnostics for count markets.
6. Compare against naive/base-rate, Elo, Poisson/Dixon-Coles where applicable, previous DGOPRO champion, and market no-vig probabilities when available.
7. Run feature/model ablations. A feature is retained only when incremental OOS value is demonstrated.
8. Check concept drift and scenario/model disagreement.
9. Audit failures using the error taxonomy; do not retrain because of isolated normal variance.
10. ARB reviews the frozen evidence independently before any champion promotion.

## Promotion principle
A challenger remains a challenger unless sample size, calibration, OOS performance, ablation, drift health and independent review all pass. Promotion is never based on one successful matchday.

## Reporting
Always distinguish event probability from Prediction Quality Score. A lower probability with strong calibration and low uncertainty may be a higher-quality forecast than a larger but fragile probability.
