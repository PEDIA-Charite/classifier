# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 09:56:23 2017

@author: Martin
"""

import json, os
import warnings
import numpy as np
import sys
import csv
import argparse
from data import Data
from classifier import *
from draw import *
from time import gmtime, strftime
from json_to_table import parse_json

def main():

    # Mode
    TEST_MODE = 0
    CV_MODE = 1
    LOOCV_MODE = 2

    # Parse input arguments
    parser = argparse.ArgumentParser(description='Run classifier to get PEDIA score')
    parser.add_argument('Train_path', help='path of training data')
    parser.add_argument('Train_label', help='label of Training data')
    parser.add_argument('-t', '--test', help='path of testing data')
    parser.add_argument('-o', '--output', default=".", help='Path of output')
    parser.add_argument('-c', '--cv', type=int, help='Enable k-fold cross validation. Default 10-fold')
    parser.add_argument('-l', '--loocv', action='store_true', help='Enable group leave one out cross validation')
    parser.add_argument('-e', '--exclude', help='Exclude specific feature. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use ; to separate them.')

    args = parser.parse_args()
    train_path = args.Train_path
    train_label = args.Train_label
    output_path = args.output
    train_file = output_path + "/train.csv"
    test_file = output_path + "/test.csv"
    test_path = None

    mode = TEST_MODE

    if args.cv is not None:
        fold = args.cv
        mode = CV_MODE
        print("CV: ", fold)
    elif args.loocv:
        mode = LOOCV_MODE
        print("LOOCV")
    else:
        test_path = args.test
        mode = TEST_MODE
        if test_path == None:
            sys.stderr.write('Error: Please provide testing data path with --test, if you are not using cross validation.\n')
            parser.print_help()
            sys.exit(1)

    if args.exclude is not None:
        filter_feature = list(map(int, args.exclude.split("_")))
    else:
        filter_feature = None

    # Create output folder if not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Create file for saving command
    fp = open(output_path + "/run.log", 'w')
    fp.write("Time:" + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "\n")
    fp.write("Command:" + str(args) + "\n")
    fp.write("Input directory:" + train_path + "\n")
    fp.write("Output directory:" + output_path + "\n")
    fp.write("Exclude features:" + str(filter_feature) + "\n")
    fp.close()

    # Parse json files from Training folder and Testing folder
    parse_json(train_path, train_file)

    if mode == TEST_MODE:
        parse_json(test_path, test_file)

    # Load training data and testing data
    train_data = Data()
    train_data.loadData(train_file, 'gestalt_score')

    # Get min value of each feature then apply to missing value
    features_default = train_data.getFeatureDefault()
    train_data.preproc(features_default)
    train = train_data.data

    # Train classifier by training set and test on testing set
    # Return pedia which contain pedia score, label and gene id
    # We can add filter_feature to remove the feature we don't want
    # to be trained by the classifier. For example
    # filter_feature = [FM_IDX, GESTALT_IDX]
    if mode == TEST_MODE:
        test_data = Data()
        test_data.loadData(test_file, 'gestalt_score')
        test_data.preproc(features_default)
        test = test_data.data
        pedia = classify(train, test, output_path, filter_feature)
    elif mode == LOOCV_MODE:
        pedia = classify_loocv(train, output_path, filter_feature)
    else:
        pedia = classify_cv(train, output_path, fold, filter_feature)


    # draw manhattan plot
    for case in pedia:
        manhattan(pedia, output_path, case)

    rank(pedia, 'red', train_label, output_path)

if __name__ == '__main__':
    main()


