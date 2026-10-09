---
title: |
  Session 4\
  Clustering
subtitle: |
  Advanced Machine Learning · MSc DSBA · 2026\
  \
  Paul Dubois
date: Week 4 — Lecture
---

# What is clustering?

## No labels

![](img/clustering_setting.png)

## Two ways to simplify a table

![](img/clustering_vs_dimred.png)

## Use cases

![](img/clustering_apps.png)

## What a cluster can mean

![](img/cluster_types.png)

## Partitional or hierarchical

![](img/partitional_vs_hierarchical.png)

## Exclusive or overlapping

![](img/exclusive_vs_overlapping.png)

## Hard or fuzzy

![](img/hard_vs_fuzzy.png)

## Complete or partial

![](img/complete_vs_partial.png)

## Homogeneous or heterogeneous

![](img/homogeneous_vs_heterogeneous.png)

## Choice of algorithm assumes

![](img/cluster_distinctions.png)

## Distance and dissimilarity

![](img/eq_dissimilarity.png)

## Distances examples

![](img/distance_zoo.png)

## Hamming: a distance for categories

![](img/hamming_distance.png)

## Distances between groups

![](img/linkage_definitions.png)

# Clustering quality

## Within and between

![](img/eq_inertia.png)

## What a good clustering looks like

![](img/good_clustering.png)

# K-means

## The objective

![](img/eq_kmeans.png)

## Lloyd's algorithm

![](img/kmeans_algorithm.png)

## Inertia

![](img/inertia_defined.png)

## Random results

![](img/kmeans_init.png)

## k-means fails with

![](img/kmeans_limits.png)

## Variants

![](img/kmeans_alternatives.png)

# Mountain and subtractive clustering

## Clusters as peaks of a landscape

![](img/mountain_idea.png)

## Mountain function

![](img/eq_mountain.png)

## Take a peak, flatten it, repeat

![](img/mountain_steps.png)

## Dropping the grid

![](img/subtractive_clustering.png)

## Pros and cons

![](img/mountain_props.png)

# Hierarchical clustering

## Representing clusters inside clusters
![](img/hierarchy_idea.png)

## Agglomerative, one merge at a time
![](img/agglomerative_steps.png)

## Cutting the dendrogram

![](img/dendrogram_cut.png)

## Ward: the cost of a merge

![](img/ward_idea.png)

## Moving the reference point

![](img/eq_huygens.png)

## Where the Ward formula comes from

![](img/eq_ward_proof.png)

## Ward distance

![](img/eq_ward.png)

## Every merge changes every distance

![](img/linkage_update.png)

## WPGMA: Weighted Pair Group Method with Arithmetic mean

![](img/wpgma.png)

## Unweighted Pair Group Method with Arithmetic mean

![](img/wpgma_vs_upgma.png)

## Four linkages
![](img/linkage_compare.png)

## Four linkages

![](img/linkage_dendrograms.png)

## Which linkage to use

![](img/linkage_props.png)

## Tree

![](img/hierarchical_props.png)

# DBSCAN

## Neighborhood and crowdedness

![](img/dbscan_idea.png)

## Core, border, noise

![](img/dbscan_points.png)

## Algorithm

![](img/dbscan_algorithm.png)

## Effect of ε

![](img/dbscan_epsilon.png)

## Reading ε off the k-NN curve

![](img/dbscan_knn_elbow.png)

## Effect of MinPts

![](img/dbscan_minpts.png)

## Shapes k-means cannot reach

![](img/dbscan_vs_kmeans.png)

## DBSCAN

![](img/dbscan_props.png)

# HDBSCAN

## DBSCAN at every scale at once

![](img/hdbscan_idea.png)

## Six steps

![](img/hdbscan_steps.png)

## Step 1: measure the density

![](img/core_distance.png)

## Step 2: transform the space

![](img/eq_mutual_reachability.png)

## Step 2: a worked example

![](img/mreach_example.png)

## Step 2: why the maximum

![](img/mreach_intuition.png)

## What the new distance does

![](img/mreach_effect.png)

## Step 3: the minimum spanning tree

![](img/mst_step.png)

## Step 3: how the tree is built

![](img/mst_build.png)

## Step 4: cluster hierarchy

![](img/mst_to_hierarchy.png)

## Step 4 on real data

![](img/hdbscan_hierarchy.png)

## Step 5: condense the tree

![](img/condense_example.png)

## Step 5 on real data
![](img/condensed_tree.png)

## Stability
![](img/stability_idea.png)

## Stability example

![](img/stability_example.png)

## Step 6: keep the stable clusters

![](img/extract_example.png)

## Six steps

![](img/hdbscan_steps.png)

## Dataset with multiple densities

![](img/hdbscan_result.png)

## HDBSCAN

![](img/hdbscan_props.png)

## Four methods on four datasets
![](img/algo_compare.png)

## The map
![](img/clustering_map.png)
