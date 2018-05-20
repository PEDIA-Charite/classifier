# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import logging
import csv
from sklearn import preprocessing
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.externals import joblib
from data import Data
from sklearn import svm, datasets, ensemble
from scipy import interp
from itertools import cycle
from sklearn.model_selection import KFold
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import GroupKFold
from sklearn.metrics import classification_report
from sklearn.svm import SVC
from shutil import copyfile
import multiprocessing as mp
from rank import *
from constants import *
from sklearn.kernel_approximation import RBFSampler


# Setup logging
logger = logging.getLogger(__name__)
console_handle = logging.StreamHandler()
console_handle.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
console_handle.setFormatter(formatter)
logger.addHandler(console_handle)

def classify(train_data, test_data, path, config_data, cv_fold=None, param_g=None, param_c=None):
    #    param_fold, mode=NORMAL_MODE, filter_feature=None, cv_fold=None, tuning=None):
    """ SVM classification of all samples in the instance of Data against a given training
    data set that is also an instance of class Data """

    # Set the parameters by cross-validation

    param_fold = config_data['param_fold']
    filter_feature = config_data['filter_feature']
    mode = config_data['running_mode']

    X = []
    y = []
    group = []

    for case in train_data:
        if filter_feature == None:
            [X.append(value) for value in train_data[case][0]]
        else:
            for value in train_data[case][0]:
                X.append(value[~np.in1d(range(len(value)), filter_feature)])
        for value in train_data[case][1]:
            y.append(value)
            group.append(case)

    X = np.array(X)
    X = X.astype(float)
    # data is scaled to values between 1 and 0 using minmax scaler
    normalizer = preprocessing.MinMaxScaler().fit(X)
    X = normalizer.transform(X)
    y = np.array(y)

    if not param_g:
        param_g = config_data['param_g']
    if not param_c:
        param_c = config_data['param_c']

    # Tuning parameter
    if param_fold > 0:
        group = np.array(group)
        best_param = param_tuning(X, y, group, config_data)
        param_g = best_param[0] 
        param_c = best_param[1] 
            
    logger.info("Start training")
    logger.info("RBF sampler with gamma: %f", param_g)
    logger.info("Linear SVM with C: %f", param_c)
    rbf_feature = RBFSampler(gamma=param_g, random_state=1)
    X_features = rbf_feature.fit_transform(X)
    clf = svm.LinearSVC(C=param_c, class_weight='balanced', loss='hinge')
    clf.fit(X_features, y)
    logger.debug("Feature weights %s", str(clf.coef_[0]))
    
    # Classify test set
    logger.info("Start testing")
    pedia = {}
    for case in test_data:
        test_X = []
        score = []
        if filter_feature == None:

            [test_X.append(value) for value in test_data[case][0]]
        else:
            for value in test_data[case][0]:
                test_X.append(value[~np.in1d(range(len(value)), filter_feature)])

        test_X = np.array(test_X)
        test_X = test_X.astype(float)
        X = rbf_feature.fit_transform(normalizer.transform(test_X))
        score = clf.decision_function(X)

        score = np.array(score)
        pathogenicity = np.array(test_data[case][1])
        gene = np.array(test_data[case][2])
        gene_name = np.array(test_data[case][3])
        length = len(score)
        sorted_index = score.argsort()[::-1][:length]
        score = score[sorted_index]
        pathogenicity = pathogenicity[sorted_index]
        gene = gene[sorted_index]
        gene_name = gene_name[sorted_index]
        pedia.update({case:[score, pathogenicity, gene, gene_name]})

        if mode == NORMAL_MODE:
            filename = path + "/" + case + ".csv"
            with open(filename, 'w') as csvfile:
                fieldnames = ['gene_name', 'gene_id', 'pedia_score', 'label']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for index in range(len(score)):
                    writer.writerow({'gene_name': gene_name[index], 'gene_id': gene[index], 'pedia_score': score[index], 'label': pathogenicity[index]})
            if cv_fold != None:
                cv_dir = path + "/" + str(cv_fold)
                if not os.path.exists(cv_dir):
                    os.mkdir(cv_dir)
                copyfile(filename, cv_dir + "/" + case + ".csv")
        else:
            fieldnames = ['gene_name', 'gene_id', 'pedia_score', 'label']
            writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
            writer.writeheader()
            for index in range(len(score)):
                writer.writerow({'gene_name': gene_name[index], 'gene_id': gene[index], 'pedia_score': score[index], 'label': pathogenicity[index]})

    if cv_fold != None:
        rank(pedia, str(cv_fold), path)

    return pedia


