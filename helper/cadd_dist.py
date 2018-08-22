# -*- coding: utf-8 -*-
import os
import numpy as np
import sys
import logging
import csv
import matplotlib.pyplot as plt


tar = [28827, 62094, 62286, 65213, 66443, 73413, 46073, 62099, 65183, 65229, 66964, 96824]
backs = ['1KG']
for back in backs:
    input_file = "output/cv_g/CV_" + back + "/train.csv"
    count_all = []
     
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile)
        case = ""
        count = 0
        gene_all = []
        patho_score = []
        normal_score = []
        for row in reader:
            tmp_case = row["case"]
            gene = row["gene_symbol"]
            label = row["label"]
            score = row["cadd_phred_score"]
            if label == '1' and score == 'nan':
                print(tmp_case + " - " + gene)
            if score == 'nan':
                score = -1
                #continue
            score = float(score)
            if gene in gene_all and tmp_case == case:
                print(gene)
            if label == '1':
                patho_score.append(score)
            else:
                normal_score.append(score)

    data = [np.array(patho_score), np.array(normal_score)]
    # Create a figure instance
    fig = plt.figure(1, figsize=(9, 6))
    
    # Create an axes instance
    ax = fig.add_subplot(111)
    
    # Create the boxplot
    #bp = ax.boxplot(data)
   
    ## add patch_artist=True option to ax.boxplot() 
    ## to get fill color
    bp = ax.boxplot(data, patch_artist=True)
    plt.xticks([1, 2], ['Pathogenicity', 'Non-Pathogenicity']) 
    ## change outline color, fill color and linewidth of the boxes
    for box in bp['boxes']:
        # change outline color
        box.set( color='#7570b3', linewidth=2)
        # change fill color
        box.set( facecolor = '#1b9e77' )
    
    ## change color and linewidth of the whiskers
    for whisker in bp['whiskers']:
        whisker.set(color='#7570b3', linewidth=2)
    
    ## change color and linewidth of the caps
    for cap in bp['caps']:
        cap.set(color='#7570b3', linewidth=2)
    
    ## change color and linewidth of the medians
    for median in bp['medians']:
        median.set(color='#b2df8a', linewidth=2)
    
    ## change the style of fliers and their fill
    for flier in bp['fliers']:
        flier.set(marker='o', color='#e7298a', alpha=0.2)
    # Save the figure
    fig.savefig('fig1.png', bbox_inches='tight')
    #print(all_cases_gene['204233']) 
    #scores = all_cases_score['204233']
    #labels = np.array(all_cases_label['204233'])
    #genes = np.array(all_cases_gene['204233'])
    #x = sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)
    #for i in range(len(scores)):
    #    print(str(i + 1) + ": " + genes[x][i] + " - " + str(np.array(scores)[x][i]))
    ##print(np.array(arrayscores)[x])
    #label = list(labels[x]).index('1')
    #print(label)
