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

