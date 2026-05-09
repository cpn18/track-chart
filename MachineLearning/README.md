Review of investigation (Sprint 1: 09/22/25 - 10/12/25)

Faux_Data_Generator
 - Converts Json data into csv so it is easier for processing.

ML_Model
 - Implementations of all models. Options are:
    * K nearest neighbors
    * Support vector machine
    * Logistic regression
    * Multilayer perceptron
    * Decision tree classifier

ML_Runner
 - Test runner. Tests all models.

Visualize_Data
 - Methods for plotting recorded data. Options for single or double axis.
 - Correlation matrix with heatmap

 File_Reader
 - Methods for parsing data formats that may be created by the PiRail unit

K_Means_Testing
- Experiments with k means clustering, looking for trends between known POIs and other data

POI_detection
- Visualizing the points identified as POIs by the linear regression model(s)

Real_Time_Model_Simulator
- Very similar to POI_detection, but running the model on each entry iteratively to ensure it runs fast enough to function on a constant data stream

Regression_Analysis
- Using OLS to create and evaluate prediction models

Test_Segment_Isolation
- Creating individual files for experiments run on 10.12.2025 
