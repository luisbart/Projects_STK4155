'''
This###This program performs Ridge regression on a synthetic dataset generated by the Franke Function
with cross-validation resampling
The program returns plot Error against polynomial degree (up to 10) for a given hyper parameter Lamda
Author: R Corseri & L Barreiro'''

#%%

import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold
from Functions import RidgeReg, MSE, FrankeFunction, DesignMatrix
import seaborn as sb

#%%

#Model complexity (polynomial degree up to 7)
maxdegree= 5

#Number of k-fold (between 5 and 10) for cross-validation
k = 10
kfold = KFold(n_splits = k)

#For Ridge regression, set up the hyper-parameters to investigate
nlambdas = 9
lambdas = np.logspace(-4, 4, nlambdas)


# Generate dataset with n observations
n = 100
x1 = np.random.uniform(0,1,n)
x2 = np.random.uniform(0,1,n)

#Define noise
var = 0.01
noise = np.random.normal(0,var,n)

y = FrankeFunction(x1,x2) + noise 

x1 = np.array(x1).reshape(n,1)
x2 = np.array(x2).reshape(n,1)
x = np.hstack((x1,x2)).reshape(n,2)

#Scaling not needed


#%%
# Plot all in the same figure as subplots

#Initialize before looping:
polydegree = np.zeros(maxdegree)
error_Kfold = np.zeros((maxdegree,k))
estimated_mse_Kfold = np.zeros(maxdegree)
bias = np.zeros(maxdegree)
variance = np.zeros(maxdegree)

E = np.zeros((maxdegree,9))

# Create a matplotlib figure
fig, ax = plt.subplots()

for l in range(nlambdas):   
    i=0
    for degree in range(maxdegree): 
        j=0
        for train_inds, test_inds in kfold.split(x):
            
            x_train = x[train_inds]
            y_train = y[train_inds]   
            x_test = x[test_inds]
            y_test = y[test_inds]
                 
            X_train = DesignMatrix(x_train[:,0],x_train[:,1],degree+1)
            X_test = DesignMatrix(x_test[:,0],x_test[:,1],degree+1)
            y_fit, y_pred, Beta = RidgeReg(X_train, X_test, y_train, y_test,lambdas[l])
            
            error_Kfold[i,j] = MSE(y_test,y_pred)
            
            j+=1
            
        estimated_mse_Kfold[degree] = np.mean(error_Kfold[i,:])
        polydegree[degree] = degree+1
                
        i+=1
    
    E[:,l] = estimated_mse_Kfold
    ax.plot(polydegree, estimated_mse_Kfold, label='%.0e' %lambdas[l])

plt.xlabel('Model complexity')    
plt.xticks(np.arange(1, len(polydegree)+1, step=1))  # Set label locations.
plt.ylabel('MSE')
plt.title('MSE Ridge regression for different lambdas (kfold=10)')

# Add a legend
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles[::-1], labels[::-1], title='lambda', loc='center right', bbox_to_anchor=(1.27, 0.5))

#Save figure
plt.savefig("plots/Ridge_Lasso/Ridge_CV_DifferentLambdas.png",dpi=150, bbox_inches='tight')
plt.show()

#%%
#Create a heatmap with the error per nlambdas and polynomial degree

heatmap = sb.heatmap(E,annot=True, annot_kws={"size":7}, cmap="coolwarm", xticklabels=lambdas, yticklabels=range(1,maxdegree+1), cbar_kws={'label': 'Mean squared error'})
heatmap.invert_yaxis()
heatmap.set_ylabel("Complexity")
heatmap.set_xlabel("lambda")
heatmap.set_title("MSE heatmap, Cross Validation, kfold = {:}".format(k))
plt.tight_layout()
plt.savefig("plots/Ridge_Lasso/Ridge_CV_heatmap.png",dpi=150)
plt.show()

