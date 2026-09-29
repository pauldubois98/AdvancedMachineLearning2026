# Datasets Suggestions
Students must submit an individual project report.
The report should be ~5 pages long on the topic of their choice.
The project must involve at least one of the techniques seen during this course.
Here are some suggestions for datasets;
Feel free to use another one of your choice.

1. **Stars CYG OB1**
    * **Size:** 47 observations, 2 variables
    * **Short description:** Classic robust regression benchmark from astronomy.
    * **Long description:** Log surface temperature versus log light intensity for 47 stars in the Cygnus constellation (Hertzsprung Russell diagram), popularised by Rousseeuw and Leroy.
    * **Data types:** Continuous numerical
    * **File format:** CSV (via Rdatasets)
    * **Link:** https://vincentarelbundock.github.io/Rdatasets/ (search "starsCYG")

2. **Ames Housing**
    * **Size:** 2,930 sales, 80 explanatory variables
    * **Short description:** House sale prices in Ames, Iowa (2006 to 2010).
    * **Long description:** Compiled by Dean De Cock (Journal of Statistics Education, 2011) as a modern replacement for Boston Housing.
    * **Data types:** Mixed (continuous, discrete, ordinal, nominal)
    * **File format:** Tab separated text
    * **Link:** http://jse.amstat.org/v19n3/decock/AmesHousing.txt (documentation: http://jse.amstat.org/v19n3/decock/DataDocumentation.txt)

3. **DVF, Demandes de Valeurs Foncières**
    * **Size:** Several million transactions per year, about 40 columns, 5 most recent years
    * **Short description:** All French real estate transactions published by the DGFiP.
    * **Long description:** Official open data on property sales in France (excluding Alsace, Moselle and Mayotte), with price, surface, number of rooms, property type and location.
    * **Data types:** Mixed (numerical, categorical, dates, addresses, coordinates in the geolocated version)
    * **File format:** Pipe delimited text (raw), CSV (geolocated version)
    * **Link:** https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/

4. **Breast Cancer Wisconsin (Diagnostic)**
    * **Size:** 569 samples, 30 features, 2 classes (212 malignant, 357 benign)
    * **Short description:** Tumour diagnosis from cell nucleus measurements.
    * **Long description:** Features are computed from digitised images of fine needle aspirates (radius, texture, concavity..., each as mean, standard error and worst value).
    * **Data types:** Continuous numerical, binary label
    * **File format:** CSV (.data), also built into scikit-learn
    * **Link:** https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic

5. **Adult (Census Income)**
    * **Size:** 48,842 individuals, 14 features
    * **Short description:** Predict whether income exceeds 50K USD per year.
    * **Long description:** Extracted from the 1994 US census. Mixes numerical and categorical features, contains missing values and a moderate class imbalance (about 24% positives).
    * **Data types:** Mixed (continuous, categorical), binary label
    * **File format:** CSV (.data / .test)
    * **Link:** https://archive.ics.uci.edu/dataset/2/adult

6. **Credit Card Fraud Detection (ULB)**
    * **Size:** 284,807 transactions, 30 features, 492 frauds (about 0.17%)
    * **Short description:** Detect fraudulent card transactions made by European cardholders.
    * **Long description:** Transactions over two days in 2013. For confidentiality, 28 features are PCA components (V1 to V28), only Time and Amount are raw.
    * **Data types:** Continuous numerical, binary label
    * **File format:** CSV (about 150 MB)
    * **Link:** https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud (free Kaggle account required)

7. **Spambase**
    * **Size:** 4,601 emails, 57 features, 2 classes (about 39% spam)
    * **Short description:** Spam versus legitimate email classification.
    * **Long description:** Features are word and character frequencies plus statistics on capital letter runs.
    * **Data types:** Continuous numerical, binary label
    * **File format:** CSV (.data)
    * **Link:** https://archive.ics.uci.edu/dataset/94/spambase

8. **USGS Earthquake Catalogue**
    * **Size:** Configurable (from a few thousand to hundreds of thousands of events depending on magnitude, period and region)
    * **Short description:** Worldwide earthquake events with location, depth and magnitude.
    * **Long description:** The search interface lets students choose a time window, a region and a minimum magnitude.
    * **Data types:** Numerical (coordinates, depth, magnitude), timestamps, categorical
    * **File format:** CSV, GeoJSON, KML, QuakeML
    * **Link:** https://earthquake.usgs.gov/earthquakes/search/

9. **Vélib' Métropole station availability**
    * **Size:** About 1,400 stations, snapshots every minute
    * **Short description:** Real time availability of bikes and docks in Paris shared bike stations.
    * **Long description:** The network has nearly 1,400 stations spread over 55 municipalities in the Paris metropolitan area, and the feed gives mechanical bikes, electric bikes and free docks per station.
    * **Data types:** Numerical counts, coordinates, timestamps, categorical
    * **File format:** JSON (API, GBFS standard), CSV export
    * **Link:** https://opendata.paris.fr/explore/dataset/velib-disponibilite-en-temps-reel/ (history: https://github.com/lovasoa/historique-velib-opendata)

