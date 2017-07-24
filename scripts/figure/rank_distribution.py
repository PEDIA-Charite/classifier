import csv
import sys
import os
import matplotlib
matplotlib.use('pdf')
import math
from matplotlib import pyplot
import numpy as np
from scipy.stats import rankdata


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


# input file is the csv file which is generated from jsonToTable.py
input_file = sys.argv[1]
output_dir = "../../output/rank_distribution/" + sys.argv[2] + "/"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

data = {}
with open(input_file) as csvfile:
    reader = csv.DictReader(csvfile)
    case = ""

    for row in reader:
        case = row["case"]
        if not case in data:
            data.update({case:[[], [], []]})
        x = data[case][FEATURE_IDX]
        y = data[case][LABEL_IDX]
        gene = data[case][GENE_IDX]

        feature_vector = [row["feature_score"], row["cadd_phred_score"], row["gestalt_score"], row["boqa_score"], row["pheno_score"]]
        for idx, value in enumerate(feature_vector):
            if value == 'nan':
                feature_vector[idx] = -1
        x.append(feature_vector)

        y.append(int(row["label"]))
        gene.append(row["gene_symbol"])

score_list = []
p_score_list = []
for key in list(data):
    x = data[key][FEATURE_IDX]
    y = data[key][LABEL_IDX]

    x = np.array(x)
    x = x.astype(float)
    y = np.array(y)
    y = y.astype(int)
    for idx in range(5):
        length = len(x)
        score = x[:, idx]
        rank =  rankdata(score, method='min')
        #rank = rankdata(score)
        x[:, idx] = rank / max(rank)

    data[key][FEATURE_IDX] = x
    data[key][LABEL_IDX] = y

for idx in range(5):
    scores = []
    p_scores = []
    for key in list(data):
        x = data[key][FEATURE_IDX][:, idx]
        min_x = min(x)
        min_idx = x == min_x
        x = x[-min_idx]
        y = data[key][LABEL_IDX]
        y = y[-min_idx]
        for gene_idx, gene_score in enumerate(x):
            if y[gene_idx] == 1:
                p_scores.append(gene_score)
            else:
                scores.append(gene_score)
    score_list.append(scores)
    p_score_list.append(p_scores)

color_list = ['#ffa347','#0064c8','#b42222','#22a5b4','#b47c22','#6db6ff']
file_names = ['FM', 'cadd', 'gestalt', 'boqa', 'pheno']
pyplot.figure(figsize=(8, 6))

marker_type = ['o', 'v', 's']

for idx, name in enumerate(file_names):
    bin_array = np.arange(math.floor(min(score_list[idx])*10)/10, math.ceil(max(p_score_list[idx]))+0.1, 0.05).tolist()
    for bin_idx, value in enumerate(bin_array):
        bin_array[bin_idx] = round(value, 2)
    n, bins, patches = pyplot.hist(score_list[idx], bin_array, alpha=0.6, color=color_list[0], label = 'All', edgecolor='black')
    n, bins, patches = pyplot.hist(p_score_list[idx], bin_array, alpha=0.6, color=color_list[1], label = 'Pathogenic', edgecolor='black')

    pyplot.gca().set_yscale("log")
    pyplot.grid(True)
    pyplot.legend()
    pyplot.legend(loc = 2, prop = {'size':12})
    pyplot.xlabel('Rank', fontsize = 18)
    pyplot.ylabel('Counts', fontsize = 18)
    pyplot.title('Distribution of ' + name + " score", fontsize=18)
    pyplot.savefig(output_dir + 'dist_' + name + '.png', dpi = 180)
    pyplot.close()
