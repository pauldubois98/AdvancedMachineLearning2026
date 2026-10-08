---
title: |
  Session 2\
  Robust Regression
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 2 — Lecture
---

# Reminders: linear regression

## Regression

![](img/regression_setting.png)

## Use cases

![](img/regression_apps.png)

## Why a linear model?

![](img/why_linear.png)

## More columns: the line becomes a plane

![](img/linreg_multi.png)

## "Linear" means linear in the *weights*

![](img/linreg_basis.png)

## Model via matrix multiplication

![](img/eq_linear_model.png)

## Least squares

![](img/ls_residuals.png)

## Analytical solution

![](img/eq_normal_equations.png)

## What the solution is doing

![](img/hat_matrix.png)

## Repeated information

![](img/collinear_example.png)

## Loss with a flat valley

![](img/collinear_valley.png)

## Detecting in practice

![](img/near_collinear.png)

## How precise is the estimate?

![](img/ls_variance.png)

# Regularized regression

## When d gets large

![](img/high_dim.png)

## Add a penalty

![](img/eq_regularized.png)

## Three penalties

![](img/penalty_zoo.png)

## Penalties behavior

![](img/penalty_geometry.png)

## Effect of λ

![](img/lambda_path.png)

## Effect of λ

![](img/thresholding.png)

## Handling non-differentiable penalty

![](img/prox_idea.png)

## The proximal step

![](img/eq_prox.png)

# Robust regression

## Outliers

![](img/outlier_demo.png)

## Why squares break

![](img/squared_loss_pull.png)

## Robustness vs complexity

![](img/outliers_vs_mismodelling.png)

## Likelihood to M-estimation

![](img/eq_m_estimation.png)

## Loss ~ Noise model

![](img/rho_from_density.png)

## Robust regression

![](img/eq_robust_regression.png)

## Possible ρ

![](img/rho_zoo.png)

## δ parameter

![](img/delta_meaning.png)

## δ effect on residual scale

![](img/delta_scale.png)

## Choosing δ

![](img/tuning_delta.png)

## Derivative of ρ

![](img/eq_stationarity.png)

## Interpret as weights

![](img/eq_weight.png)

## Influence of a point

![](img/influence_demo.png)

## Influence and weight
![](img/psi_and_weights.png)

## Weights & data

![](img/weights_on_data.png)

# IRLS algorithm

## Fixed point

![](img/eq_irls.png)

## IRLS loop

![](img/irls_loop.png)

## IRLS step by step

![](img/irls_steps.png)

## IRLS algorithm

![](img/irls_algorithm.png)

## Algorithm approximation

![](img/mm_idea.png)

## ρ requirements for convergence

![](img/eq_mm.png)


## Recap

![](img/robust_map.png)

# Logistic regression

## From regression to classification

![](img/logistic_setting.png)

## Why not least squares on the labels?

![](img/why_not_least_squares.png)

## The sigmoid

![](img/sigmoid.png)

## The log-odds

![](img/eq_logodds.png)

## More than two classes

![](img/eq_softmax.png)

## The loss

![](img/logistic_loss.png)

## Fitting

![](img/eq_logistic_irls.png)

## IRLS quadratic approximation

![](img/logistic_mm.png)

## Logistic regression, step by step

![](img/logistic_fit.png)

## What logistic regression is worth

![](img/logistic_props.png)

## Next week

Support vector machines
