"""
This program performs Ridge and Lasso regression on a synthetic dataset generated by the Franke Function
 and scan through hyperparameter values.
 The program return plots of Error versus hyperparameter Lambda for a given polynomial degree (up to 10)
Author: R Corseri & L Barreiro
"""
#%%
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
from random import random, seed
from sklearn import linear_model
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.preprocessing import MinMaxScaler, StandardScaler, Normalizer, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.utils import resample
from imageio import imread
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
#import Functions module
from Functions import FrankeFunction, DesignMatrix, MSE, R2


#%%
#Ridge & Lasso on the Franke function
#Create data
#np.random.seed(2003)
n = 100
maxdegree = 5

x = np.random.uniform(0,1,n)
y = np.random.uniform(0,1,n)
z = FrankeFunction(x, y)
z = z + np.random.normal(0,0.1,z.shape)


x = np.array(x).reshape(n,1)
y = np.array(y).reshape(n,1)

x1 = np.hstack((x,y)).reshape(n,2)


# Split the data in test and training dataset
x_train, x_test, z_train, z_test = train_test_split(x1, z, test_size=0.2)
#z_test = z_test.reshape(len(z_test),1)
#z_train = z_train.reshape(len(z_train),1)

# Scale the data
# scaler = StandardScaler()
# scaler.fit(x_train)
# x_train_scaled = scaler.transform(x_train)
# x_test_scaled = scaler.transform(x_test)
# scaler.fit(z_test)
# z_test_scaled = scaler.transform(z_test)
# scaler.fit(z_train)
# z_train_scaled = scaler.transform(z_train)
    
#Design-matrix X
X_train = DesignMatrix(x_train[:,0],x_train[:,1],maxdegree)
X_test = DesignMatrix(x_test[:,0],x_test[:,1],maxdegree)



#%%
# Decide which values of lambda to use
nlambdas = 100
lambdas = np.logspace(-4, 4, nlambdas)

MSERidgePredict = np.zeros(nlambdas)
MSELassoPredict = np.zeros(nlambdas)
R2RidgePredict = np.zeros(nlambdas)
R2LassoPredict = np.zeros(nlambdas)
MSERidgeTilde = np.zeros(nlambdas)
MSELassoTilde = np.zeros(nlambdas)
R2RidgeTilde = np.zeros(nlambdas)
R2LassoTilde = np.zeros(nlambdas)


for i in range(nlambdas):
    lmb = lambdas[i]
    # Make the fit using Ridge and Lasso
    RegRidge = linear_model.Ridge(lmb,fit_intercept=False)
    RegRidge.fit(X_train,z_train)
    RegLasso = linear_model.Lasso(lmb,fit_intercept=False)
    RegLasso.fit(X_train,z_train)
    # and then make the prediction
    ypredictRidge = RegRidge.predict(X_test)
    ypredictLasso = RegLasso.predict(X_test)
    ytildeRidge = RegRidge.predict(X_train)
    ytildeLasso = RegLasso.predict(X_train)
    # Compute the MSE and print it
    MSERidgePredict[i] = MSE(z_test,ypredictRidge)
    MSELassoPredict[i] =MSE(z_test,ypredictLasso)
    R2RidgePredict[i] = R2(z_test,ypredictRidge)
    R2LassoPredict[i] = R2(z_test,ypredictLasso)
    
    MSERidgeTilde[i] = MSE(z_train,ytildeRidge)
    MSELassoTilde[i] = MSE(z_train,ytildeLasso)
    R2RidgeTilde[i] = R2(z_train,ytildeRidge)
    R2LassoTilde[i] = R2(z_train,ytildeLasso)
    
    print(lmb,RegRidge.coef_)
    print(lmb,RegLasso.coef_)

# Now plot the results
plt.figure()
plt.plot(np.log10(lambdas), MSERidgePredict, 'r--', label = 'MSE Ridge Test')
plt.plot(np.log10(lambdas), MSERidgeTilde, 'r', label = 'MSE Ridge Train')
plt.plot(np.log10(lambdas), MSELassoPredict, 'b--', label = 'MSE Lasso Test')
plt.plot(np.log10(lambdas), MSELassoTilde, 'b', label = 'MSE Lasso Train')
plt.xlabel('log10(lambda)')
plt.ylabel('MSE')
plt.legend()
plt.savefig("plots/Ridge_Lasso/MSE_vs_lambda_RIDGE_LASSO.png", dpi=150)
plt.show()

plt.figure()
plt.plot(np.log10(lambdas), R2RidgePredict, 'r--', label = 'R2 Ridge Test')
plt.plot(np.log10(lambdas), R2RidgeTilde, 'r', label = 'R2 Ridge Train')
plt.plot(np.log10(lambdas), R2LassoPredict, 'b--', label = 'R2 Lasso Test')
plt.plot(np.log10(lambdas), R2LassoTilde, 'b', label = 'R2 Lasso Train')
plt.xlabel('log10(lambda)')
plt.ylabel('R2')
plt.legend()
plt.savefig("plots/Ridge_Lasso/R2_vs_lambda_RIDGE_LASSO.png", dpi=150)
plt.show()

