#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

import numpy as np
import pandas as pd

### feature list to import:

features_list = ['poi','salary', 'loan_advances',
        'bonus', 'deferred_income', 'exercised_stock_options', 
        'total_stock_value', 'to_messages', 'other',
        'long_term_incentive', 'director_fees', 'other', 'salary']

print "loading the features: ", features_list
### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)

### first cleanup:
def correctRobert(data):
    """
    function to clean Robert Belfer data whiwh was swiped to the
    wrong columns for part of it.
    Input:
    - dataset dictionary
    Output:
    - Robert Belfer dataset reorganised
    """
    in_robert = data["BELFER ROBERT"]
    robert = {}
    unchange = ['poi','salary', 'to_messages',
            'shared_receipt_with_poi', 'from_messages',
            'from_this_person_to_poi', 'email_address',
            'from_poi_to_this_person']
    ol_val = ["deferral_payments", "total_payments",
            "exercised_stock_options", "restricted_stock_deferred",
            "total_stock_value", "director_fees"]
    ne_val = ["deferred_income", "director_fees", "total_payments",
            "restricted_stock", "restricted_stock_deferred",
            "expenses"]
    for key in in_robert.keys():
        robert[key] = "NaN"
    for old, new in zip(ol_val, ne_val):
        robert[new] = in_robert[old]
    for key in unchange:
        robert[key] = in_robert[key]
    return robert
print "cleaning Robert Belfer data"
data_dict["BELFER ROBERT"] = correctRobert(data_dict)

##### Dataset exporation function
# check if there if 0 value in dictionary to know
#if only NaN give 0 value later:
def testVal(data_dict, num_value):
    '''test if a numerical value appear in the dict
    print the dict key and value if it does
    return the number of matching value found
    '''
    ret = 0
    se = set()
    kse = set()
    for key, value in data_dict.iteritems():
        for k, num in value.iteritems():
            if num == num_value:
                ret += 1
                se.add(k)
                kse.add(num)
    return (ret, se, kse)

#print testVal(data_dict, 0)
#print "#####################################"
# no null value in money related feature, so all 0.0 value later
#found are NaN, except in the category:
#poi; from_this_person_to_poi; from_poi_to_this_person

### Making new features. The results where not good so these
### functions are not used in this script
from math import log
from math import exp

def logtrans(data, feature1, nw_feat, fe_list=features_list):
    """
    function to make the log transform of features and add them
    into a dictionary.
    Input:
    - data : data dictionary
    - feature1 : string of the feature name to transform
    - nw_feat : string used to name the calculated feature
    - fe_list: list of the feature name in the dataset
    Output a Tuple:
    - data: data dictionary with the added feature
    - fe_list: updated feature list
    """
    for key, value in data.iteritems():
        if isinstance(value[feature1], (int, float)):
            value[nw_feat] = log(value[feature1] + 1, 10)#log(x, base)
        else:
            value[nw_feat] = "NaN"
    fe_list.append(nw_feat)
    return data, fe_list

#print "making logtransform of salary, total_stock_value,
#        total_payments"
#log_ls = [("salary", "log(salary)"),
#        ("total_stock_value", "log(total_stock_value)"),
#        ("total_payments", "log(total_payments)")]
#for origin, trans in log_ls:
#    data_dict, features_list = logtrans(data_dict, origin, trans)

def relProp(data_dict, feature1, feature2, new_feature,
        feat_list=features_list):
    """
    function to make a new feature representing the relative 
    proportion of two existing feature.
    Input:
    - data_dict: data dictionary
    - feature1, feature2: String of the features names to do
       feature1 / feature2
    - new_feature: String of the new feature name
    - feat_list: list of feature names found in data_dict
    Output:
    Tuple containing:
    - data_dict: dictionary of the data with the new feature
    - feat_list: updated list of feature names
    """
    for key, value in data_dict.iteritems():
        if isinstance(value[feature1], (int, float))\
                and isinstance(value[feature2], (int, float)):
            value[new_feature] = float(value[feature1]) / value[feature2]
        else:
            value[new_feature] = "NaN"
        data_dict[key] = value
    feat_list.append(new_feature)
    return data_dict, feat_list

