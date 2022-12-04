# -*- coding: utf-8 -*-
"""
Created on Wed Nov 30 21:36:12 2022

@author: luis.barreiro
"""

#%%
# Common imports
from IPython.display import Image 
#from pydot import graph_from_dot_data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import export_graphviz
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.datasets import load_breast_cancer
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_validate
import scikitplot as skplt
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split as splitter
from sklearn.model_selection import KFold, cross_validate
import os
from sklearn.metrics import f1_score, recall_score, precision_recall_fscore_support

os.chdir("C:/Users/luis.barreiro/Documents/GitHub/Projects_STK4155/Project3")
cwd = os.getcwd()
print(cwd)

#%%
np.random.seed(3)        #create same seed for random number every time

trees=pd.read_csv("input_data\input_trees_v02.csv")     #Load tree data

trees.columns

x=trees[['min', 'max', 'avg', 'std', 'ske', 'kur', 'p05', 'p25','p50', 'p75', 'p90', 'c00', 'int_min', 'int_max', 'int_avg', 'int_std','int_ske', 'int_kur', 'int_p05', 'int_p25', 'int_p50', 'int_p75','int_p90']]
y=trees['CON_DEC']
y2=trees['Specie']

#x_train,x_test,y_train,y_test=splitter(x,y,test_size=0.3)   #Split datasets into training and testing: not needed when we use CV

#Scale the data
scaler = StandardScaler()
scaler.fit(x)
# x_train_scaled = scaler.transform(x_train)
# x_test_scaled = scaler.transform(x_test)
x_scaled = scaler.transform(x)

#%%
n_splits=10
kf = KFold(n_splits)

#define methods

# Neural Network with 4 hidden layers, eta=1.e-5, lmbd=10
dnn = MLPClassifier(hidden_layer_sizes=4, activation='relu', solver ='lbfgs',alpha=10, learning_rate_init=1.e-5, max_iter=1000)
score_kf_NN = np.zeros(n_splits)
j=0
for train_indices, test_indices in kf.split(x_scaled):
    dnn.fit(x_scaled[train_indices], y[train_indices])
    score_kf_NN[j]=dnn.score(x_scaled[test_indices], y[test_indices])
    j+=1
print("Test set accuracy Neural Network with scaled data: {:.2f}".format(np.mean(score_kf_NN)))

# Logistic Regression
logreg = LogisticRegression(solver='lbfgs')
score_kf_logreg = np.zeros(n_splits)
j=0
for train_indices, test_indices in kf.split(x_scaled):
    logreg.fit(x_scaled[train_indices], y[train_indices])
    score_kf_logreg[j]=logreg.score(x_scaled[test_indices], y[test_indices])
    j+=1
print("Test set accuracy Logistic Regression with scaled data: {:.2f}".format(np.mean(score_kf_logreg)))

# Decision Trees
deep_tree_clf = DecisionTreeClassifier(max_depth=None)
score_kf_deep_tree_clf = np.zeros(n_splits)
j=0
for train_indices, test_indices in kf.split(x_scaled):
    deep_tree_clf.fit(x_scaled[train_indices], y[train_indices])
    score_kf_deep_tree_clf[j]=deep_tree_clf.score(x_scaled[test_indices], y[test_indices])
    j+=1
print("Test set accuracy Decision Trees with scaled data: {:.2f}".format(np.mean(score_kf_deep_tree_clf)))
 
# Support Vector Machine
svm = SVC(gamma='auto', C=100)
score_kf_svm = np.zeros(n_splits)
j=0
for train_indices, test_indices in kf.split(x_scaled):
    svm.fit(x_scaled[train_indices], y[train_indices])
    score_kf_svm[j]=svm.score(x_scaled[test_indices], y[test_indices])
    j+=1
print("Test set accuracy SVM with scaled data: {:.2f}".format(np.mean(score_kf_svm)))

# Random forests
#Instantiate the model with 100 trees and entropy as splitting criteria
Random_Forest_model = RandomForestClassifier(n_estimators=100,criterion="gini")
score_kf_RF = np.zeros(n_splits)
j=0
for train_indices, test_indices in kf.split(x_scaled):
    Random_Forest_model.fit(x_scaled[train_indices], y[train_indices])
    score_kf_RF[j]=Random_Forest_model.score(x_scaled[test_indices], y[test_indices])
    j+=1
