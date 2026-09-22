---
title: |
  Session 1\
  Introduction and Reminders on Machine Learning
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 1 — Lecture
---

# Practical information

## This course, in one slide

![](img/about.png)

## What you are expected to know already

![](img/prerequisites.png)

## Grading

100% of your grade will be based on the final project report.

The goal is for you to pick up some topic of your interest, with public data available.
Produce an analysis using one or more technique(s) introduced during this course.
You will write your findings in a report of ~5 pages.

## Reading material

- G. James, D. Witten, T. Hastie, R. Tibshirani — *An Introduction to Statistical Learning* (2013)
- T. Hastie, R. Tibshirani, J. Friedman — *The Elements of Statistical Learning* (2009)
- C. M. Bishop — *Pattern Recognition and Machine Learning* (2006)

Slides, labs, data and announcements live on Edunao.\
The slides are not comprehensive.

## Where it is used

![](img/applications.png)

# Reminders on parameter estimation

## Learning is estimating parameters

![](img/estimation_setup.png)

## How close, on average?

![](img/bias.png)

## How stable?

![](img/variance.png)

## Bias and variance are independent problems

![](img/dartboard.png)

## One number for both bias & var

![](img/eq_mse.png)

## Three ways to find a good estimator

![](img/three_methods.png)

## Method of moments: match what you can compute

![](img/mom_idea.png)

## Method of moments: the Gaussian case

![](img/mom_gaussian.png)

## What the method of moments is worth

![](img/mom_props.png)

## What is likelihood?

![](img/eq_likelihood.png)

## Likelihood on data

![](img/likelihood_build.png)

## Maximum likelihood on data

![](img/mle_idea.png)

## Why taking the log

![](img/log_likelihood.png)

## Maximum likelihood: the Gaussian case

![](img/mle_gaussian.png)

## What maximum likelihood is worth

![](img/mle_props.png)

## When parameters follow a random distribution

![](img/bayes_setup.png)

## The posterior

![](img/eq_posterior.png)

## What  is a "cost"?

![](img/cost_idea.png)

## Three costs, three estimators

![](img/cost_zoo.png)

## How much the prior matters

![](img/prior_effect.png)

## Three divisors

![](img/divisor_family.png)

## Unbiased is not the same as best

![](img/estimators_compare.png)

## Where n comes from: the likelihood

![](img/mle_variance.png)

## Where n − 1 comes from: a lost degree of freedom

![](img/bessel.png)

## Where n + 1 comes from: the smallest MSE

![](img/mse_divisor.png)

# Supervised learning

## The setting

![](img/supervised_principle.png)

## Regression or classification

![](img/regression_vs_classification.png)

## Examples

![](img/supervised_apps.png)

## Two ways to build a classifier

![](img/discriminative_vs_generative.png)

## Bayes classifier as a MAP rule

![](img/eq_bayes_classifier.png)

## Bayes classifier

![](img/bayes_ingredients.png)

## Naive Bayes: assume the features are independent

![](img/eq_naive_bayes.png)

## Naive Bayes: spam filtering

![](img/spam_filter.png)

## Naive Bayes: the zero distribution problem

![](img/laplace_smoothing.png)

## Naive Bayes on continuous features

![](img/naive_bayes_gaussian.png)

## Linear discriminant analysis

![](img/lda_setup.png)

## LDA, step by step

![](img/lda_fit_steps.png)

## LDA: computing the rule

![](img/lda_derivation.png)

## LDA: a linear decision boundary

![](img/lda_boundary.png)

## LDA: why the boundary is straight

![](img/lda_why_linear.png)

## LDA: values estimated from the training set

![](img/lda_training.png)

## QDA: one covariance per class

![](img/qda_vs_lda.png)

## QDA shapes

![](img/qda_shapes.png)

## LDA vs QDA: costs & benefits

![](img/lda_qda_cost.png)

# Unsupervised learning

## The setting

![](img/unsupervised_principle.png)

## Two families

![](img/dimred_vs_clustering.png)

## What that looks like in practice

![](img/unsupervised_apps.png)

## k-means goal

![](img/eq_kmeans.png)

## k-means algorithm

![](img/kmeans_algorithm.png)

## k-means limitations

![](img/kmeans_weaknesses.png)

## PCA: directions of maximum variance

![](img/pca_projection.png)

## PCA: how much can be dropped

![](img/pca_spectrum.png)

## Conclusion

![](img/concept_map.png)
