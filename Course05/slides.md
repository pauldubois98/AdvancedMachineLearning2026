---
title: |
  Session 5\
  Non-negative Matrix Factorization
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 5 — Lecture
---

# A matrix as a product

## Reducing size

![](img/factorization_idea.png)

## Modeling problem

![](img/eq_factorization.png)

## Column as a weighted sum

![](img/factorization_columns.png)

## Why non-negative

![](img/why_nonneg.png)

## Additive components

![](img/nmf_vs_pca.png)

## Three questions

![](img/key_aspects.png)

# What it is used for

## Faces: the three matrices

![](img/setup_faces.png)

## Faces: what comes out

![](img/app_faces.png)

## Hyperspectral unmixing: a cube, unfolded

![](img/setup_cube.png)

## Hyperspectral unmixing: the three matrices

![](img/setup_spectral.png)

## Hyperspectral unmixing: what comes out

![](img/app_spectral.png)

## Topics in text: the three matrices

![](img/setup_topics.png)

## Topics in text: what comes out

![](img/app_topics.png)

## Fill missing values

![](img/app_recsys.png)

## Music: the three matrices

![](img/setup_music.png)

## Music: what comes out

![](img/app_music.png)

# Choosing a loss

## Entry by entry

![](img/eq_loss.png)

## Divergence, not distance

![](img/loss_axioms.png)

## Classic choices

![](img/loss_zoo.png)

## Classic choices

![](img/loss_shapes.png)

## Where a loss comes from

![](img/eq_loss_from_noise.png)

## Gaussian noise gives the square

![](img/eq_gaussian_loss.png)

## Poisson counts give KL

![](img/eq_poisson_loss.png)

## Multiplicative noise gives Itakura–Saito

![](img/eq_is_loss.png)

## General formula

![](img/eq_beta_divergence.png)

## Derivative

![](img/eq_beta_gradient.png)

## Choosing the loss

![](img/loss_choice.png)

# Mathematical optimisation

## Problem formulation

![](img/eq_problem.png)

## Convex in each half

![](img/biconvex.png)

## Convex in each half

![](img/biconvex_picture.png)

## The answer is never unique

![](img/eq_ambiguity.png)

## Hard ill-posed problem

![](img/nmf_hardness.png)

# Multiplicative updates

## The Frobenius norm, as a trace

![](img/eq_frobenius.png)

## The gradient

![](img/eq_gradient.png)

## W & H can be swapped

![](img/eq_symmetry.png)

## Gradient descent kept positive

![](img/gradient_negative.png)

## One step size per entry

![](img/eq_mu_derivation.png)

## Why that step size

![](img/mu_eta_why.png)

## Lee and Seung rules

![](img/eq_mu_frobenius.png)

## Why split the gradient

![](img/mu_split_why.png)

## Splitting the gradient

![](img/eq_mu_general.png)

# Why it works

## Two nested arguments

![](img/alternate_vs_majorize.png)

## Minimize a majorant

![](img/mm_idea.png)

<!-- these detailed can be skipped (keep them in comment in case I want to pu them back)
## Three inequalities

![](img/eq_mm_monotone.png)

## Jensen's inequality

![](img/jensen_what.png)

## Jensen on one entry

![](img/eq_jensen_split.png)

## Jensen, drawn

![](img/jensen_picture.png) -->

## What a surrogate is

![](img/eq_surrogate_frobenius.png)

## The quadratic surrogate

![](img/eq_surrogate_jensen.png)

## Minimizing the surrogate

![](img/eq_surrogate_minimize.png)

## Where the step size came from

![](img/mu_eta_surrogate.png)

## The other losses, same recipe

![](img/mu_other_losses.png)

## Multiplicative Updates

![](img/mu_algorithm.png)

## Monotone and slow

![](img/mu_convergence.png)

## Initialization

![](img/init_strategies.png)

## Initialization

![](img/init_geometry.png)

## Initialization

![](img/init_faces.png)

## Initialization

![](img/init_compare.png)

# Weighted NMF

## Entries with different importances

![](img/weighted_idea.png)

## Weighted loss

![](img/eq_weighted_loss.png)

## Weighted rules

![](img/eq_weighted_mu.png)

## Matrix completion

![](img/completion_demo.png)

# Regularized NMF

## Three reasons for a penalty

![](img/reg_idea.png)

## The penalized loss

![](img/eq_reg_loss.png)

## The regularized rules

![](img/eq_reg_mu.png)

## Sparsity

![](img/sparsity_demo.png)

# Other algorithms
## Alternating least squares

![](img/als_idea.png)

## Rank-one layers

![](img/hals_layers.png)

## One layer at a time

![](img/hals_residual.png)

## One entry at a time

![](img/hals_column.png)

## HALS in one slide

![](img/hals_algorithm.png)

## Families of algorithms

![](img/algo_types.png)

## Three algorithms, measured

![](img/algo_compare.png)

## Choosing r

![](img/choosing_r.png)

## NMF

![](img/nmf_props.png)