#print "\nmaking new features...\n"
#print "features to make:"
#print "    - defferal / total_payments"
#print "    - bonus / salary"
#print "    - bonus / total_payments"
#print "    - exercised stock option / total stocks"
#
#new_feat_lst = [('deferred_income', 'total_payments', 'defe/paym'),
#        ('bonus', 'salary', 'bonus/salary'),
#        ('bonus', 'total_payments', 'bonus/paym'),
#        ('exercised_stock_options', 'total_stock_value',
#         'ex_st_opt/tot_sto')]
#"""
#for f1, f2, nf in new_feat_lst:
#    data_dict, features_list = relProp(data_dict, f1, f2, nf)

### Now let's do some cleaning using PCA, some helper 
### function are also defined in this part

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest
import matplotlib.pyplot as plt
import seaborn as snb
from sklearn.pipeline import Pipeline, FeatureUnion

# helper function for plotting 
def plotFeat(data, labl, fe_list,
        feat=('exercised_stock_options', 'other')):
    """
    function to plot a scatter plot of two functions:
    Input:
    - data: data array
    - fe_list: list of feature in the dataset
    Output:
    - Display a scatter plot
    - return: String "done" when function exit
    """
    id1 = fe_list.index(feat[0]) - 1
    id2 = fe_list.index(feat[1]) - 1 
    dat = np.array(data)
    Xn = [x for x,l in zip(dat[:,id1], labl) if l == 0]
    Yn = [y for y,l in zip(dat[:,id2], labl) if l == 0]
    Xp = [x for x,l in zip(dat[:,id1], labl) if l == 1]
    Yp = [y for y,l in zip(dat[:,id2], labl) if l == 1]
    plt.scatter(Xn, Yn, color="blue")
    plt.scatter(Xp, Yp, color="red")
    plt.xlabel('{0} {1}'.format('feature:', feat[0]))
    plt.ylabel('{0} {1}'.format('feature:', feat[1]))
    plt.show()
    return "done"

def axisShow(features, labels, fe_list=features_list,
        n_comp=4):
    """
    print each axis composition of PCA and it's explained variance.
    Input:
    - features: array of the feature values
    - labels: array of the features labels
    - fe_list: feature list
    - n_comp: number of component of the PCA
    Output:
    - display the graph
    - return string "done"
    """
    pca = PCA(n_components=n_comp)
    n_feat =  rescaler(features)
    fe_list = fe_list[1:]
    pca.fit(n_feat)
    vari = list(np.round(pca.explained_variance_ratio_, 5))
    dimension = ['{} {} {} {}'.format("Dimension", 
        x+1, "\nexplained Variance:", y) for x,y in enumerate(vari)]
    compo = pd.DataFrame(np.round(pca.components_, 5),
            columns = fe_list, index = dimension)
    ax = compo.plot(kind = "bar")
    ax.set_ylabel("Feature\nweight", rotation = 0, weight = 'bold',
            size = 'large')
    ax.yaxis.labelpad = 30
    plt.yticks(np.arange(-1, 1, 0.2))
    plt.title('feature weight composition of PCA axis and variance explained for each axis',
            weight='bold', size="x-large")
    ax.set_xticklabels(dimension, rotation=0, weight = 'bold',
            size='large')
    plt.show()
    return "done"

# functions to clean the dataset using PCA
def rescaler(data, verbose=False):
    """
    function to rescale a dataset
    Input:
    - data: array of feature value
    - verbose: Bool controling verbosity. default= False
    Output:
    - ret_data: rescaled dataset dictionary
    """
    scaler = MinMaxScaler()#StandardScaler()
    scaler.fit(data)
    if verbose:
        print "max data"
        print scaler.data_max_, "\n"
        print scaler.data_min_
    ret_data = scaler.transform(data)
    return ret_data

