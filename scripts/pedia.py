# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 09:56:23 2017

@author: Martin
"""

import os
import numpy as np
import sys
import csv
import argparse
import logging
from data import Data
from classifier import *
from json_to_table import parse_json
from json_to_table import parse_json_stdin
from rank import *
from version import __version__

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def main():

    # Mode
    TEST_MODE = 0
    CV_MODE = 1
    LOOCV_MODE = 2

    # Graph
    NO_GRAPH = 0
    GRAPH = 1

    # Running Mode
    NORMAL_MODE = 0
    SERVER_MODE = 1

    # CV Repetition
    CV_REPEATE = 10


    # Parse input arguments
    parser = argparse.ArgumentParser(description='Run classifier to get PEDIA score')
    parser.add_argument('Train_path', help='path of training data')
    parser.add_argument('Train_label', help='label of Training data')
    parser.add_argument('-t', '--test', help='path of testing data')
    parser.add_argument('-o', '--output', default=".", help='Path of output')
    parser.add_argument('-c', '--cv', type=int, help='Enable k-fold cross validation. Default 10-fold')
    parser.add_argument('-l', '--loocv', action='store_true', help='Enable group leave one out cross validation')
    parser.add_argument('-e', '--exclude', help='Exclude specific feature. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use _ to separate them.')
    parser.add_argument('-g', '--graph', action='store_true', help='Enable manhattan plot')
    parser.add_argument('-s', '--server', action='store_true', help='Enable server mode')
    parser.add_argument('-p', '--param-tuning-fold', type=int, help='Enable parameter tuning mode')
    parser.add_argument('-f', '--filter_feature', help='Filter sample without specific feature. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use _ to separate them.')

    args = parser.parse_args()
    train_path = args.Train_path
    train_label = args.Train_label
    output_path = args.output
    train_file = output_path + "/train.csv"
    test_file = output_path + "/test.csv"
    test_path = None
    param_fold = 0

    mode = TEST_MODE
    graph_mode = NO_GRAPH
    running_mode = NORMAL_MODE

    # Create output folder if not exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Setup logging
    log_file = output_path + '/run.log'
    logging.basicConfig(filename=log_file, format='%(asctime)s: %(name)s - %(message)s', datefmt='%m-%d %H:%M', level=logging.DEBUG, filemode='w')
    console_handle = logging.StreamHandler()
    console_handle.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
    console_handle.setFormatter(formatter)
    logger.addHandler(console_handle)

    logger.info("Start pedia version %s", __version__)

    if args.cv is not None:
        fold = args.cv
        mode = CV_MODE
        logger.info("CV: %d", fold)
    elif args.loocv:
        mode = LOOCV_MODE
        logger.info("LOOCV")
    else:
        test_path = args.test
        mode = TEST_MODE
        if test_path == None and not args.server:
            logger.error('Error: Please provide testing data path with --test, if you are not using cross validation.\n')
            parser.print_help()
            sys.exit(1)

    if args.exclude is not None:
        exclude_feature = list(map(int, args.exclude.split("_")))
    else:
        exclude_feature = None

    if args.filter_feature is not None:
        filter_feature = list(map(int, args.filter_feature.split("_")))
    else:
        filter_feature = None

    if args.graph:
        graph_mode = GRAPH
        from draw import draw_rank
        from draw import manhattan
        from draw import manhattan_all

    if args.server:
        running_mode = SERVER_MODE
    else:
        running_mode = NORMAL_MODE

    if args.param_tuning_fold:
        param_fold = int(args.param_tuning_fold)

    logger.debug("Command: %s", str(args))
    logger.info("Input directory: %s", train_path)
    logger.info("Output directory: %s", output_path)
    logger.info("Exclude features: %s", str(filter_feature))

    running_mode_str = "Normal"

    if running_mode == SERVER_MODE:
        running_mode_str = "Server"
    logger.info("Running mode: %s", running_mode_str)
    param_str = 'Default parameter' if param_fold == 0 else 'Parameter tuning fold ' + str(param_fold)
    logger.info("%s", param_str)

    # Parse json files from Training folder and Testing folder
    logger.info("Parse training json files from %s", train_path)
    parse_json(train_path, train_file)

    if mode == TEST_MODE:
        if running_mode == NORMAL_MODE:
            logger.info("Parse testing json files from %s", test_path)
            parse_json(test_path, test_file)
        else:
            logger.info("Parse testing json file from stdin")
            parse_json_stdin(test_file)

    # Load training data and testing data
    train_data = Data()
    train_data.loadData(train_file, filter_feature)


    # Train classifier by training set and test on testing set
    # Return pedia which contain pedia score, label and gene id
    # We can add filter_feature to remove the feature we don't want
    # to be trained by the classifier. For example
    # filter_feature = [FM_IDX, GESTALT_IDX]
    if mode == TEST_MODE:
        train = train_data.data

        test_data = Data()
        test_data.loadData(test_file, filter_feature)
        test = test_data.data
        pedia = classify_test(train, test, output_path, running_mode, exclude_feature)

        rank(pedia, train_label, output_path)
        if graph_mode == GRAPH:
            for case in pedia:
                manhattan(pedia, output_path, case)
            manhattan_all(pedia, output_path)
            draw_rank('red', train_label, output_path)

    elif mode == LOOCV_MODE:
        train = train_data.data
        pedia = classify_loocv(train, output_path, running_mode, exclude_feature)

        rank(pedia, train_label, output_path)
        if graph_mode == GRAPH:
            for case in pedia:
                manhattan(pedia, output_path, case)
            draw_rank('red', train_label, output_path)

    else:
        for ite in range(CV_REPEATE):
            logger.info("Start CV repetition %d", ite+1)
            path = output_path + "/cv_" + str(ite)
            if not os.path.exists(path):
                os.makedirs(path)
            train = train_data.data
            pedia = classify_cv(train, path, fold, param_fold, running_mode, exclude_feature)

            rank(pedia, train_label, path)
            if graph_mode == GRAPH:
                for case in pedia:
                    manhattan(pedia, path, case)
                manhattan_all(pedia, path)
                draw_rank('red', train_label, path)
        rank_all_cv(train_label, output_path, CV_REPEATE)


if __name__ == '__main__':
    main()