def param_tuning(X, y, group, config_data, path):

    param_fold = config_data['param_fold']
    
    tuning_set = []
    for g in PARAM_G:
        for c in PARAM_C:
            tuning_set.append([g, c])

    group = np.array(group)
    
    logger.info("Tuning hyper-parameters")
    
    param_acc = []
    for param in tuning_set:
        # Calculate top 1 acc on each param
        fold_count = 1
        acc = 0
        logger.info("Start parameter tuning on C: %f, gamma: %f", param[1], param[0])
        for train_index, test_index in GroupKFold(n_splits=param_fold).split(X, y, group):
            logger.debug("Start parameter tuning on fold %d", fold_count)

            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]
            
            # Train classifier 
            rbf_feature = RBFSampler(gamma=param[0], random_state=1)
            X_features = rbf_feature.fit_transform(X_train)
            clf = svm.LinearSVC(C=param[1], class_weight='balanced',loss='hinge')
            clf.fit(X_features, y_train)
            fold_count += 1
            top_count = 0
            logger.debug("Start testing")
            test_group = group[test_index]
            test_case = set(test_group)

            for case in test_case:
                test_idx = [np.where(test_group==case)]
                x_case_test = X_test[test_idx][0]
                y_case_test = y_test[test_idx][0]

                score = []
                X_test_feature = rbf_feature.fit_transform(x_case_test)
                score = clf.decision_function(X_test_feature)

                score = np.array(score)
                length = len(score)
                sorted_index = score.argsort()[::-1][:length]
                score = score[sorted_index]
                pathogenicity = y_case_test[sorted_index]
                if pathogenicity[0] == 1:
                    top_count += 1
            acc += top_count/len(test_case)
        param_acc.append(acc/param_fold)
        logger.debug("Parameter C: %f, gamma: %f, Top 1 acc: %f", param[0], param[1], acc/param_fold)
    max_acc = max(param_acc)
    max_index = [ i for i,v in enumerate(param_acc) if v==max_acc ]

    best_param = []
    if len(max_index) == 1:
        best_param = tuning_set[max_index[0]]
    else:
        max_params = np.array(tuning_set)[max_index]
        index = np.argmin(max_params[:,1])
        best_param = list(max_params[index])
    logger.info("Best parameter C: %f, gamma: %f, Top 1 acc: %f", best_param[1], best_param[0], max_acc)
    
                    #filename = path + "/" + case + ".csv"
                    #with open(filename, 'w') as csvfile:
                    #    fieldnames = ['gene_name', 'gene_id', 'pedia_score', 'label']
                    #    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    #    writer.writeheader()
                    #    for index in range(len(score)):
                    #        writer.writerow({'gene_name': gene_name[index], 'gene_id': gene[index], 'pedia_score': score[index], 'label': pathogenicity[index]})

    return best_param

def classify_test(train, test, path, config_data):
    default_value = get_feature_default(train)
    set_default(train, default_value)
    set_default(test, default_value)

    pedia = classify(train, test, path, config_data)

    return pedia

