---
title: |
  Session 3\
  Support Vector Machines
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 3 — Lecture
---

# The linear SVM

## Separating classes with a line

![](img/svm_setting.png)

## Which line?

![](img/svm_which.png)

## The widest street

![](img/svm_margin.png)

## Width of the street

![](img/eq_margin.png)

## Fixing the scale

![](img/canonical.png)

## Optimization problem

![](img/eq_primal.png)

## Lagrangian to α ≥ 0 constraints

![](img/eq_squared_slack.png)

## Expressing constraint in two ways

![](img/slack_or_max.png)

## Dual formulation

![](img/eq_dual.png)

## The Lagrangian has a saddle

![](img/duality_saddle.png)

## Reading the primal back off the dual

![](img/kkt_recover.png)

## Only a few points matter

![](img/support_vectors.png)

# The soft margin

## When no line works

![](img/not_separable.png)

## Slack

![](img/slack_idea.png)

## Soft-margin problem

![](img/eq_soft.png)

## C: how much misbehaviour is allowed?

![](img/svm_c.png)

## The loss

![](img/eq_svm.png)

## Hinge, log loss, squares

![](img/hinge_loss.png)

# Kernels

## The kernel trick

![](img/svm_kernel.png)

## XOR

![](img/xor_example.png)

## Why the trick works

![](img/eq_kernel_trick.png)

## RBF kernel

![](img/svm_similarity.png)

## Kernel requirements

![](img/eq_kernel_conditions.png)

## Typical kernels

![](img/svm_kernel_zoo.png)

## Kernels in practice

![](img/svm_kernels.png)

## Scale features first

![](img/feature_scaling.png)

## Choosing C and γ

![](img/kernel_cv.png)

## Dual problem with a kernel

![](img/eq_kernel_dual.png)

## What kernels cost

![](img/kernel_props.png)

## SVMs scaling

![](img/svm_cost.png)

## More than two classes

![](img/multiclass.png)

# Beyond classification

## The same idea, for regression

![](img/svr.png)

## Regression in the dual

![](img/svr_dual.png)

## The width of the tube

![](img/svr_epsilon.png)

## Recap

![](img/svm_map.png)

## Next week

Density-based and hierarchical clustering:\
learning without labels.
