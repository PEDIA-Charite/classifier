# -*- coding: utf-8 -*-
import os
import warnings
import numpy as np
import sys
import logging
import csv
import pandas as pd
from lib.constants import *
from collections import Counter

# Setup logging
logger = logging.getLogger(__name__)
console_handle = logging.StreamHandler()
console_handle.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
console_handle.setFormatter(formatter)
logger.addHandler(console_handle)

def rank(pedia, path, fold=None, config_data=None):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # lab is the label of the plot

    mute_flag = False

    if config_data:
        mute_flag = True if config_data['param_test'] else False

    unknown = False
    # will evalute ranks in range 0 to 200)
    counts = []
    if fold:
        filename = os.path.join(path, "rank_%s.csv" % fold)
    else:
        filename = os.path.join(path, "rank.csv")

    total = len(pedia)
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        cases = []
        for case in pedia:
            rank_list = pedia[case].index[pedia[case]['label'] == 1].tolist()
            df = pedia[case]
            df['rank'] = df['pedia_score'].rank(method='max',ascending=False)
            rank_list = df.loc[df['label'] == 1, 'rank']
            #rank_list = pedia[case].index[pedia[case]['label'] == 1].tolist()
            if len(rank_list) == 0:
                continue
            rank = int((rank_list.tolist())[0])
            cases.append(case)
            writer.writerow([case, rank])
            counts.append(rank)
        if not mute_flag:
            logger.info("Total: %d", len(pedia))

    tmp = 0

    if fold:
        filename = os.path.join(path, "count_%s.csv" % fold)
    else:
        filename = os.path.join(path, "count.csv")
    total_counts = Counter(counts)
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        rank = 1
        max_count = max(max(total_counts), 11) if total_counts else 11
        for i in range(1, max_count + 1):
            writer.writerow([rank, total_counts[i]])
            tmp += total_counts[i]
            if not mute_flag:
                if rank == 1:
                    logger.info('Rank 1: %d', total_counts[i])
                if rank == 10:
                    logger.info('Rank 2-10: %d', tmp-total_counts[1])
            rank += 1

def rank_all_cv(lab, path, repetition):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # lab is the label of the plot

    logger.debug('ranking results based on %s', lab)

    tmp = 0
    total = []
    total_df = []
    max_row = 0
    for idx in range(repetition):
        filename = path + '/cv_' + str(idx) + '/count.csv'
        data = pd.read_csv(filename, header=None)
        total_df.append(data)
        if data.shape[0] > max_row:
            max_row = data.shape[0]
    x = np.zeros(max_row)
    df = pd.DataFrame(x)
    for i in range(0, repetition):
        df[0] = df[0] + total_df[i][1]

    total = df[0]
    avg = [x / repetition for x in total]
    filename = path + '/count.csv'
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        rank = 1
        tmp = 0
        for value in avg:
            writer.writerow([rank, value])
            tmp += value
            if rank == 1:
                logger.info('Rank 1: %f', tmp)
            if rank == 10:
                logger.info('Rank 2-10: %f', tmp-avg[0])
            rank += 1

def rank_tuning(lab, path, config_data):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # lab is the label of the plot

    logger.debug('ranking results based on %s', lab)

    tmp_path = path
    tuning_set = []
    for g in PARAM_G:
        for c in PARAM_C:
            tuning_set.append([g, c])
    for c, c_value in enumerate(tuning_set):
        counts = []
        total = []
        for idx in range(100):
            total.append(0)
        total_sample_row = []
        for fold in range(config_data['cv_fold']):
            fold = str(fold + 1)
            # will evalute ranks in range 0 to 101)
            path = os.path.join(tmp_path, 'param_' + str(c))
            tmp = 0
            filename = path + '/rank_' + fold + ".csv"
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                count = 0
                rank = []
                for row in reader:
                    total[count] += int(row[1])
                    count += 1
                tmp = 0

            filename = path + '/rank_gene_' + fold + ".csv"
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    total_sample_row.append(row)

        path = os.path.join(tmp_path, 'param_' + str(c))
        tmp = 0
        final_row = sorted(total_sample_row, key = lambda x: int(x[1]))
        filename = path + '/rank_gene.csv'
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            rank = 1
            for row in final_row:
                writer.writerow(row)

        filename = path + '/rank.csv'
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            rank = 1
            top_1 = 0
            for count in total:
                writer.writerow([rank, count])
                tmp += count
                if rank == 1:
                    logger.info('Rank 1: %f', tmp)
                    top_1 = tmp
                if rank == 10:
                    logger.info('Rank 2-10: %f', tmp-top_1)
                rank += 1

def rank_all_cv_tuning(lab, path, repetition):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # lab is the label of the plot

    logger.debug('ranking results based on %s', lab)

    for c, c_value in enumerate(PARAM_C):
        tmp = 0
        total = []
        for idx in range(100):
            total.append(0)
        for idx in range(repetition):
            filename = path + '/cv_' + str(idx) + '/param_' + str(c) + '/rank.csv'
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile)
                count = 0
                rank = []
                for row in reader:
                    total[count] += int(row[1])
                    count += 1


        avg = [x / repetition for x in total]
        filename = path + '/rank_param_' + str(c) + ".csv"
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            rank = 1
            tmp = 0
            for value in avg:
                writer.writerow([rank, value])
                tmp += value
                if rank == 1:
                    logger.info('Rank 1: %f', tmp)
                if rank == 10:
                    logger.info('Rank 2-10: %f', tmp-avg[0])
                rank += 1

