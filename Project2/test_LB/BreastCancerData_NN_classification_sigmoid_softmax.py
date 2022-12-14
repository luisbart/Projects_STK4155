#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 14:42:21 2022

@author: rpcorser
"""
import numpy as np
import matplotlib.pyplot as plt
from  matplotlib.colors import LogNorm
import seaborn as sns
from sklearn.model_selection import train_test_split as splitter
from sklearn.metrics import accuracy_score
from sklearn.datasets import load_breast_cancer
import pickle
import os 
from Functions import Beta_std, FrankeFunction, R2, MSE, DesignMatrix, LinReg
from NeuralNetwork_classification_sigmoid_softmax import NeuralNetwork, leakyrelu, leakyrelu_grad, sigmoid, softmax_stable , accuracy_score_numpy
from sklearn.neural_network import MLPRegressor, MLPClassifier
#%%
from tensorflow.keras.layers import Input
from tensorflow.keras.models import Sequential      #This allows appending layers to existing models
from tensorflow.keras.layers import Dense           #This allows defining the characteristics of a particular layer
from tensorflow.keras import optimizers             #This allows using whichever optimiser we want (sgd,adam,RMSprop)
from tensorflow.keras import regularizers           #This allows using whichever regularizer we want (l1,l2,l1_l2)
from tensorflow.keras.utils import to_categorical   #This allows using categorical cross entropy as the cost function

from tensorflow.keras import layers
from tensorflow.keras import activations
from tensorflow.keras.layers import LeakyReLU

def create_neural_network_keras(n_neurons_layer1, n_categories, eta, lmbd):
    model = Sequential()
    model.add(Dense(n_neurons_layer1, activation='sigmoid', kernel_regularizer=regularizers.l2(lmbd)))
    model.add(Dense(n_categories, activation='softmax'))
    
    sgd = optimizers.SGD(lr=eta)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    
    return model

#%%

np.random.seed(0)        #create same seed for random number every time

cancer=load_breast_cancer()      #Download breast cancer dataset

inputs=cancer.data                     #Feature matrix of 569 rows (samples) and 30 columns (parameters)
outputs=cancer.target                  #Label array of 569 rows (0 for benign and 1 for malignant)
labels=cancer.feature_names[0:30]

print('The content of the breast cancer dataset is:')      #Print information about the datasets
print(labels)
print('-------------------------')
print("inputs =  " + str(inputs.shape))
print("outputs =  " + str(outputs.shape))
print("labels =  "+ str(labels.shape))

x=inputs      #Reassign the Feature and Label matrices to other variables
y=outputs


#%%
# Visualisation of dataset (for correlation analysis)

plt.figure()
plt.scatter(x[:,0],x[:,2],s=40,c=y,cmap=plt.cm.Spectral)
plt.xlabel('Mean radius',fontweight='bold')
plt.ylabel('Mean perimeter',fontweight='bold')
plt.show()

plt.figure()
plt.scatter(x[:,5],x[:,6],s=40,c=y, cmap=plt.cm.Spectral)
plt.xlabel('Mean compactness',fontweight='bold')
plt.ylabel('Mean concavity',fontweight='bold')
plt.show()


plt.figure()
plt.scatter(x[:,0],x[:,1],s=40,c=y,cmap=plt.cm.Spectral)
plt.xlabel('Mean radius',fontweight='bold')
plt.ylabel('Mean texture',fontweight='bold')
plt.show()

plt.figure()
plt.scatter(x[:,2],x[:,1],s=40,c=y,cmap=plt.cm.Spectral)
plt.xlabel('Mean perimeter',fontweight='bold')
plt.ylabel('Mean compactness',fontweight='bold')
plt.show()

#%%
# Generate training and testing datasets

#Select features relevant to classification (texture,perimeter,compactness and symmetery) 
#and add to input matrix

#temp1=np.reshape(x[:,1],(len(x[:,1]),1))
temp1=np.reshape((x[:,1]-np.mean(x[:,1]))/np.std(x[:,1]),(len(x[:,1]),1))

#temp2=np.reshape(x[:,2],(len(x[:,2]),1))
temp2=np.reshape((x[:,2]-np.mean(x[:,2]))/np.std(x[:,2]),(len(x[:,2]),1))

X=np.hstack((temp1,temp2))      
#temp=np.reshape(x[:,5],(len(x[:,5]),1))
temp=np.reshape((x[:,5]-np.mean(x[:,5]))/np.std(x[:,5]),(len(x[:,5]),1))

X=np.hstack((X,temp))       
#temp=np.reshape(x[:,8],(len(x[:,8]),1))
temp=np.reshape((x[:,8]-np.mean(x[:,8]))/np.std(x[:,8]),(len(x[:,8]),1))
X=np.hstack((X,temp))       

x_train,x_test,z_train,z_test=splitter(X,y,test_size=0.8)   #Split datasets into training and testing

#z_train_onehot=to_categorical_numpy(z_train)     #Convert labels to categorical when using categorical cross entropy
#z_test_onehot=to_categorical_numpy(z_test)

del temp1,temp2,temp

M = 100   #size of each minibatch
m = int(z_train.shape[0]/M) #number of minibatches
epochs = 1000 #number of epochs 

etas = np.logspace(-4, -1, 4)
lambdas = np.logspace(-5, 2, 8)
n_hidden_neurons = [4]
n_hidden_neurons_v02 = 4
n_categories = 1
n_features = x_train.shape[1]
n_inputs = x_train.shape[0]

#Initialize error to store
NN_err_train=np.zeros(shape=(lambdas.shape[0],etas.shape[0]))
NN_err_test=np.zeros(shape=(lambdas.shape[0],etas.shape[0]))
DNN_scikit_train = np.zeros(shape=(lambdas.shape[0],etas.shape[0]))
DNN_scikit_test = np.zeros(shape=(lambdas.shape[0],etas.shape[0]))

DNN_keras_train = np.zeros((len(lambdas), len(etas)))
DNN_keras_test = np.zeros((len(lambdas), len(etas)))
#

z_train = np.reshape(z_train, (z_train.shape[0],1))
z_train_ravel = np.ravel(z_train)
z_test_ravel = np.ravel(z_test)

i=0
for lmbd in lambdas:
    j=0  
    for eta in etas: 
        
        #####own NN implementation######
        dnn = NeuralNetwork(x_train, z_train, eta=eta, lmbd=lmbd, epochs=epochs, batch_size=M, n_hidden_neurons=n_hidden_neurons, n_categories=n_categories)
        dnn.train()
        
        z_fit = dnn.predict2(x_train)
        z_pred = dnn.predict2(x_test)
        
        
        NN_err_train[i,j] = accuracy_score(z_train,z_fit)
        NN_err_test[i,j] = accuracy_score(z_test,z_pred)
       
        #####scikit NN implementation#####
        dnn2 = MLPClassifier(hidden_layer_sizes=n_hidden_neurons, activation='relu', solver ='lbfgs',
                            alpha=lmbd, batch_size = M, learning_rate_init=eta, max_iter=epochs)
        dnn2.fit(x_train, z_train_ravel)
        z_fit2 = dnn2.predict(x_train)
        z_pred2 = dnn2.predict(x_test)
        
        DNN_scikit_train[i,j] = accuracy_score_numpy(z_train_ravel,z_fit2)
        DNN_scikit_test[i,j] = accuracy_score_numpy(z_test_ravel,z_pred2)
#       
        #####Keras NN implementation#####
        dnn3 = create_neural_network_keras(n_hidden_neurons_v02, n_categories, eta=eta, lmbd=lmbd)
        dnn3.fit(x_train, z_train, epochs=epochs, batch_size=M, verbose=0)
        DNN_keras_train[i][j] = dnn3.evaluate(x_train, z_train)[0]
        DNN_keras_test[i][j] = dnn3.evaluate(x_test, z_test)[0]        
                
        j+=1
    i+=1
    


#Heatmaps for gridsearch on lambda and ridge
x_axis = etas # labels for x-axis
y_axis = lambdas # labels for y-axis 



heat1 = sns.heatmap(NN_err_train,vmin=0.009,vmax=1,annot=True, xticklabels=x_axis, yticklabels=y_axis, cmap="viridis",linewidths =0.5)
heat1.set(xlabel='learning rate', ylabel ='regularization', title = f"Accuracy score training set (Act:leakyReLU-softmax)")
plt.savefig(f"Results/NN/BreastCancer_softmax_accuracy_score_train_.png", dpi=150)
plt.show()


heat2 = sns.heatmap(NN_err_test,vmin=0.009,vmax=1,annot=True, xticklabels=x_axis, yticklabels=y_axis, cmap="viridis",linewidths =0.5)
heat2.set(xlabel='learning rate', ylabel ='regularization', title = f"Accuracy score test set (Act:leakyReLU-softmax)")
plt.savefig(f"Results/NN/BreastCancer_softmax_accuracy_score_test.png", dpi=150)
plt.show()


heat3 = sns.heatmap(DNN_scikit_train,vmin=0.009,vmax=1,annot=True, xticklabels=x_axis, yticklabels=y_axis, cmap="viridis",linewidths =0.5) 
heat3.set(xlabel='learning rate', ylabel ='regularization', title = f"Accuracy score training set Scikit (Act: ReLU)")
plt.savefig(f"Results/NN/BreastCancer_accuracy_score_train_scikit.png", dpi=150)
plt.show()


heat4 = sns.heatmap(DNN_scikit_test,vmin=0.009,vmax=1,annot=True, xticklabels=x_axis, yticklabels=y_axis, cmap="viridis",linewidths =0.5)
heat4.set(xlabel='learning rate', ylabel ='regularization', title = f"Accuracy score training set Scikit( Act: ReLU)")
plt.savefig(f"Results/NN/BreastCancer_accuracy_score_test_scikit.png", dpi=150)
plt.show()

heat5 = sns.heatmap(DNN_keras_train,vmin=0.009,vmax=1,annot=True, xticklabels=x_axis, yticklabels=y_axis, cmap="viridis",linewidths =0.5)
heat5.set(xlabel='learning rate', ylabel ='regularization', title = f"Accuracy score training set (Act:leakyReLU-tanh)")
plt.savefig(f"Results/NN/BreastCancer_softmax_accuracy_score_train_keras_l2.png", dpi=150)
plt.show()

heat5 = sns.heatmap(DNN_keras_test,vmin=0.009,vmax=1,annot=True, xticklabels=x_axis, yticklabels=y_axis, cmap="viridis",linewidths =0.5)
heat5.set(xlabel='learning rate', ylabel ='regularization', title = f"Accuracy score test set (Act:leakyReLU-tanh)")
plt.savefig(f"Results/NN/BreastCancer_softmax_accuracy_score_test_keras_l2.png", dpi=150)
plt.show()
