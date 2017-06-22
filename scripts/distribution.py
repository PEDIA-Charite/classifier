import csv
import sys
import os
import matplotlib
matplotlib.use('pdf')
import math
from matplotlib import pyplot
import numpy as np

# input file is the csv file which is generated from jsonToTable.py
input_file = sys.argv[1]
output_dir = "../output/distribution/" + sys.argv[2] + "/"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

total_gene = []
path_gene = {}
data = {}
g_scores = []
f_scores = []
p_scores = []
b_scores = []
c_scores = []
g_p_scores = []
f_p_scores = []
p_p_scores = []
b_p_scores = []
c_p_scores = []
score_list = []
p_score_list = []

with open(input_file) as csvfile:
    reader = csv.DictReader(csvfile)
    case = ""
    for row in reader:
        case = row["case"]
        score = row["gestalt_score"]
        if score == 'nan':
            score = -1
        else:
            g_scores.append(float(score))
        score = row["feature_score"]
        if score == 'nan':
            score = -1
        else:
            f_scores.append(float(score))
        score = row["cadd_phred_score"]
        if score == 'nan':
            score = -1
        else:
            c_scores.append(float(score))
        score = row["boqa_score"]
        if score == 'nan':
            score = -1
        else:
            b_scores.append(float(score))
        score = row["pheno_score"]
        if score == 'nan':
            score = -1
        else:
            p_scores.append(float(score))

        if int(row["label"]) == 1:
            score = row["gestalt_score"]
            if score == 'nan':
                score = -1
            else:
                g_p_scores.append(float(score))
            score = row["feature_score"]
            if score == 'nan':
                score = -1
            else:
                f_p_scores.append(float(score))
            score = row["cadd_phred_score"]
            if score == 'nan':
                score = -1
            else:
                c_p_scores.append(float(score))
            score = row["boqa_score"]
            if score == 'nan':
                score = -1
            else:
                b_p_scores.append(float(score))
            score = row["pheno_score"]
            if score == 'nan':
                score = -1
            else:
                p_p_scores.append(float(score))

score_list.append(g_scores)
score_list.append(f_scores)
score_list.append(c_scores)
score_list.append(b_scores)
score_list.append(p_scores)
p_score_list.append(g_p_scores)
p_score_list.append(f_p_scores)
p_score_list.append(c_p_scores)
p_score_list.append(b_p_scores)
p_score_list.append(p_p_scores)

x_idx = np.arange(-1.0,1.1,0.05).tolist()

for i, idx in enumerate(x_idx):
    x_idx[i] = round(x_idx[i], 2)
y_value_list = []
for list_idx in range(5):
    y_value = []
    for idx, x in enumerate(x_idx):
        if idx == len(x_idx) - 1:
            break
        count = 0
        for score in score_list[list_idx]:
            if score >= x and score < x_idx[idx+1] and score != -1:
                count += 1
        y_value.append(count)
    y_value.append(0)
    y_value_list.append(y_value)

color_list = ['#ffa347','#0064c8','#b42222','#22a5b4','#b47c22','#6db6ff']
file_names = ['gestalt', 'FM', 'cadd', 'boqa', 'pheno']
pyplot.figure(figsize=(8, 6))

marker_type = ['o', 'v', 's']

for idx, name in enumerate(file_names):
    if idx == 2:
        bin_array = np.arange(math.floor(min(score_list[idx])), math.ceil(max(score_list[idx]))+10, 1).tolist()
    else:
        bin_array = np.arange(math.floor(min(score_list[idx])*10)/10, math.ceil(max(score_list[idx]))+0.1, 0.05).tolist()
    for i, j in enumerate(bin_array):
        bin_array[i] = round(bin_array[i], 2)

    n, bins, patches = pyplot.hist(score_list[idx], bin_array, alpha=0.6, color=color_list[0], label = 'All', edgecolor='black')
    n, bins, patches = pyplot.hist(p_score_list[idx], bin_array, alpha=0.6, color=color_list[1], label = 'Pathogenic', edgecolor='black')

    pyplot.gca().set_yscale("log")
    pyplot.grid(True)
    pyplot.legend()
    pyplot.legend(loc = 2, prop = {'size':12})
    pyplot.xlabel('Value', fontsize = 18)
    pyplot.ylabel('Counts', fontsize = 18)
    pyplot.title('Distribution of ' + name + " score", fontsize=18)
    pyplot.savefig(output_dir + 'dist_' + name + '.png', dpi = 180)
    pyplot.close()
