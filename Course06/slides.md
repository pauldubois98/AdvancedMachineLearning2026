---
title: |
  Session 6\
  Mixture Models and Expectation-Maximization
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 6 — Lecture
---

# A mixture of populations

## Two regimes in one sample

![](img/mixture_idea.png)

## One bell is not enough

![](img/one_gaussian_fails.png)

## Where mixtures come up

![](img/mixture_apps.png)

## Mixture density

![](img/eq_mixture.png)

## Latent variable

![](img/latent_idea.png)

## Simulating mixture

![](img/generative_sim.png)

## Two components case

![](img/eq_two_component.png)

## A fitted model is

![](img/density_vs_clustering.png)

## Key questions

![](img/key_questions.png)

# What a Gaussian mixture can model

## The model

![](img/eq_gmm.png)

## Sums of normals

![](img/gmm_zoo.png)

## Effect of growing K

![](img/gmm_flexible.png)

## In d dimensions

![](img/eq_gmm_multivariate.png)

## Shapes of the covariance

![](img/covariance_shapes.png)

## Counting parameters

![](img/gmm_params.png)

## Mixture relabeled

![](img/identifiability.png)

## Simulation / Estimation asymmetry

![](img/eq_simulation.png)

# Fitting by maximum likelihood

## Likelihood of observed data

![](img/eq_loglik.png)

## Sum inside the log

![](img/why_hard.png)

## Surface of likelihood

![](img/loglik_landscape.png)

## Likelihood is unbounded

![](img/degeneracy.png)

## If we knew the labels

![](img/complete_data_idea.png)

## Complete-data likelihood splits

![](img/eq_complete_loglik.png)

## Closed form class by class

![](img/eq_complete_mle.png)

## Class probabilities from the fit

![](img/posterior_pointwise.png)

## Along axis

![](img/posterior_curve.png)

## Chicken and egg

![](img/chicken_egg.png)

# Responsibilities

## Bayes (reminder)

![](img/bayes_reminder.png)

## Posterior over the label

![](img/eq_responsibility.png)

## Responsibility

![](img/responsibility_picture.png)

## Responsibility as a matrix

![](img/responsibility_matrix.png)

## Soft and hard

![](img/soft_vs_hard.png)

# Expectation-Maximization algorithm

## Alternate

![](img/em_idea.png)

## Expectation–Maximization

![](img/em_algorithm.png)

## The E-step

![](img/em_estep.png)

## The M-step

![](img/em_mstep.png)

## Weighted by responsibility

![](img/eq_em_mstep.png)

## Example run

![](img/em_run.png)

## Same run

![](img/em_run_2d.png)

## Likelihood evolution

![](img/em_monotone.png)

## Cost per pass

![](img/em_cost.png)

# Why it works

## EM alternate view

![](img/em_two_views.png)

## Splitting the log-likelihood

![](img/eq_elbo.png)

## Lower bound on the log-likelihood

![](img/eq_elbo_gap.png)

## Jensen step

![](img/jensen_step.png)

## Jensen inequality

![](img/jensen_picture.png)

## E-step
![](img/elbo_estep.png)

## M-step
![](img/elbo_mstep.png)

## Minorize–maximize steps

![](img/mm_picture.png)

## Inequalities proving monotonicity

![](img/eq_em_monotone.png)

<!-- ## The E-step, as an expectation

![](img/eq_q_function.png) -->

## Closed form derivation

![](img/eq_mstep_derivation.png)

## Where it stops

![](img/em_convergence.png)

# Expectation-Maximization variations

## Algorithm variations

![](img/hard_em.png)

## k-means is a limit case of EM

![](img/eq_kmeans_limit.png)

## k-means vs Gaussian mixture

![](img/kmeans_vs_gmm.png)

## Stochastic EM

![](img/sem_algorithm.png)

## SEM example

![](img/sem_run.png)

## N draws per point
![](img/nsem_idea.png)

## k-means vs EM vs SEM vs N-SEM
![](img/em_variants.png)

# Reach convergence

## Where you start matters

![](img/init_strategies.png)

## Starts comparison

![](img/init_compare.png)

## Guarding against collapse

![](img/reg_covar.png)

## Covariance types

![](img/covariance_choice.png)

## AIC and BIC

![](img/aic_bic.png)

## Number of components

![](img/choosing_k.png)

## Example on real data

![](img/gmm_iris.png)

## Scoring a new point

![](img/gmm_anomaly.png)

## Beyond the Gaussian

![](img/beyond_gaussian.png)

## Conclusion

![](img/gmm_props.png)
