import json, os
import warnings
import numpy as np
import sys
from sklearn import svm
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib


warnings.filterwarnings("ignore", category=DeprecationWarning)



class Sample(object):
    """common class for all samples. that is the vector of scores describing a sample and its unique identifier case and gene.

    Attributes:
        case: The ID of the case to which the vector belongs as a string.
        gene: The name of the gene this vector describes as a string.
        gestalt: The gestalt score based on FDNA's analysis of the case's portrait foto as a float.
        feature: The feature score based on FDNA's analysis of the case's annotated symptoms as a float.
        cadd_phred: the highest CADDphred scores of the gene (has passed filtering; otherwise it is 0) as a float
        phenomizer: the phenomizer p-value (*-1) based on the phenomizers analysis of the cases's annotated symptoms in classical mode as a float
        boqa: the phenomizer score based on the phenomizers analyisis of the of the case's annotated symptoms in BOQA mode as a float
        pathogenicity: a class label as an integer: 1 means pathogenic, 0 means neutral
        pedia: an attribute to hold the PEDIA score as a float (initially it is -5)
        extom: an attribute to hold the extom score based on patients symptoms and exome (no biometry)
    """

    def __init__(self, case='?', gene='?', gestalt=0, feature=0, cadd_phred=0, phenomizer=0, boqa=0, pathogenicity=0, pedia=-5, extom=-5):
        self.case = case
        self.gene = gene
        self.gestalt = gestalt
        self.feature = feature
        self.cadd_phred = cadd_phred
        self.phenomizer = phenomizer
        self.boqa = boqa
        self.pathogenicity = pathogenicity
        self.pedia = pedia
        self.extom = extom

    def classify(self):
        """a function to classify a sample using the classifier and the scaler provided in the respective pkl-files
        """
        clf = joblib.load('pedia_classifier.pkl')
        scaler = joblib.load('pedia_scaler.pkl')
        pedia = float(clf.decision_function(scaler.transform(np.array([self.gestalt, self.feature, self.cadd_phred, self.phenomizer, self.boqa]))))
        print(pedia)

