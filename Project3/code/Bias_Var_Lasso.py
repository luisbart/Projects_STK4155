# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 07:31:06 2022

@author: luis.barreiro
"""

#%%
import os
os.chdir("C:/Users/luis.barreiro/Documents/GitHub/Projects_STK4155/Project3")
cwd = os.getcwd()
print(cwd)

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
from Functions import LassoReg, DesignMatrix, FrankeFunction
import seaborn as sb


#%%
np.random.seed(3)        #create same seed for random number every time

#For Ridge regression, set up the hyper-parameters to investigate
lmbd = 1e-6

#Number of bootstraps
n_bootstraps = 75

# Generate dataset with n observations
n = 100
x = np.random.uniform(0,1,n)
y = np.random.uniform(0,1,n)

#Define noise
var = 0.01
noise = np.random.normal(0,var,n)

z = FrankeFunction(x,y) + noise 

x = np.array(x).reshape(n,1)
y = np.array(y).reshape(n,1)
x1 = np.hstack((x,y)).reshape(n,2)

#Split train (80%) and test(20%) data before looping on polynomial degree
x_train, x_test, z_train, z_test = train_test_split(x1, z, test_size=0.2)

    
#Scaling not needed

#%%
#Define maximal model complexity
maxdegree= 25

#Initialize before looping:
TestError = np.zeros(maxdegree)
TrainError = np.zeros(maxdegree)
TestR2 = np.zeros(maxdegree)
TrainR2 = np.zeros(maxdegree)
polydegree = np.zeros(maxdegree)

error = np.zeros(maxdegree)
bias = np.zeros(maxdegree)
variance = np.zeros(maxdegree)

#E = np.zeros((maxdegree,9))

#Initialize bootstrap matrice
z_pred = np.empty((z_test.shape[0],n_bootstraps))

for degree in range(maxdegree):   
    for i in range(n_bootstraps):
        x_, z_ = resample(x_train,z_train)
      
        X_train = DesignMatrix(x_[:,0],x_[:,1],degree+1)
        X_test = DesignMatrix(x_test[:,0],x_test[:,1],degree+1)
        z_fit, z_pred[:,i] = LassoReg(X_train, X_test, z_, z_test,lmbd)
                    
    z_test = np.reshape(z_test, (len(z_test),1))
    polydegree[degree] = degree+1
          
    error[degree] = np.mean( np.mean((z_test - z_pred)**2, axis=1, keepdims=True) )
    bias[degree] = np.mean( (z_test - np.mean(z_pred, axis=1, keepdims=True))**2 )
    variance[degree] = np.mean( np.var(z_pred, axis=1, keepdims=True) )
        

plt.plot(range(1,maxdegree+1), error, label = 'Error')
plt.plot(range(1,maxdegree+1), bias, label = 'Bias')
plt.plot(range(1,maxdegree+1), variance, label = 'Variance')
plt.ylabel('Error')
plt.xlabel('Model complexity: polynomial degree')
plt.title("Variance-Bias tradeoff for Lasso")
plt.legend()
plt.savefig("Results/bias_variance_tradeoff/Lasso_bias_var_tradeoff.png",dpi=150)
plt.show()

#Check that bias+variance=error
temp=error-(bias+variance)
print(temp)
