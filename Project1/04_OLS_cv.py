# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 12:15:00 2022

@author: luis.barreiro
"""
import numpy as np
import matplotlib.pyplot as plt
#from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from Functions import LinReg, DesignMatrix,FrankeFunction, MSE
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample

#%%

#Model complexity (polynomial degree up to 7)
maxdegree= 5

#Number of k-fold (between 5 and 10) for cross-validation
k = 10
kfold = KFold(n_splits = k)

# Make data set.
n = 100
x = np.random.uniform(0,1,n)
y = np.random.uniform(0,1,n)
z = FrankeFunction(x,y)

#Add normally distributed noise
#y = y + np.random.normal(0,0.1,y.shape)

x = np.array(x).reshape(n,1)
y = np.array(y).reshape(n,1)
x1 = np.hstack((x,y)).reshape(n,2)

#Scaling
#y_train_mean = np.mean(y_train)
#x_train_mean = np.mean(x_train)
#x_train = x_train - x_train_mean
#y_train = y_train - y_train_mean
#x_test = x_test - x_train_mean
#y_test = y_test - y_train_mean

#Initialize before looping:
polydegree = np.zeros(maxdegree)
error_Kfold = np.zeros((maxdegree,k))
estimated_mse_Kfold = np.zeros(maxdegree)
bias = np.zeros(maxdegree)
variance = np.zeros(maxdegree)


i=0

#OLS
for degree in range(maxdegree): 
    j=0
    for train_inds, test_inds in kfold.split(x1):
        
        x_train = x1[train_inds]
        y_train = z[train_inds]   
        x_test = x1[test_inds]
        y_test = z[test_inds]
             
        X_train = DesignMatrix(x_train[:,0],x_train[:,1],degree+1)
        X_test = DesignMatrix(x_test[:,0],x_test[:,1],degree+1)
        y_fit, y_pred, Beta = LinReg(X_train, X_test, y_train)
        
        error_Kfold[i,j] = MSE(y_test,y_pred)
        
        j+=1
        
    estimated_mse_Kfold[degree] = np.mean(error_Kfold[i,:])
    polydegree[degree] = degree+1
    
    i+=1
     

#####Plots####
    
plt.plot(polydegree, estimated_mse_Kfold, label='OLS Error Cross Validation')
plt.xticks(np.arange(1, len(polydegree)+1, step=1))  # Set label locations.
plt.xlabel('Model complexity')
plt.ylabel('Mean squared error')
plt.legend()
plt.savefig("plots/OLS/OLS_Error_CrossValidation.png",dpi=150)
plt.show()

#%%
## Cross-validation using cross_val_score from sklearn along with KFold

# kfold is an instance initialized above as:
# kfold = KFold(n_splits = k)

estimated_mse_sklearn = np.zeros(maxdegree)
i = 0
for degree in range(maxdegree):
    model = LinearRegression(fit_intercept=False)
    polydegree[degree] = degree+1
    X = DesignMatrix(x1[:,0],x1[:,1],degree+1)
    
    estimated_mse_folds = cross_val_score(model, X, z, scoring='neg_mean_squared_error', cv=kfold)

    # cross_val_score return an array containing the estimated negative mse for every fold.
    # we have to the the mean of every array in order to get an estimate of the mse of the model
    estimated_mse_sklearn[i] = np.mean(-estimated_mse_folds)

    i += 1

## Plot and compare the slightly different ways to perform cross-validation

plt.figure()
plt.plot(polydegree, estimated_mse_Kfold, 'b-', label = 'KFold')
plt.plot(polydegree, estimated_mse_sklearn, 'r--', label = 'cross_val_score')
plt.xticks(np.arange(1, 6, step=1))  # Set label locations.
plt.xlabel('Complexity')
plt.ylabel('mse')
plt.legend()
plt.savefig("plots/OLS/Error_kfold_sklearn.png",dpi=150)
plt.show()

#%% Compare MSE from bootstrap(n=100) and cross-validation (kfold=7)
# Copy bootstrap
#Bootstrap
n_bootstraps = 75

# Make data set. (take from previous exercise)
#np.random.seed(2003)
n = 100
maxdegree = 5

x = np.random.uniform(0,1,n)
y = np.random.uniform(0,1,n)
z = FrankeFunction(x, y)
z = z + np.random.normal(0,0.1,z.shape)

x = np.array(x).reshape(n,1)
y = np.array(y).reshape(n,1)
z = np.array(z).reshape(n,1)

x1 = np.hstack((x,y)).reshape(n,2)


error = np.zeros(maxdegree)
bias = np.zeros(maxdegree)
variance = np.zeros(maxdegree)
polydegree = np.zeros(maxdegree)
x_train, x_test, z_train, z_test = train_test_split(x1, z, test_size=0.2)


for degree in range(maxdegree):
    X_train = DesignMatrix(x_train[:,0],x_train[:,1],degree+1)
    X_test = DesignMatrix(x_test[:,0],x_test[:,1],degree+1)
    z_pred = np.zeros((z_test.shape[0], n_bootstraps))
    for i in range(n_bootstraps):
        x_, z_ = resample(X_train, z_train)
        z_fit, zpred, beta = LinReg(x_, X_test, z_)
        z_pred[:, i] = zpred.ravel()

  
    
    polydegree[degree] = degree+1
    error[degree] = np.mean( np.mean((z_test - z_pred)**2, axis=1, keepdims=True) )
    bias[degree] = np.mean( (z_test - np.mean(z_pred, axis=1, keepdims=True))**2 )
    variance[degree] = np.mean( np.var(z_pred, axis=1, keepdims=True) )
#    print('Polynomial degree:', degree)
#    print('Error:', error[degree])
#    print('Bias^2:', bias[degree])
#    print('Var:', variance[degree])
#    print('{} >= {} + {} = {}'.format(error[degree], bias[degree], variance[degree], bias[degree]+variance[degree]))

plt.plot(polydegree, error, 'r--', label='Bootstrap (n=75)')
plt.plot(polydegree, estimated_mse_Kfold, 'b-', label = 'Cross-Validation (k=10)')
plt.xticks(np.arange(1, 6, step=1))  # Set label locations.
plt.xlabel('Model complexity')
plt.ylabel("Mean square error")
plt.legend()
plt.savefig("plots/OLS/Boot_vs_CV.png",dpi=150)
plt.show()
