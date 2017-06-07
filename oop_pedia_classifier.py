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

def main():

    # Parse input arguments
    parser = argparse.ArgumentParser(description='Run classifier to get PEDIA score')
    parser.add_argument('Train_path', help='path of training data')
    parser.add_argument('Test_path', help='path of testing data')
    parser.add_argument('Train_label', help='label of Training data')
    parser.add_argument('-o', '--output', default=".", help='Path of output')

    args = parser.parse_args()
    train_path = args.Train_path
    test_path = args.Test_path
    train_label = args.Train_label
    output_path = args.output
    train_file = output_path + "/train.csv"
    test_file = output_path + "/test.csv"

    # Create output folder if not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Parse json files from Training folder and Testing folder
    cmd = "python jsonToTable.py -i " + train_path + " -o " + train_file
    os.system(cmd)

    cmd = "python jsonToTable.py -i " + test_path + " -o " + test_file
    os.system(cmd)

    # Load training data and testing data
    train_data = Data()
    test_data = Data()
    train_data.loadData(train_file)
    test_data.loadData(test_file)

    # Get min value of each feature then apply to missing value
    features_min = train_data.getFeatureMin()
    train_data.preproc(features_min)
    test_data.preproc(features_min)

    # Train classifier by training set and test on testing set
    # Return pedia which contain pedia score, label and gene id
    pedia = classify(train_data, test_data, output_path)

    # draw manhattan plot
    for case in pedia:
        manhattan(pedia, output_path, case)

    rank(pedia, 'red', train_label, output_path)

if __name__ == '__main__':
    main()


