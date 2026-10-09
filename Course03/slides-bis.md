---
title: |
  Trees, Forests and Boosting
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 3 — Lecture
---

# Decision trees

## A tree is a sequence of questions

![](img-bis/tree_questions.png)

## Choosing the split

![](img-bis/tree_split.png)

## What "pure" means

![](img-bis/impurity.png)

## Depth is the capacity knob

![](img-bis/tree_grow.png)

## Regression trees predict staircases

![](img-bis/tree_regression.png)

## And they over-fit

![](img-bis/tree_overfit.png)

## The real problem: instability

![](img-bis/tree_instability.png)

# Random forests

## The idea

![](img-bis/forest_idea.png)

## Trees must disagree

![](img-bis/eq_forest_variance.png)

## Averaging is not magic

![](img-bis/forest_variance.png)

## What max_features does

![](img-bis/max_features.png)

## The knob: max_features

![](img-bis/forest_features.png)

## Two injections of randomness

![](img-bis/forest_diagram.png)

## The boundary stops twitching

![](img-bis/forest_boundary.png)

## Strength against diversity

![](img-bis/forest_correlation.png)

## More trees never over-fits

![](img-bis/forest_ntrees.png)

# Boosting

## Combine many trees differently

![](img-bis/boosting_stages.png)

## Forest and boosting attack different errors

![](img-bis/bagging_vs_boosting.png)

## Boosting *can* over-fit

![](img-bis/boosting_overfit.png)

## Boosting as an additive model

![](img-bis/additive_model.png)

## Boosting is gradient descent in function space

![](img-bis/eq_boosting.png)

# Shrinkage

## Shrinkage

![](img-bis/shrinkage.png)

## The learning rate is a regulariser

![](img-bis/learning_rate.png)

# XGBoost

## Regularisation inside the tree objective

![](img-bis/eq_xgboost.png)

## Splitting candidates

![](img-bis/xgb_split_search.png)

## Loss simplification for one leaf

![](img-bis/eq_leaf_objective.png)

## Scoring candidate splits

![](img-bis/xgb_leaf_score.png)

## Gradient and Hessian

![](img-bis/xgb_gh.png)

## Summing trees to get the prediction

![](img-bis/xgb_leaf_predict.png)

# LightGBM

## Bin each feature once

![](img-bis/lgbm_bins.png)

## Finding the optimal cut in one sweep

![](img-bis/lgbm_prefix.png)

## Scan bin edges, not rows

![](img-bis/lgbm_binned_scan.png)

## A child's histogram is the parent minus its sibling

![](img-bis/lgbm_subtract.png)

## Leaf-wise growth: spend every split where it pays most

![](img-bis/lgbm_leafwise.png)

## GOSS: sample the rows that are already fitted

![](img-bis/lgbm_goss.png)

# CatBoost

## Categories: the target statistic problem

![](img-bis/cat_example.png)

## The encoding leaks the label

![](img-bis/cat_leak_why.png)

## Ordered target statistics: use only what came before

![](img-bis/cat_chain.png)

## Ordered target statistics: the correlation is gone

![](img-bis/cat_ordered_ts.png)

## Oblivious trees: one split per level

![](img-bis/cat_oblivious.png)

## XGBoost, LightGBM, CatBoost

![](img-bis/gbm_compare.png)