def pcaShow(feat, labl, axis=(0,1), n_comp=3):
    """
    function to print a scatter plot of data projected on 
    2 PCA axis.
    Input:
    - feat: feature ready to be fed in the PCA function
    - labl: list of the labels of the features
    - axis: tuple containing the number of the two axis to
            use for the projection
    - n_comp: number of component to find with the PCA
    Output:
    - Display a scatter plot of the feature projected on 
      the axis asked
    - return "done" when the function exit
    """
    pca_dat = PCA(n_components=n_comp)
    pca_dat.fit(feat)
    nfeat = pca_dat.transform(feat)
    Xn = [x for x,l in zip(nfeat[:,axis[0]], labl) if l == 0]
    Yn = [y for y,l in zip(nfeat[:,axis[1]], labl) if l == 0]
    Xp = [x for x,l in zip(nfeat[:,axis[0]], labl) if l == 1]
    Yp = [y for y,l in zip(nfeat[:,axis[1]], labl) if l == 1]
    plt.scatter(Xn, Yn, color="blue")
    plt.scatter(Xp, Yp, color="red")
    plt.xlabel('{0} {1}'.format('PCA axis', axis[0]))
    plt.ylabel('{0} {1}'.format('PCA axis', axis[1]))
    plt.show()
    return 'done'

def rmOutl(data_dict, feat, limits=(-2, 0.5), axis=0,
        n_comp=3, fe_list=features_list):
    """
    function to remove data points having value outside of
    a predefine interval when projected on PCA axis.
    Input:
    - data_dict: dictionary of dataset
    - feat: feature ready to be fed the PCA
    - limits: Interval of value for the PCA projection
    - axis: axis of the PCA to project on
    - n_comp: number of component for the PCA calcul
    - fe_list: list of feature names
    Output:
    - out_dict: dictionary of data with outlier removed
    """
    out_dict = {}
    scaler = MinMaxScaler()#StandardScaler()
    scaler.fit(feat)
    feat = scaler.transform(feat)
    pca = PCA(n_components=n_comp)
    pca.fit(feat)
    fe_list = [x for x in fe_list if x != "poi"]
    for person, data in data_dict.iteritems():
        adat = makeArr(data, fe_list)
        sc = scaler.transform(adat)
        trans = pca.transform(sc)
        if data['poi'] == 1.0:
            out_dict[person] = data
            print person, " is a poi not removing it!"
        elif trans[0, axis] > limits[0] and trans[0,axis] < limits[1]:
            out_dict[person] = data
        else:
            print "    ", person, " is an outlier! remoing it!"
    return out_dict


def makeArr(data, fe_list):
    """
    function to transform a dictionary into an array with
    th right shape to feed MinMaxScaler.
    Input:
    - data: a dictionary of data.
    - fe_list: list of features in the dataset
    Output:
    - arr: array of the right shape
    """
    li = []
    for feature in fe_list:
        if data[feature] == "NaN":
            li.append(0)
        else:
            li.append(data[feature])
    arr = np.array(li).reshape(1, -1)
    return arr

def findOutl(data,  n_passe, axis_sh=[(0, 1)], n_comp=3,
        fe_list=features_list, ploti=False):
    """
    function to find outliers and remove them, using PCA projection
    and an intervall for the projection. Can be made to display the
    PCA performed to find outlier and prepare function.
    The function will print out the name of the outliers found.
    Input:
    - data: data dictionary
    - n_passe: number of time the PCA elimination process has to
     be made on the dataset
    - axis_sh: list of tupple containing axis number
      to make the scatter plot if ploti is True
    - n_comp: number of component to use in the PCA fitting
    - fe_list: list of the feature name
    - ploti: boolean turning on the plotting function
    Output:
    - dictionary with the outliers removed.
    """
    for passe, variable in n_passe.iteritems():
        atad = featureFormat(data, fe_list, sort_keys = True)
        labels, features = targetFeatureSplit(atad)
        print "\nmaking the ", passe, "outlier cleaning..."
        data = rmOutl(data, features, variable["limits"],
                variable["axis"], n_comp, fe_list)
    print "\nall requested cleaning was done."
    if ploti:
        print "plotting data in axis"
        print "Look if no outlier stands out,",\
              " if yes, update Removal_sec by adding a key and a\
              dictionnary"
        print "press any key to plot the different graphs, ",\
              "each graph must be closed for the next one to appear.\n"
        atad = featureFormat(data, fe_list, sort_keys = True)
        labels, features = targetFeatureSplit(atad)
        features = rescaler(features, verbose=True)
        for axis in axis_sh:
            print "plotting axis: ", axis
            pcaShow(features, labels, axis)
    return data

