# -*- coding: utf-8 -*-
import os
import numpy as np
import sys
import logging
import csv


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
            score = row["gestalt_score"]
            if score == 'nan':
                #continue
                score = 0

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
    #print(all_cases_gene['34223']) 
    total = 0
    top10 = 0
    for case in all_cases_score:
        scores = all_cases_score[case]
        labels = np.array(all_cases_label[case])
        genes = np.array(all_cases_gene[case])
        x = sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)
        #for i in range(len(scores)):
        #    print(str(i + 1) + ": " + genes[x][i] + " - " + str(np.array(scores)[x][i]))
        #print(np.array(arrayscores)[x])
        label = list(labels[x]).index('1')
        #print(label)
        total += 1
        if label < 10:
            top10 += 1
    print(top10/total)
