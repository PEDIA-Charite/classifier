# -*- coding: utf-8 -*-
import os
import sys
import numpy as np
import logging
import csv
from sklearn import preprocessing
from sklearn.model_selection import LeaveOneGroupOut
import joblib
from lib.data import Data
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
from lib.rank import *
from lib.constants import *
from lib.mapping import mapping
from sklearn.kernel_approximation import RBFSampler
import pandas as pd


# Setup logging
logger = logging.getLogger(__name__)
console_handle = logging.StreamHandler()
console_handle.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
console_handle.setFormatter(formatter)
logger.addHandler(console_handle)

def classify(train_data, test_data, path, config_data, cv_fold=None, rand_num=1, param_g=None, param_c=None):
    """ SVM classification of all samples in the instance of Data against a given training
    data set that is also an instance of class Data """

    # Set the parameters by cross-validation

    param_fold = config_data['param_fold']
    filter_feature = config_data['exclude_feature']

    X = []
    y = []
    group = []

    for case in train_data:
        if filter_feature == None:
            [X.append(value) for value in train_data[case][0]]
        else:
            for value in train_data[case][0]:
                # select inverse index of filter_feature
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

    if not param_c:
        param_c = config_data['param_c']

    # Tuning parameter
    if param_fold > 0:
        group = np.array(group)
        best_param = param_tuning(X, y, group, config_data, rand_num)
        param_c = best_param[0]

    logger.info("Start training")
    logger.info("Linear SVM with C: %f", param_c)
    clf = svm.LinearSVC(C=param_c, class_weight='balanced', loss='hinge', random_state=rand_num)
    clf.fit(X, y)
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

        test_X = np.array(test_X).astype(float)
        X = normalizer.transform(test_X)
        score = clf.decision_function(X)

        # Manage pedia results by dataframe and store in filename
        df = pedia_df(score, test_data, test_X, case, filter_feature)
        pedia.update({case: df.reset_index(drop=True)})
        filename = os.path.join(path, case + ".csv")
        new_json_filename = os.path.join(path, case + ".json")
        write_df_to_csv(df, filename)
        if config_data['test_path']:
            if os.path.isdir(config_data['test_path']):
                json_path = os.path.join(config_data['test_path'], str(case) + '.json')
            else:
                json_path = config_data['test_path']
        else:
            json_path = os.path.join(config_data['train_path'], str(case) + '.json')
        # Append pedia results to original JSON file, then store in new_json_filename
        #mapping(json_path, new_json_filename, filename, config_data)

    if cv_fold != None:
        rank(pedia, path, str(cv_fold))

    return pedia

def write_df_to_csv(df, filename):
    fieldnames = [
            'gene_name',
            'gene_id',
            'pedia_score',
            'feature_score',
            'cadd_score',
            'gestalt_score',
            'boqa_score',
            'pheno_score',
            'cada_score',
            'lirical_score',
            'xrare_score',
            'exomizer_score',
            'amelie_score',
            'label'
            ]
    df.to_csv(filename, sep=',', index=False, columns=fieldnames)

def pedia_df(score, test_data, test_X, case, filter_feature):
    df = pd.DataFrame({
        'pedia_score': score,
        'label': test_data[case][1],
        'gene_name': test_data[case][3],
        'gene_id': test_data[case][2]},
        )

    column_names = np.array([
        'feature_score',
        'cadd_score',
        'gestalt_score',
        'boqa_score',
        'pheno_score',
        'cada_score',
        'lirical_score',
        'xrare_score',
        'exomizer_score',
        'amelie_score'
        ])

    feature_df = pd.DataFrame(
            test_X,
            columns=column_names[~np.in1d(range(column_names.shape[0]), filter_feature)]
            )

    if filter_feature == None:
        filter_feature = []
    for idx in filter_feature:
        feature_df[column_names[idx]] = None
    df = pd.concat([df, feature_df], axis=1)
    df = df.sort_values('pedia_score', ascending=False)
    return df

