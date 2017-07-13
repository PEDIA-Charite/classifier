# -*- coding: utf-8 -*-
import os
import warnings
import numpy as np
import sys
import logging
import csv

# Setup logging
logger = logging.getLogger(__name__)
console_handle = logging.StreamHandler()
console_handle.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
console_handle.setFormatter(formatter)
logger.addHandler(console_handle)

def rank(pedia, lab, path):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # lab is the label of the plot

    logger.debug('ranking results based on %s', lab)

    # will evalute ranks in range 0 to 101)
    counts = []
    filename = path + '/rank_gene_' + lab + ".csv"
    total = len(pedia)
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        cases = []
        for i in range(99):
            count = 0
            for case in pedia:
                if pedia[case][1][i] == 1:
                    count += 1
                    cases.append(case)
                    writer.writerow([case, i])
            counts.append(count)
        over_100 = {key: pedia[key] for key in pedia if key not in cases}
        for key in over_100.keys():
            writer.writerow([key, 99])
        counts.append(len(over_100))

        logger.info("Total: %d", len(pedia))

    tmp = 0

    filename = path + '/rank_' + lab + ".csv"
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        rank = 1
        for count in counts:
            writer.writerow([rank, count])
            tmp += count
            if rank == 1:
                logger.info('Rank 1: %d', count)
            if rank == 10:
                logger.info('Rank 2-10: %d', tmp-counts[0])
            rank += 1

def rank_all_cv(lab, path, repetition):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # lab is the label of the plot

    logger.debug('ranking results based on %s', lab)

    tmp = 0
    total = []
    for idx in range(100):
        total.append(0)
    for idx in range(repetition):
        filename = path + '/cv_' + str(idx) + '/rank_' + lab + ".csv"
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            count = 0
            rank = []
            for row in reader:
                total[count] += int(row[1])
                count += 1


    avg = [x / repetition for x in total]
    filename = path + '/rank_' + lab + ".csv"
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