10. **Online Retail II**
    * **Size:** About 1,067,000 invoice lines, 8 columns
    * **Short description:** Transactions of a UK online gift retailer (2009 to 2011).
    * **Long description:** Each line is a product in an invoice, with quantity, unit price, customer ID and country.
    * **Data types:** Mixed (numerical, categorical, dates, text descriptions)
    * **File format:** XLSX
    * **Link:** https://archive.ics.uci.edu/dataset/502/online+retail+ii

11. **Wholesale Customers**
    * **Size:** 440 clients, 8 variables
    * **Short description:** Annual spending of clients of a Portuguese wholesale distributor.
    * **Long description:** Six product categories (fresh, milk, grocery, frozen, detergents, delicatessen) plus channel (hotel/restaurant/café versus retail) and region.
    * **Data types:** Continuous numerical, categorical
    * **File format:** CSV
    * **Link:** https://archive.ics.uci.edu/dataset/292/wholesale+customers

12. **20 Newsgroups**
    * **Size:** About 18,800 documents, 20 categories
    * **Short description:** Posts from 20 Usenet discussion groups.
    * **Long description:** A standard text corpus covering computers, sport, religion, politics, science...
    * **Data types:** Text, categorical label
    * **File format:** tar.gz of plain text files, also built into scikit-learn
    * **Link:** http://qwone.com/~jason/20Newsgroups/

13. **Olivetti Faces (AT&T)**
    * **Size:** 400 images, 40 people, 10 images each (64×64 in the scikit-learn version)
    * **Short description:** Grey level face images under varying expression and lighting.
    * **Data types:** Images (grey level pixel intensities), identity label
    * **File format:** PGM images (original), NumPy arrays via scikit-learn
    * **Link:** https://cam-orl.co.uk/facedatabase.html, or `sklearn.datasets.fetch_olivetti_faces`

14. **MovieLens 100K**
    * **Size:** 100,000 ratings, 943 users, 1,682 movies
    * **Short description:** Movie ratings (1 to 5) from the MovieLens recommender site.
    * **Data types:** Integer ratings, timestamps, categorical metadata
    * **File format:** ZIP of tab or pipe separated text files
    * **Link:** https://grouplens.org/datasets/movielens/100k/

15. **Galaxies (Roeder, 1990)**
    * **Size:** 82 observations, 1 variable
    * **Short description:** Velocities of galaxies in the Corona Borealis region.
    * **Data types:** Continuous numerical
    * **File format:** CSV (via Rdatasets)
    * **Link:** https://vincentarelbundock.github.io/Rdatasets/ (search "galaxies"), original package at https://cran.r-project.org/package=MASS

16. **Palmer Penguins**
    * **Size:** 344 penguins, 8 variables
    * **Short description:** Morphological measurements of three penguin species in Antarctica.
    * **Data types:** Continuous numerical, categorical
    * **File format:** CSV
    * **Link:** https://github.com/allisonhorst/palmerpenguins

17. **Berkeley Segmentation Dataset (BSDS500)**
    * **Size:** 500 natural images with several human segmentations each
    * **Short description:** Benchmark for image segmentation.
    * **Data types:** Images (RGB pixels), segmentation maps
    * **File format:** JPG images, MATLAB .mat ground truth
    * **Link:** https://www2.eecs.berkeley.edu/Research/Projects/CS/vision/grouping/resources.html

18. **Fashion MNIST**
    * **Size:** 70,000 images (60,000 train, 10,000 test), 28×28 pixels, 10 classes
    * **Short description:** Grey level images of clothing items from Zalando.
    * **Long description:** A in replacement for MNIST that is harder and less saturated.
    * **Data types:** Images (pixel intensities 0 to 255), class label
    * **File format:** gzip IDX binary, also on OpenML
    * **Link:** https://github.com/zalandoresearch/fashion-mnist

19. **PBMC 3k (single cell RNA sequencing)**
    * **Size:** About 2,700 cells, about 32,700 genes
    * **Short description:** Gene expression of peripheral blood mononuclear cells from a healthy donor (10x Genomics).
    * **Data types:** Integer counts (sparse matrix), gene and cell identifiers
    * **File format:** tar.gz containing Matrix Market (matrix.mtx) plus TSV files, or directly via `scanpy.datasets.pbmc3k()`
    * **Link:** https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz

20. **Human Activity Recognition Using Smartphones**
    * **Size:** 10,299 samples, 561 features, 6 activities, 30 subjects
    * **Short description:** Activity recognition from smartphone accelerometer and gyroscope signals.
    * **Long description:** Activities are walking, walking upstairs, walking downstairs, sitting, standing and lying.
    * **Data types:** Continuous numerical, raw time series, class and subject labels
    * **File format:** ZIP of space separated text files
    * **Link:** https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones

21. **COIL 20**
    * **Size:** 1,440 images, 20 objects, 72 poses each, 128×128 pixels
    * **Short description:** Grey level images of objects rotated on a turntable.
    * **Data types:** Images (pixel intensities), object and pose labels
    * **File format:** PNG images
    * **Link:** https://www.cs.columbia.edu/CAVE/software/softlib/coil-20.php
