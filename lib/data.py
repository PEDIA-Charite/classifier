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
    CADA_IDX = 5
    LIRICAL_IDX = 6
    XRARE_IDX = 7
    EXOME_IDX = 8
    AMELIE_IDX = 9

    # FEATURE_IDX is for feature vector which contain the above feature score
    # LABEL_IDX is for pathogenic gene label (0, 1)
    # GENE_IDX is for gene symbol
    FEATURE_IDX = 0
    LABEL_IDX = 1
    GENE_IDX = 2
    GENE_NAME_IDX = 3

    def __init__(self):
        self.data = {}
        # Filter dict
        self.filter_dict = {0: "feature_score", 1: "cadd_score", 2: "gestalt_score",
                            3: "boqa_score", 4: "pheno_score", 5: "cada_score",
                            6: "lirical_score", 7: "xrare_score", 8: "exomizer_score", 9: "amelie_score"
                            }

    def loadData(self, input_file, filter_field=None):
        filter_cases = []

        with open(input_file) as csvfile:
            reader = csv.DictReader(csvfile)
            case = ""
            for row in reader:
                case = row["case"]
                if not case in self.data:
                    self.data.update({case:[[], [], [], []]})
                x = self.data[case][self.FEATURE_IDX]
                y = self.data[case][self.LABEL_IDX]
                gene = self.data[case][self.GENE_IDX]
                gene_name = self.data[case][self.GENE_NAME_IDX]

                x.append([row["feature_score"], row["cadd_score"], row["gestalt_score"],
                          row["boqa_score"], row["pheno_score"], row["cada_score"],
                          row["lirical_score"], row["xrare_score"], row["exomizer_score"],
                          row["amelie_score"]
                ])
                y.append(int(row["label"]))
                gene.append(row["gene_id"])
                gene_name.append(row["gene_symbol"])
                # filter the sample which has no the feature we assigned
                if filter_field != None:
                    if int(row["label"]) == 1 and 'train' in input_file:
                        if row[self.filter_dict[filter_field[0]]] == 'nan' or row[self.filter_dict[filter_field[0]]] == '0':
                            logger.debug("%s - %s has no %s score", case, row["gene_symbol"], self.filter_dict[filter_field[0]])
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

