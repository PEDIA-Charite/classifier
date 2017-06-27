# -*- coding: utf-8 -*-
import os
import warnings
import numpy as np
import sys
import logging
import csv

logging.basicConfig(filename='run.log', level=logging.INFO)
logger = logging.getLogger(__name__)


def rank(pedia, lab, path):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # lab is the label of the plot

    print('ranking results based on', lab)

    # a list that will contain lists of the IDs of each case and the rank of the respective pathogenic
    # variant, ranked by the pedia-score
    combined_rank = []
    #n_cases = len(self.casedisgene)

    combined_performance = []
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

        print("Total:"+str(len(pedia)))
        print('Over 100:'+str(len(over_100)))

                # the absolute number is divided by the total number of cases, so that one has the
                # fraction of cases having a patho rank not higher than i
                # appends sens to i, so that combined rank is a list of floats, each float describing
                # the fraction of cases that have a pathorank lower or eqaul to its index
                #combined_performance.append(sens)

    tmp = 0

    filename = path + '/rank_' + lab + ".csv"
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        rank = 1
        for count in counts:
            writer.writerow([rank, count])
            rank += 1
            tmp += count
            combined_performance.append(tmp / total)

