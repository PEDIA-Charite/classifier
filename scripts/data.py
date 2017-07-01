# -*- coding: utf-8 -*-
import os
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

class Data:
    """Common class for a list of instances of the class Samples

    Attributes:
        name: name of the data as a string
        samples: a list of samples as instances of class Sample
        casedisgene: a list of lists [[case,gene]] containing each case in samples and the respective disease causing gene
    """

    # index for each score
    FM_IDX = 0
    CADD_IDX = 1
    GESTALT_IDX = 2
    BOQA_IDX = 3
    PHENO_IDX = 4


    # FEATURE_IDX is for feature vector which contain the above feature score
    # LABEL_IDX is for pathogenic gene label (0, 1)
    # GENE_IDX is for gene symbol
    FEATURE_IDX = 0
    LABEL_IDX = 1
    GENE_IDX = 2

    def __init__(self):
        self.data = {}

    def loadData(self, input_file, filter_field=None):
        filter_cases = []

        with open(input_file) as csvfile:
            reader = csv.DictReader(csvfile)
            case = ""
            for row in reader:
                case = row["case"]
                if not case in self.data:
                    self.data.update({case:[[], [], []]})
                x = self.data[case][self.FEATURE_IDX]
                y = self.data[case][self.LABEL_IDX]
                gene = self.data[case][self.GENE_IDX]

                x.append([row["feature_score"], row["cadd_phred_score"], row["gestalt_score"], row["boqa_score"], row["pheno_score"]])
                y.append(int(row["label"]))
                gene.append(row["gene_symbol"])

                # filter the sample which has no the feature we assigned
                if filter_field != None:
                    if int(row["label"]) == 1:
                        if row[filter_field] == 'nan':
                            logger.debug("%s - %s has no %s score", case, row["gene_symbol"], filter_field)
                            filter_cases.append(case)

            for key in list(self.data):
                if key in filter_cases:
                    del self.data[key]
                else:
                    x = self.data[key][self.FEATURE_IDX]
                    y = self.data[key][self.LABEL_IDX]

                    x = np.array(x)
                    y = np.array(y)

                    self.data[key][self.FEATURE_IDX] = x
                    self.data[key][self.LABEL_IDX] = y

            logger.info("Input %s: total %d cases", input_file, len(self.data))

    def getFeatureDefault(self):
        features_default = []
        feature_dim = next(iter(self.data.values()))[self.FEATURE_IDX].shape[1]
        for index in range(feature_dim):
            feature_value = np.concatenate([self.data[case][self.FEATURE_IDX][:, index] for case in self.data], axis=0)
            m = np.nanmin(feature_value.astype(np.float))
            features_default.append(m)

        return features_default

    def preproc(self, features_default):
        feature_dim = len(features_default)
        for index in range(feature_dim):
            for case in self.data:
                data = self.data[case][self.FEATURE_IDX]
                data[data[:, index] == 'nan', index] = features_default[index]

