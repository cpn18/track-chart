"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""
from MachineLearning import Faux_Data_Generator, ML_Model


def main():
    models = ["KNN", "SVM", "LR", "MLP", "DTC"]
    #Visualize_Data.graph_correlation_axis("wolfeboro20201107.json", "acc_z", "yaw")
    #Visualize_Data.create_graph_for_select_axis("wolfeboro20201107.json", "acc_z")
    Faux_Data_Generator.create_faux_data_for_test_train_from_json("wolfeboro20201107.json", "training.csv", 100) #if fail, rerun
    Faux_Data_Generator.create_faux_data_for_test_train_from_json("wolfeboro20201107.json", "test.csv", 100) #TODO adjust parameters within function to work with any data
    #Visualize_Data.visualize_generated_data()
    for m in models:
        #TODO once proper training data is achieved, adjust hyperparameters within models
        ML_Model.classify_train_test(m) #training and testing
        #ML_Model.classify_data() #training and prediciton


if __name__ == '__main__':
    main()