def param_tuning(X, y, group, config_data, rand_num):

    param_fold = config_data['param_fold']
    tuning_set = []

    for c in PARAM_C:
        tuning_set.append([c])
    group = np.array(group)

    logger.info("Tuning hyper-parameters")

    param_acc = []
    for param in tuning_set:
        # Calculate top 1 acc on each param
        fold_count = 1
        acc = 0
        logger.info("Start parameter tuning on C: %f", param[0])
        for train_index, test_index in GroupKFold(n_splits=param_fold).split(X, y, group):
            logger.debug("Start parameter tuning on fold %d", fold_count)

            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            # Train classifier
            X_features = X_train

            clf = svm.LinearSVC(C=param[0], class_weight='balanced',loss='hinge', random_state=rand_num)
            clf.fit(X_features, y_train)
            fold_count += 1
            top_count = 0
            logger.debug("Start testing")
            test_group = group[test_index]
            test_case = set(test_group)

            for case in test_case:
                test_idx = [np.where(test_group==case)]
                #print(X_test.shape)
                x_case_test = X_test[test_idx][0][0]
                y_case_test = y_test[test_idx][0][0]

                score = []
                X_test_feature = x_case_test
                #print(X_test_feature.shape)
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
        logger.debug("Parameter C: %f, Top 1 acc: %f", param[0], acc/param_fold)
    max_acc = max(param_acc)
    max_index = [ i for i,v in enumerate(param_acc) if v==max_acc ]

    best_param = []
    if len(max_index) == 1:
        best_param = tuning_set[max_index[0]]
    else:
        max_params = np.array(tuning_set)[max_index]
        index = np.argmin(max_params[:,0])
        best_param = list(max_params[index])
    logger.info("Best parameter C: %f, Top 1 acc: %f", best_param[0], max_acc)

    return best_param

def classify_test(train, test, path, config_data):
    default_value = get_feature_default(train)
    set_default(train, default_value)
    set_default(test, default_value)

    pedia = classify(train, test, path, config_data)

    return pedia

def classify_cv(data, path, config_data, rand_num):
    sample_names = np.array(list(data.keys()))
    genes = []
    for name in sample_names:
        gene_idx, = np.where(data[name][Data.LABEL_IDX] == 1)
        genes.append(np.array(data[name][Data.GENE_IDX])[gene_idx].tolist()[0])

    #kf = KFold(n_splits=config_data['cv_fold'], shuffle=True, random_state=rand_num)
    kf = GroupKFold(n_splits=config_data['cv_fold'])
    sample_names = np.array(list(data.keys()))

    fold_count = 1
    results = []
    pedia = {}
    param_sets = []
    pool = mp.Pool(processes = config_data['cv_cores'])
    csvfile = open(os.path.join(path, 'cv_group.csv'), 'w')
    csvwriter = csv.writer(csvfile, delimiter=',')
    for train_idx, test_idx in kf.split(sample_names, groups=genes):
        logger.info("Start fold %d", fold_count)
        train_keys = sample_names[train_idx]
        test_keys = sample_names[test_idx]
        for key in test_keys:
            csvwriter.writerow([key, fold_count])

        train = {key:data[key] for key in train_keys}
        test = {key:data[key] for key in test_keys}

        default_value = get_feature_default(train)
        set_default(train, default_value)
        set_default(test, default_value)
        param_sets.append([train, test, path, config_data, fold_count, rand_num])
        fold_count += 1
    csvfile.close()

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

def classify_loocv(data, path, config_data, rand_num):
    sample_names = np.array(list(data.keys()))
    genes = []
    for name in sample_names:
        gene_idx, = np.where(data[name][Data.LABEL_IDX] == 1)
        genes.append(np.array(data[name][Data.GENE_IDX])[gene_idx].tolist()[0])

    logo = LeaveOneGroupOut()
    fold_count = 1
    pedia = {}

    pool = mp.Pool(processes = config_data['cv_cores'])
    param_sets = []
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

        param_sets.append([train, test, path, config_data, fold_count, rand_num])
        fold_count += 1

        writer.writerow([np.array(genes)[test_idx][0], test_keys.tolist()])
    results = [pool.apply_async(classify, args=(p)) for p in param_sets]
    for result in results:
        pedia.update(result.get())
    return pedia

def get_feature_default(data):
    features_default = []
    feature_dim = next(iter(data.values()))[Data.FEATURE_IDX].shape[1]
    for index in range(feature_dim):
        feature_value = np.concatenate([data[case][Data.FEATURE_IDX][:, index] for case in data], axis=0)
        #m = round(np.nanmin(feature_value.astype(np.float)), 10)
        m = 0.0
        features_default.append(m)
    return features_default

def set_default(data, features_default):
    feature_dim = len(features_default)
    for index in range(feature_dim):
        for case in data:
            f_data = data[case][Data.FEATURE_IDX]
            f_data[f_data[:, index] == 'nan', index] = features_default[index]