def classify_cv(data, path, config_data):

    kf = KFold(n_splits=config_data['cv_fold'], shuffle=True)
    sample_names = np.array(list(data.keys()))

    fold_count = 1
    results = []
    pedia = {}
    param_sets = []
    pool = mp.Pool(processes = config_data['cv_cores'])
    for train_idx, test_idx in kf.split(sample_names):
        logger.info("Start fold %d", fold_count)
        train_keys = sample_names[train_idx]
        test_keys = sample_names[test_idx]

        train = {key:data[key] for key in train_keys}
        test = {key:data[key] for key in test_keys}

        default_value = get_feature_default(train)
        set_default(train, default_value)
        set_default(test, default_value)
        param_sets.append([train, test, path, config_data, fold_count])
        fold_count += 1
    
    results = [pool.apply_async(classify, args=(p)) for p in param_sets]
    for result in results:
        pedia.update(result.get())
    
    pool.close()
    pool.join()

    return pedia

def classify_cv_tuning_test(data, path, config_data):
    kf = KFold(n_splits=config_data['cv_fold'], shuffle=True)
    sample_names = np.array(list(data.keys()))

    fold_count = 1
    results = []
    pedia = {}
    param_sets = []
    pool = mp.Pool(processes = config_data['cv_cores'])
    tuning_set = []
    for g in PARAM_G:
        for c in PARAM_C:
            tuning_set.append([g, c])
    for train_idx, test_idx in kf.split(sample_names):
        logger.info("Start fold %d", fold_count)
        train_keys = sample_names[train_idx]
        test_keys = sample_names[test_idx]

        train = {key:data[key] for key in train_keys}
        test = {key:data[key] for key in test_keys}

        default_value = get_feature_default(train)
        set_default(train, default_value)
        set_default(test, default_value)
        for tuning_idx, tuning in enumerate(tuning_set):
            tuning_path = os.path.join(path, 'param_' + str(tuning_idx))
            if not os.path.exists(tuning_path):
                os.mkdir(tuning_path)
            param_sets.append([train, test, tuning_path, config_data, fold_count, tuning[0], tuning[1]])
        fold_count += 1
    
    results = [pool.apply_async(classify, args=(p)) for p in param_sets]
    for result in results:
        pedia.update(result.get())

    pool.close()
    pool.join()

    return pedia

def classify_loocv(data, path, running_mode, filter_feature=None):
    sample_names = np.array(list(data.keys()))
    genes = []
    for name in sample_names:
        gene_idx, = np.where(data[name][Data.LABEL_IDX] == 1)
        genes.append(np.array(data[name][Data.GENE_IDX])[gene_idx].tolist()[0])

    logo = LeaveOneGroupOut()

    fold_count = 1
    pedia = {}

    csvfile = open(path + "/loocv_group.csv", 'w')
    writer = csv.writer(csvfile)
    for train_idx, test_idx in logo.split(sample_names, groups=genes):
        logger.info("Start fold %d", fold_count)
        train_keys = sample_names[train_idx]
        test_keys = sample_names[test_idx]

        train = {key:data[key] for key in train_keys}
        test = {key:data[key] for key in test_keys}

        default_value = get_feature_default(train)
        set_default(train, default_value)
        set_default(test, default_value)

        pedia.update(classify(train, test, path, running_mode, filter_feature))
        fold_count += 1

        writer.writerow([np.array(genes)[test_idx][0], test_keys.tolist()])
    return pedia

def get_feature_default(data):
    features_default = []
    feature_dim = next(iter(data.values()))[Data.FEATURE_IDX].shape[1]
    for index in range(feature_dim):
        feature_value = np.concatenate([data[case][Data.FEATURE_IDX][:, index] for case in data], axis=0)
        m = round(np.nanmin(feature_value.astype(np.float)), 10)
        features_default.append(m)
    return features_default

def set_default(data, features_default):
    feature_dim = len(features_default)
    for index in range(feature_dim):
        for case in data:
            f_data = data[case][Data.FEATURE_IDX]
            f_data[f_data[:, index] == 'nan', index] = features_default[index]


