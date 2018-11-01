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
from lib.data import Data
from lib.classifier import *
from lib.json_to_table import parse_json
from lib.json_to_table import parse_json_stdin
from lib.rank import *
from lib.version import __version__
from lib.constants import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def parse_arguments(parser):
    # Parse input arguments
    parser.add_argument('Train_path', help='path of training data')
    parser.add_argument('Train_label', help='label of Training data')
    parser.add_argument('-t', '--test', help='path of testing data')
    parser.add_argument('-o', '--output', default=".", help='Path of output')
    parser.add_argument('-c', '--cv', type=int, help='Enable k-fold cross validation. Default 10-fold')
    parser.add_argument('-l', '--loocv', action='store_true', help='Enable group leave one out cross validation')
    parser.add_argument('-e', '--exclude', help='Exclude specific feature. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use _ to separate them.')
    parser.add_argument('-g', '--graph', help='Enable manhattan plot and the path to geneposition file')
    parser.add_argument('-s', '--server', action='store_true', help='Enable server mode')
    parser.add_argument('-p', '--param-tuning-fold', type=int, help='Enable parameter tuning mode')
    parser.add_argument('-f', '--filter_feature', help='Filter sample without specific feature. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use _ to separate them.')
    parser.add_argument('-k', '--kernel', default="linear", help='Kernel of SVM, default: linear')
    parser.add_argument('--param-c', type=float, default=1, help='Parameter C of SVM, default: 1')
    parser.add_argument('--param-g', type=float, default=0.25, help='Parameter G of SVM, default: 0.25')
    parser.add_argument('--param-test', action='store_true', help='Enable parameter testing mode')
    parser.add_argument('--cv-rep', type=int, default=10, help='Repitiotion of k-fold CV experiment, default 10')
    parser.add_argument('--cv-cores', type=int, default=5, help='Cores using in cross validation, default 5')

    return parser.parse_args()

def setup_config():
    parser = argparse.ArgumentParser(description='Run classifier to get PEDIA score')
    args = parse_arguments(parser)

    data = {}
    data['train_path'] = args.Train_path
    data['train_label'] = args.Train_label
    data['output_path'] = args.output
    data['train_file'] = os.path.join(args.output, "train.csv")
    data['test_file'] = os.path.join(args.output, "test.csv")
    data['test_path'] = None
    data['param_fold'] = 0
    data['mode'] = TEST_MODE
    data['graph_mode'] = NO_GRAPH
    data['pos_file'] = args.graph
    data['running_mode'] = NORMAL_MODE
    data['cv_rep'] = args.cv_rep
    data['param_c'] = args.param_c
    data['param_g'] = args.param_g
    data['kernel'] = args.kernel
    data['cv_cores'] = args.cv_cores
    data['param_test'] = args.param_test

    # Create output folder if not exist
    if not os.path.exists(data['output_path']):
        os.makedirs(data['output_path'])

    # Setup logging
    log_file = os.path.join(data['output_path'], 'run.log')
    logging.basicConfig(filename=log_file, format='%(asctime)s: %(name)s - %(message)s', datefmt='%m-%d %H:%M', level=logging.DEBUG, filemode='w')
    console_handle = logging.StreamHandler()
    console_handle.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
    console_handle.setFormatter(formatter)
    logger.addHandler(console_handle)

    logger.info("Start pedia version %s", __version__)

    # Parse mode
    if args.param_test:
        data['cv_fold'] = args.cv
        data['mode'] = PARAM_TEST_MODE
        logger.info("Param test CV: %d", data['cv_fold'])
    elif args.cv is not None:
        data['cv_fold'] = args.cv
        data['mode'] = CV_MODE
        logger.info("CV: %d", data['cv_fold'])
    elif args.loocv:
        data['mode'] = LOOCV_MODE
        logger.info("LOOCV")
    else:
        data['test_path']= args.test
        data['mode'] = TEST_MODE
        if data['test_path'] == None and not args.server:
            logger.error('Error: Please provide testing data path with --test, if you are not using cross validation.\n')
            parser.print_help()
            sys.exit(1)

    # Parse exclude features
    if args.exclude is not None:
        data['exclude_feature'] = list(map(int, args.exclude.split("_")))
    else:
        data['exclude_feature'] = None

    # Parse filter features
    if args.filter_feature is not None:
        data['filter_feature'] = list(map(int, args.filter_feature.split("_")))
    else:
        data['filter_feature'] = None

    # Parse graph mode
    if args.graph:
        data['graph_mode'] = GRAPH

    # Parse running mode
    if args.server:
        data['running_mode'] = SERVER_MODE
    else:
        data['running_mode'] = NORMAL_MODE

    # k-fold param tuning
    if args.param_tuning_fold:
        data['param_fold'] = int(args.param_tuning_fold)

    logger.debug("Command: %s", str(args))
    logger.info("Input directory: %s", data['train_path'])
    logger.info("Output directory: %s", data['output_path'])
    logger.info("Exclude features: %s", str(data['filter_feature']))
    logger.info("Using kernel: %s", str(data['kernel']))

    running_mode_str = "Normal"

    if data['running_mode'] == SERVER_MODE:
        running_mode_str = "Server"
    logger.info("Running mode: %s", running_mode_str)
    param_str = 'Default parameter' if data['param_fold'] == 0 else 'Parameter tuning fold ' + str(data['param_fold'])
    logger.info("%s", param_str)

    return data

