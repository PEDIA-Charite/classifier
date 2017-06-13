import json, os
import warnings
import numpy as np
import sys
import logging
import csv
from matplotlib import pyplot as plt
from sklearn import svm
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib
from sample import Sample

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.basicConfig(filename='run.log', level=logging.INFO)
logger = logging.getLogger(__name__)

class Data:
    """Common class for a list of instances of the class Samples

    Attributes:
        name: name of the data as a string
        samples: a list of samples as instances of class Sample
        casedisgene: a list of lists [[case,gene]] containing each case in samples and the respective disease causing gene
    """


    def __init__(self, samples=[], casedisgene=[]):
        self.data = {}

        self.casedisgene = casedisgene

    def loadData(self, input_file, filter_field=None):

        filter_cases = []

        with open(input_file) as csvfile:
            reader = csv.DictReader(csvfile)
            case = ""
            for row in reader:
                case = row["case"]
                if not case in self.data:
                    self.data.update({case:[[], [], []]})
                x = self.data[case][0]
                y = self.data[case][1]
                gene = self.data[case][2]

                x.append([row["feature_score"], row["cadd_phred_score"], row["gestalt_score"], row["boqa_score"], row["pheno_score"]])
                y.append(int(row["label"]))
                gene.append(row["gene_symbol"])

                # filter the sample which has no the feature we assigned
                if filter_field != None:
                    if int(row["label"]) == 1:
                        if row[filter_field] == 'nan':
                            logger.info("%s - %s has no %s score", case, row["gene_symbol"], filter_field)
                            filter_cases.append(case)

            for key in list(self.data):
                if key in filter_cases:
                    del self.data[key]
                else:
                    x = self.data[key][0]
                    y = self.data[key][1]

                    x = np.array(x)
                    y = np.array(y)

                    self.data[key][0] = x
                    self.data[key][1] = y

            logger.info("Input %s: total %d cases", input_file, len(self.data))

    def getFeatureMin(self):
        features_min = []
        feature_dim = next(iter(self.data.values()))[0].shape[1]
        for index in range(feature_dim):
            feature_value = np.concatenate([self.data[case][0][:, index] for case in self.data], axis=0)
            m = np.nanmin(feature_value.astype(np.float))
            features_min.append(m)

        return features_min

    def preproc(self, features_min):
        feature_dim = len(features_min)
        for index in range(feature_dim):
            for case in self.data:
                data = self.data[case][0]
                data[data[:, index] == 'nan', index] = features_min[index]


