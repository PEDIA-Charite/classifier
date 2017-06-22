import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
import collections

# input file is the csv file which is generated from jsonToTable.py
input_file = sys.argv[1]
output_dir = '../../output/heatmap/' + sys.argv[2] + "/"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

total_gene = []
path_gene = {}
data = {}
with open(input_file) as csvfile:
    reader = csv.DictReader(csvfile)
    case = ""
    for row in reader:
        case = row["case"]
        if not case in data:
            data.update({case:{}})

        x = data[case]
        feature = row["gestalt_score"]
        if feature == 'nan':
            feature = 0
        x.update({row["gene_symbol"]:feature})
        if int(row["label"]) == 1:
            path_gene.update({case:row["gene_symbol"]})
            if row["gene_symbol"] not in total_gene:
                total_gene.append(row['gene_symbol'])
        data[case] = x

#total_name = ['name']
total_name = []
for sample in data:
    total_name.append(sample)

total_score = []
for gene in total_gene:
    tmp = [gene]
    for name in total_name:
        if name == 'name':
            break
        score = 0
        if gene not in data[name]:
            score = 0
        else:
            score = data[name][gene]
        tmp.append(score)
    total_score.append(tmp)

for idx, sample in enumerate(total_name):
    total_name[idx] = sample + "-" + path_gene[sample]

total_name.insert(0, "name")
g_file = output_dir + "gestalt_score.csv"
with open(g_file, 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(total_name)
    for gene in total_score:
        writer.writerow(gene)

cmd = "Rscript clustering_heatmap.R " + g_file + " " + output_dir
os.system(cmd)
