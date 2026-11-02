---
title: |
  Trees, Forests and Boosting
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 7 — Lecture
---

# Decision trees

## A tree is a sequence of questions

![](img/tree_questions.png)

## Choosing the split

![](img/tree_split.png)

## What "pure" means

![](img/impurity.png)

## Depth is the capacity knob

![](img/tree_grow.png)

## Regression trees predict staircases

![](img/tree_regression.png)

## And they over-fit

![](img/tree_overfit.png)

## The real problem: instability

![](img/tree_instability.png)

# Random forests

## The idea

![](img/forest_idea.png)

## Trees must disagree

![](img/eq_forest_variance.png)

## Averaging is not magic

![](img/forest_variance.png)

## What max_features does

![](img/max_features.png)

## The knob: max_features

![](img/forest_features.png)

## Two injections of randomness

![](img/forest_diagram.png)

## The boundary stops twitching

![](img/forest_boundary.png)

## Strength against diversity

![](img/forest_correlation.png)

## More trees never over-fits

![](img/forest_ntrees.png)

# Boosting

## Combine many trees differently

![](img/boosting_stages.png)

## Forest and boosting attack different errors

![](img/bagging_vs_boosting.png)

## Boosting *can* over-fit

![](img/boosting_overfit.png)

## Boosting as an additive model

![](img/additive_model.png)

## Boosting is gradient descent in function space

![](img/eq_boosting.png)

# Shrinkage

## Shrinkage

![](img/shrinkage.png)

## The learning rate is a regulariser

![](img/learning_rate.png)

# XGBoost

## Regularisation inside the tree objective

![](img/eq_xgboost.png)

## Splitting candidates

![](img/xgb_split_search.png)

## Loss simplification for one leaf

![](img/eq_leaf_objective.png)

## Scoring candidate splits

![](img/xgb_leaf_score.png)

## Gradient and Hessian

![](img/xgb_gh.png)

## Summing trees to get the prediction

![](img/xgb_leaf_predict.png)

# LightGBM

## Bin each feature once

![](img/lgbm_bins.png)

## Finding the optimal cut in one sweep

![](img/lgbm_prefix.png)

## Scan bin edges, not rows

![](img/lgbm_binned_scan.png)

## A child's histogram is the parent minus its sibling

![](img/lgbm_subtract.png)

## Leaf-wise growth: spend every split where it pays most

![](img/lgbm_leafwise.png)

## GOSS: sample the rows that are already fitted

![](img/lgbm_goss.png)

# CatBoost

## Categories: the target statistic problem

![](img/cat_example.png)

## The encoding leaks the label

![](img/cat_leak_why.png)

## Ordered target statistics: use only what came before

![](img/cat_chain.png)

## Ordered target statistics: the correlation is gone

![](img/cat_ordered_ts.png)

## Oblivious trees: one split per level

![](img/cat_oblivious.png)

## XGBoost, LightGBM, CatBoost

![](img/gbm_compare.png)