print("Test set accuracy Random Forest with scaled data: {:.2f}".format(np.mean(score_kf_RF)))


#%%
x_train,x_test,y_train,y_test=splitter(x,y,test_size=0.3)   #Split datasets into training and testing: not needed when we use CV

#Scale the data
scaler = StandardScaler()
scaler.fit(x_train)
x_train_scaled = scaler.transform(x_train)
x_test_scaled = scaler.transform(x_test)
x_scaled = scaler.transform(x)

#Confusion matrix with Neural Network
dnn.fit(x_train_scaled, y_train)
y_pred = dnn.predict(x_test_scaled)
skplt.metrics.plot_confusion_matrix(y_test, y_pred, normalize=True)
plt.show()
# y_probas = dnn.predict_proba(x_test_scaled)
# skplt.metrics.plot_roc(y_test, y_probas)
# plt.show()
# skplt.metrics.plot_cumulative_gain(y_test, y_probas)
# plt.show()

#Confusion matrix with Random Forest
Random_Forest_model.fit(x_train_scaled, y_train)
y_pred1 = Random_Forest_model.predict(x_test_scaled)
skplt.metrics.plot_confusion_matrix(y_test, y_pred1, normalize=True)
plt.show()
# y_probas1 = Random_Forest_model.predict_proba(x_test_scaled)
# skplt.metrics.plot_roc(y_test, y_probas1)
# plt.show()
# skplt.metrics.plot_cumulative_gain(y_test, y_probas1)
# plt.show()

#Confusion matrix with SVM
svm.fit(x_train_scaled, y_train)
y_pred2 = svm.predict(x_test_scaled)
skplt.metrics.plot_confusion_matrix(y_test, y_pred2, normalize=True)
plt.show()
# y_probas2 = svm.predict_proba(x_test_scaled)
# skplt.metrics.plot_roc(y_test, y_probas2)
# plt.show()
# skplt.metrics.plot_cumulative_gain(y_test, y_probas2)
# plt.show()


#Confusion matrix with Logistic
logreg.fit(x_train_scaled, y_train)
y_pred3 = logreg.predict(x_test_scaled)
skplt.metrics.plot_confusion_matrix(y_test, y_pred3, normalize=True)
plt.show()
# y_probas3 = logreg.predict_proba(x_test_scaled)
# skplt.metrics.plot_roc(y_test, y_probas3)
# plt.show()
# skplt.metrics.plot_cumulative_gain(y_test, y_probas3)
# plt.show()


#Confusion matrix with Decision tree
deep_tree_clf.fit(x_train_scaled, y_train)
y_pred4 = logreg.predict(x_test_scaled)
skplt.metrics.plot_confusion_matrix(y_test, y_pred4, normalize=True)
plt.show()
# y_probas3 = logreg.predict_proba(x_test_scaled)
# skplt.metrics.plot_roc(y_test, y_probas3)
# plt.show()
# skplt.metrics.plot_cumulative_gain(y_test, y_probas3)
# plt.show()



#%%
#Accuracy, recall, precision, F1
print("Precision, recall, F1 score for NN (coniferous, deciduous):",precision_recall_fscore_support(y_test, y_pred))
print("Precision, recall, F1 score for RF (coniferous, deciduous):",precision_recall_fscore_support(y_test, y_pred1))
print("Precision, recall, F1 score for SVM (coniferous, deciduous):",precision_recall_fscore_support(y_test, y_pred2))
print("Precision, recall, F1 score for logreg (coniferous, deciduous):",precision_recall_fscore_support(y_test, y_pred3))
print("Precision, recall, F1 score for decision tree (coniferous, deciduous):",precision_recall_fscore_support(y_test, y_pred4))

#%%
from sklearn.tree import plot_tree

plt.figure(figsize=(150, 100))
plot_tree(Random_Forest_model.estimators_[0], 
          feature_names=['min', 'max', 'avg', 'std', 'ske', 'kur', 'p05', 'p25','p50', 'p75', 'p90', 'c00', 'int_min', 'int_max', 'int_avg', 'int_std','int_ske', 'int_kur', 'int_p05', 'int_p25', 'int_p50', 'int_p75','int_p90'],
          class_names=['Conifers', 'Deciduous'], 
          filled=True, impurity=True, 
          rounded=True)
plt.savefig(f"Results/RF_diagram.png", dpi=150)




