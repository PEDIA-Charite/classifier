# -*- coding: utf-8 -*-
import os
import numpy as np
import sys
import logging
import csv
from statistics import mean 


tar = [28827, 62094, 62286, 65213, 66443, 73413, 46073, 62099, 65183, 65229, 66964, 96824]
backs = ['1KG']
for back in backs:
    input_file = "../output/cv_g/CV_" + back + "/train.csv"
    count_all = []
     
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)
        case = ""
        count = 0
        gene_all = []
        all_cases_gene = {}
        all_cases_label = {}
        all_cases_score = {}
        for row in reader:
            tmp_case = row["case"]
            gene = row["gene_symbol"]
            label = row["label"]
            score = row["cadd_phred_score"]
            #if score == 'nan':
            #    continue
            score = float(score)
            if gene in gene_all and tmp_case == case:
                print(gene)
            if tmp_case in all_cases_gene:
                all_cases_gene[tmp_case].append(gene)
                all_cases_label[tmp_case].append(label)
                all_cases_score[tmp_case].append(score)
            else:
                all_cases_gene.update({tmp_case:[gene]})
                all_cases_label.update({tmp_case:[label]})
                all_cases_score.update({tmp_case:[score]})
    count = [len(all_cases_gene[x]) for x in all_cases_gene]
    print(mean(count))
