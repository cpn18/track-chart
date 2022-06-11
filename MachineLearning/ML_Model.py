"""
UNH Capstone 2022 Project

Ben Grimes, Jeff Fernandes, Max Hennessey, Liqi Li
"""
import pandas as panda
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
import matplotlib.pyplot as plt
from sklearn import metrics


def classify_train_test(model):
    # import test and training data
    df_train = panda.read_csv("training.csv")
    df_test = panda.read_csv("test.csv")

    x_train_pn = df_train[['acc_y', 'acc_x', 'pitch', 'roll',
                           'yaw']].values  # features #INCLUDE 'acc_z' when not using dummy data and actuial training data
    x_test_pn = df_test[['acc_y', 'acc_x', 'pitch', 'roll',
                         'yaw']].values  # features #INCLUDE 'acc_z' when not using dummy data and actuial training data
    y_train = df_train['damaged'].astype(int).values  # response
    y_test = df_test['damaged'].astype(int).values  # response

    # Normalize Data
    norm = MinMaxScaler().fit(x_train_pn)
    x_train = norm.transform(x_train_pn)
    x_test = norm.transform(x_test_pn)

    classifier_model = None

    if model == "KNN":
        classifier_model = KNeighborsClassifier(n_neighbors=1)
    elif model == "SVM":
        classifier_model = svm.SVC(probability=True)
    elif model == "LR":
        classifier_model = LogisticRegression()
    elif model == "MLP":
        classifier_model = MLPClassifier(max_iter=400)
    elif model == "DTC":
        classifier_model = DecisionTreeClassifier()
    elif model is None:
        classifier_model = KNeighborsClassifier(n_neighbors=1)

    classifier_model.fit(x_train, y_train)
    y_pred = classifier_model.predict(x_test)
    y_scores = classifier_model.predict_proba(x_test)
    fpr, tpr, thresh = metrics.roc_curve(y_test, y_scores[:, 1])
    print(model + "results: ")
    print("Accuracy: " + metrics.accuracy_score(y_test, y_pred).__str__())
    print("Area Under ROC Curve: " + metrics.auc(fpr, tpr).__str__())


def classify_data(model):
    # import test and training data
    df_train = panda.read_csv("training.csv")
    df_test = panda.read_csv("test.csv")  # data we are predicting

    x_train_pn = df_train[['acc_y', 'acc_x', 'pitch', 'roll',
                           'yaw']].values  # features #INCLUDE 'acc_z' when not using dummy data and actuial training data
    x_test_pn = df_test[['acc_y', 'acc_x', 'pitch', 'roll',
                         'yaw']].values  # features #INCLUDE 'acc_z' when not using dummy data and actuial training data
    y_train = df_train['damaged'].astype(int).values  # response

    # Normalize Data
    norm = MinMaxScaler().fit(x_train_pn)
    x_train = norm.transform(x_train_pn)
    x_test = norm.transform(x_test_pn)

    classifier_model = None

    if model == "KNN":
        classifier_model = KNeighborsClassifier(n_neighbors=1)
    elif model == "SVM":
        classifier_model = svm.SVC(probability=True)
    elif model == "LR":
        classifier_model = LogisticRegression()
    elif model == "MLP":
        classifier_model = MLPClassifier(max_iter=400)
    elif model == "DTC":
        classifier_model = DecisionTreeClassifier()

    classifier_model.fit(x_train, y_train)
    y_pred = classifier_model.predict(x_test)
    plt.scatter()
    plt.show(x_test, y_pred)
