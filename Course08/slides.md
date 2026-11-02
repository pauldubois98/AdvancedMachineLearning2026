---
title: |
  Session 8\
  Model Order Selection
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 7 — Lecture
---
## Kernel of SVM

![](img/svm_sigma.png)

## Kernel of SVM

![](img/knob_svm_c.png)

## Naive Bayes, LDA, QDA
![](img/knob_rigid_vs_flexible.png)

## Ridge regression

![](img/knob_ridge_lambda.png)

## k-means

![](img/knob_kmeans_k.png)

## DBSCAN

![](img/knob_dbscan_eps.png)

## Non-negative Matrix Factorization

![](img/knob_nmf_rank.png)

## Gaussian mixture

![](img/knob_gmm_k.png)

## Classification and regression
![](img/knob_recap_supervised.png)

## Clustering, mixtures, factorization

![](img/knob_recap_unsupervised.png)

## Choosing hyper-parameter values
![](img/todays_question.png)

## An unfitted parameter

![](img/selection_setting.png)

## Classic example

![](img/curve_fitting.png)

## Fitting a polynomial

![](img/eq_poly_fit.png)

## Effect of model order

![](img/poly_orders.png)

## Training error against test error

![](img/train_vs_test.png)

## Inside the over-fitted model

![](img/coefficients_blow_up.png)

## Modern solution
![](img/more_data.png)

## Vocabulary

![](img/overfit_underfit.png)

## True risk

![](img/eq_risk.png)

## Empirical risk

![](img/eq_empirical_risk.png)

## Train vs Test curves

![](img/risk_picture.png)

## Bias and variance

![](img/bias_variance.png)

## Choosing model on test set
![](img/select_on_test.png)

## Hold out, select, report 

![](img/holdout_idea.png)

## K-fold
![](img/kfold_idea.png)

## Choosing the number of folds

![](img/loo_vs_k.png)

## Uncontaminated split

![](img/cv_variants.png)

## Model selection costs

![](img/cv_cost.png)

# Hyper-parameter optimization

## Why this search is hard
![](img/hyper_hard.png)

## Search on a log scale

![](img/log_scale.png)

## The landscape with one knob
![](img/landscape_1d.png)

## The landscape with two knobs

![](img/landscape_2d.png)

## Grid, random, Bayesian

![](img/search_compare.png)

## A cheap stand-in for an expensive score

![](img/bo_surrogate.png)

## Explore or exploit

![](img/bo_acquisition.png)

## The loop

![](img/bo_loop.png)

## In practice: Optuna

![](img/optuna_code.png)

## Reading the history

![](img/optuna_history.png)

## Pruning
![](img/pruning.png)

# Information criteria

## Fit minus penalty

![](img/ic_idea.png)

## Akaike's criterion

![](img/eq_aic.png)

## The Bayesian criterion

![](img/eq_bic.png)

## Two conventions

![](img/eq_ic_conventions.png)

## AIC vs BIC

![](img/aic_vs_bic.png)

## Practical guidelines

![](img/ic_guidelines.png)

## A correction for small samples

![](img/eq_aicc.png)

## How each one is chosen

![](img/knobs_in_practice.png)

## Which tool, when

![](img/method_choice.png)