ax = [(0, 1), (1, 2), (0, 2)]
Removal_sec = {0 : {"axis" : 0, "limits" : (-2, 0.5)}}#,
       # 1 : {"axis" : 0, "limits" : (-1.5, 1)},
       # 2 : {"axis" : 1, "limits" : (-1, 0.6)},
       # 3 : {"axis" : 1, "limits" : (-0.8, 2)}}

### Store to my_dataset for easy export below.
my_dataset = data_dict
### Remove outlier
my_dataset = findOutl(data=my_dataset, n_passe=Removal_sec,
        axis_sh=ax, ploti=False)


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

#### Make statistics about the dataset:

def stasum(labels_data, feature_data, feature_list, list_feature2sum):
    """
    function to make some descriptive statistics on some fetures of
    a dataset.
    Input:
    - labels_data: label as nested array
    - features_data: features as nested array
    - feature_list: list of the feature found in the dataset
    - list_feature2sum: list of feature to make the summary on
    Output:
    - dict of summary for each features found in list_feature2sum.
      for each feature a summary is presented containing:
        - key: feature name
        then the value of the tuple are:
        - number of NaN
        - mean
        - median
        - quartile 25%
        - quartile 75%
        - number of poi with non Nan data
     additional, general keys can be found in the output:
        - number of poi
        - number of points
    """
    retu = {}
    tot = len(labels_data)
    n_poi = sum(1 for x in labels if x == 1.0)
    retu["nb_data_point"] = tot
    retu["nb_poi_tot"] = n_poi
    for feat in list_feature2sum:
        col = feature_list.index(feat) - 1 
        retu[feat] = fstat(feature_data, col, labels_data)
    return retu

def fstat(data, col, labe):
    """
    function that take a data list of array and the column to
    summarize on.
    Input:
    - data: feature data in nested array
    - col: column index to summerize on
    Output:
    - dictionary with statistics 
    """
    a = np.array([item[col] for item in data])
    mea = a.mean()
    q25, med, q75 = np.percentile(a, [25, 50, 75])
    nul = a[a == 0.0].size
    lab = np.array(map(bool, labe))
    poi_nan = len([l for l in a[lab] if l == 0])
    mini = a.min()
    maxi = a.max()
    return {"NaN_num" : nul, "minimum" : mini, "mean" : mea,
            "median" : med, "q25" : q25, "q75" : q75,
            "maximum" : maxi, "poi_with_NaN" : poi_nan}

l_feat = ['salary', 'loan_advances',
        'bonus', 'deferred_income', 'exercised_stock_options', 
        'total_stock_value', 'to_messages', 'other',
        'long_term_incentive', 'director_fees']

stats = stasum(labels, features, features_list, l_feat)
for key in stats:
    print "\n- statistics for the ", key, " feature:"
    print stats[key]
print "\n"

######## importing different models: ###########
# SVM:
# param: kernel; gamma; C
from sklearn.svm import SVC

# AdaBoostClassifier:
# param: n_estimator
from sklearn.ensemble import AdaBoostClassifier

#kneighbors:
# param: n_neighbors
from sklearn.neighbors import KNeighborsClassifier

# Naive bayes:
from sklearn.naive_bayes import GaussianNB

# Random Forest:
from sklearn.ensemble import RandomForestClassifier
# n_estimators; min_samples_split; 

# Decision tree:
from sklearn.tree import DecisionTreeClassifier
# min_samples_split, min_samples_leaf

from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import StratifiedShuffleSplit