def main():

    # Parse input arguments and store in config_data
    config_data = setup_config()

    graph_mode = config_data['graph_mode']
    if graph_mode == GRAPH:
        from lib.draw import draw_rank
        from lib.draw import manhattan
        from lib.draw import manhattan_all

    # Parse json files from Training folder and Testing folder
    logger.info("Parse training json files from %s", config_data['train_path'])
    train_path = config_data['train_path']
    train_file = config_data['train_file']
    train_label = config_data['train_label']
    parse_json(train_path, train_file)


    mode = config_data['mode']
    test_path = config_data['test_path']
    test_file = config_data['test_file']
    running_mode = config_data['running_mode']
    output_path = config_data['output_path']

    if mode == TEST_MODE:
        if running_mode == NORMAL_MODE:
            logger.info("Parse testing json files from %s", test_path)
            parse_json(test_path, test_file)
        else:
            logger.info("Parse testing json file from stdin")
            parse_json_stdin(test_file)

    # Load training data and testing data
    train_data = Data()
    filter_feature = config_data['filter_feature']
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
        pedia = classify_test(train, test, output_path, config_data)

        rank(pedia, train_label, output_path)
        if graph_mode == GRAPH:
            for case in pedia:
                manhattan(pedia, output_path, config_data['pos_file'], case)
            manhattan_all(pedia, output_path, config_data['pos_file'])
            draw_rank('red', train_label, output_path)

    elif mode == LOOCV_MODE:
        ite = 0
        train = train_data.data
        pedia = classify_loocv(train, output_path, config_data, ite+1)

        rank(pedia, train_label, output_path)
        if graph_mode == GRAPH:
            for case in pedia:
                manhattan(pedia, output_path, config_data['pos_file'], case)
            draw_rank('red', train_label, output_path)
    elif mode == PARAM_TEST_MODE:
        for ite in range(config_data['cv_rep']):
            logger.info("Start CV repetition %d", ite+1)
            path = output_path + "/cv_" + str(ite)
            if not os.path.exists(path):
                os.makedirs(path)
            train = train_data.data
            pedia = classify_cv_tuning_test(train, path, config_data)

            rank_tuning(train_label, path, config_data)
            if graph_mode == GRAPH:
                for case in pedia:
                    manhattan(pedia, path, config_data['pos_file'], case)
                manhattan_all(pedia, path, config_data['pos_file'])
                draw_rank('red', train_label, path)
        rank_all_cv_tuning(train_label, output_path, config_data['cv_rep'])
    else:
        for ite in range(config_data['cv_rep']):
            logger.info("Start CV repetition %d", ite+1)
            path = output_path + "/cv_" + str(ite)
            if not os.path.exists(path):
                os.makedirs(path)
            train = train_data.data
            pedia = classify_cv(train, path, config_data, ite+1)

            rank(pedia, train_label, path)
            if graph_mode == GRAPH:
                for case in pedia:
                    manhattan(pedia, path, config_data['pos_file'], case)
                manhattan_all(pedia, path, config_data['pos_file'])
                draw_rank('red', train_label, path)
        rank_all_cv(train_label, output_path, config_data['cv_rep'])


if __name__ == '__main__':
    main()