def makePipe(model):
    """
    function to make the pipeline.
    Input:
    - model to use in :
             - 'GaussianNB'
             - 'AdaBoost'
             - 'SVM'
             - 'KNeighbors'
             - 'RandomForest'
    Output:
    - Pipeline
    """
    scaler = MinMaxScaler()#StandardScaler()
    pca = PCA()
    selector = SelectKBest()
    combined_features = FeatureUnion([("pca", pca),
                       ("feat_select", selector)])
    if model == 'GaussianNB':
        pipe_clf = GaussianNB()
    elif model == 'AdaBoost':
        pipe_clf = AdaBoostClassifier()
    elif model == 'SVM':
        pipe_clf = SVC()
    elif model == 'KNeighbors':
        pipe_clf = KNeighborsClassifier()
    elif model == 'RandomForest':
        pipe_clf = RandomForestClassifier()
    else:
        print "no model chosen, please retry with a model. Ending"
        return "Not run"
    return Pipeline([("rescale", scaler),
        ("features", combined_features), ("classify", pipe_clf)])

### Classifier Tunning:
param_grid = dict(features__pca__n_components=[1, 2, 3, 4, 5],
        #classify__n_estimators=[8, 9, 10, 11, 15],
        #classify__learning_rate=[1.6, 1.8, 1.9, 2, 2.1, 2.2],
        #classify__min_samples_leaf=[1, 2, 3, 4],
        #classify__min_samples_split=[1, 2, 3, 4],
        features__feat_select__k=[2, 3, 4, 5, 6, 7, 8, 9, 10])

def classfyTune(features, labels, model, param,
        scores=["f1", "recall", "precision"], jobs=3):
    """
    function to test different classifier and return the score
    for different scoring methods on the best algorithm pick using the
    first score method given.
    Input:
    - features: feature ready to be fed to the algorithm
    - labels: labels ready to be fed to the algorithm
    - model: string representing one of the classifier accepted:
             - 'GaussianNB'
             - 'AdaBoost'
             - 'SVM'
             - 'KNeighbors'
             - 'RandomForest'
    - param: parameter grid used in the GridSearchCV
    - scores: list of scoring function to calculate the score.
              The first scoring function will be used to find the 
              "best" model.
    Output:
    - return the string "Not run" if no model was passed
    - return a dictionary containing:
          - algorithm name
          - best parameter found
          - scores: list of the different calculated scores
    """
    cv = StratifiedShuffleSplit(labels, n_iter=1000, random_state=42)
    pipeline = makePipe(model)
    if isinstance(pipeline, str):
        return "Not run"
    out_best = {"algo" : model, "best parameters" : {}, "scores" : {}}
    grid_search = GridSearchCV(pipeline, param, scoring=scores[0],
                  cv=cv, n_jobs=jobs)
    grid_search.fit(features, labels)
    out_best["best parameters"] = grid_search.best_params_
    out_best["scores"][scores[0]] = grid_search.best_score_
    nw_value = dict()
    for key, value in out_best["best parameters"].iteritems():
        nw_value[key] = [value]
    for scs in scores[1:]:
        nw_grid = GridSearchCV(pipeline, nw_value,
                scoring=scs, cv=cv, n_jobs=jobs)
        nw_grid.fit(features, labels)
        out_best["scores"][scs] = nw_grid.best_score_
    return out_best

alg = classfyTune(features, labels, "GaussianNB", param_grid)
print "\n\n", alg

## Make the final classifier after finding the classifier with good 
#  performance and done the tuning.

# Uncomment to display a graph of the axis composition.
#axisShow(features, labels)

clf = makePipe("GaussianNB")
clf.set_params(features__pca__n_components=4, features__feat_select__k=7)
clf.fit(features, labels)

from operator import itemgetter
fs = list()
sc =  clf.named_steps["features"].transformer_list[1][1].scores_
p_val = clf.named_steps["features"].transformer_list[1][1].pvalues_
fs = zip(features_list[1:], sc, p_val)
fs.sort(key=itemgetter(1), reverse=True)
print fs
    
## dump the classifier, dataset and feature_list
dump_classifier_and_data(clf, my_dataset, features_list)
