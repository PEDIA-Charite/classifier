import csv
import sys
import os
import numpy as np
from statistics import mean
from statistics import stdev
from scipy.stats import sem, t
from scipy import mean

################################################################3
# It is for generating the Sup table 1
#############################################################33333333333333333333



confidence = 0.95

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
outFile = open(output_dir + 'acc_result.tex', "w")
input_dir =['../../output/cv_g']
label = ['table:cv_g']
data_type = ["1KG"]

FEATURE = ["", "0", "3", "4", "0_3", "0_4", "3_4",
        "0_3_4",
        "1", "0_1", "1_3", "1_4", "0_1_3", "0_1_4", "1_3_4",
        "2", "0_2", "2_3", "2_4", "0_2_3", "0_2_4", "2_3_4",
        "0_1_3_4",
        "0_2_3_4",
        "1_2", "0_1_2", "1_2_3", "1_2_4", "0_1_2_3", "0_1_2_4", "1_2_3_4"]
divide_row = {0: 'Photo + Exome + Feature', 7: 'Photo + Exome', 15: 'Exome + Feature', 8: 'Photo + Feature',
        22: 'Photo', 23: 'Exome', 24: 'Feature'}
f_name = {'0':'F', '1':'C', '2':'G', '3':'B', '4':'P'}
divide_idxs = [0, 7, 8, 15, 22, 23, 24]
e_nums = [1, 2, 3, 4]
e_idx = {0:'1', 5:'2', 15:'3', 25:'4'}
print_idx = [4, 14, 24, 29]

############################################################################
# output header of table
###############################################################################

outFile.write("\\begin{center}\n")
outFile.write("\\begin{table}[ht]\n")
outFile.write("\\caption{Comparision results of using different scores for \
prioritization. \
First column indicates the scores used in each row. \
The second and third columns are the Top-1 and Top-10 accuracy and confidance interval. \
(F, Feature match score. \
C, CADD score. G, \
Gestalt score. P, Phenomizer score. B, Boqa score).}\\medskip\n")
outFile.write("\\label{result}\n")
outFile.write("\\centering\n")
outFile.write("\\begin{tabular}{|c|c|c|} \\hline\n")
outFile.write("&Top-1 (\%)&Top-10 (\%)\\\\ \\hline \n")

############################################################################
# Parse CV_g - 10 fold CV with gestalt support cases
###############################################################################

cv_dir = input_dir[0]
for idx, feature in enumerate(FEATURE):
    total_count = []
    for name in data_type:
        type_counts = {'1':[], '10':[], 'std1': [], 'std10':[]}
        cv_counts = {'1':[], '10':[]}
        for j in range(10):
            if idx == 0:
                filename = cv_dir + "/CV_" + name + "/cv_0" + "/count_" + str(j+1) + ".csv"
            else:
                cv_dir = '../../output/exclude_g/'
                filename = cv_dir + "/CV_" + name + "_e_" + feature + "/cv_0/count_" + str(j+1) + ".csv"
            top1 = 0
            top10 = 0
            row_count = 0
            total = 0
            with open(filename) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row_count == 0:
                        top1 = int(row[1])
                    if row_count < 10:
                        top10 += int(row[1])
                    total += int(row[1])
                    row_count += 1

            cv_counts['1'].append(top1/total*100)
            cv_counts['10'].append(top10/total*100)
        type_counts['1'].append(mean(cv_counts['1']))
        type_counts['10'].append(mean(cv_counts['10']))
        type_counts['std1'].append(stdev(cv_counts['1']))
        type_counts['std10'].append(stdev(cv_counts['10']))
    total_count.append(type_counts)

    perc = []
    stds = []
    ci = []
    index = 0
    perc.append([round(total_count[index]['1'][0], 1), round(total_count[index]['10'][0], 1)])
    stds.append([round(total_count[index]['std1'][0], 1), round(total_count[index]['std10'][0], 1)])
    m1 = round(total_count[index]['1'][0], 1)
    m10 = round(total_count[index]['10'][0], 1)
    h1 = round(total_count[index]['std1'][0], 1)
    h10 = round(total_count[index]['std10'][0], 1)
    low1 = m1 - 2 * h1 if (m1 - 2 * h1) > 0 else 0
    u1 = m1 + 2 * h1 if (m1 + 2 * h1) < 100 else 100
    low10 = m10 - 2 * h10 if (m10 - 2 * h10) > 0 else 0
    u10 = m10 + 2 * h10 if (m10 + 2 * h10) < 100 else 100
    ci.append([str(round(low1, 1)) + ' - ' + str(round(u1, 1)),
             str(round(low10, 1)) + ' - ' + str(round(u10, 1))])

    feature = feature.replace('_', '-')
    e_names = feature.split('-')

    e_list = []
    for x in f_name.keys():
        if x not in e_names:
            e_list.append(f_name[x])
    e_name = ','.join(e_list)

    if idx in divide_idxs:
        outFile.write("\\multicolumn{3}{|c|}{\\textbf{" + divide_row[idx] + "}}\\\\ \\hline \n")
    outFile.write(e_name  + "&" + str(perc[0][0]) + " \\small{[" + ci[0][0]  + "]} & " + str(perc[0][1]) +
            " \\small{[" + ci[0][1] + "]}\\\\ \\hline \n")

outFile.write("\\end{tabular}\n")
outFile.write("\\end{table}\n")

outFile.write("\\end{center}\n")

############################################################################
# Parse LOOCV_g - LOOCV CV with gestalt support cases
###############################################################################
#Output text
#cv_dir = input_dir[1]
#total_count = []
#for name in data_type:
#    counts = []
#    filename = cv_dir + "/LOOCV_" + name + "/rank_" + name + ".csv"
#    with open(filename) as csvfile:
#        reader = csv.reader(csvfile)
#        for row in reader:
#            counts.append(int(row[1]))
#    total_count.append(counts)
#
#total_rank = []
#perc = []
#avg_pedia = []
#for index in range(len(data_type)):
#    total = sum(total_count[index][0:100])
#    perc.append([round(total_count[index][0]/total*100, 2), round(sum(total_count[index][0:10])/total*100, 2)])
#outFile.write(rank_idx[1] + "&" + str(perc[0][0]) + "&" + str(perc[0][1]) + "&" + str(perc[1][0]) + "&" + str(perc[1][1]) + "\\\\ \\hline \n")


############################################################################
# Parse DeepGestalt
###############################################################################

#cv_dir = input_dir[2]
#total_count = []
#total_pedia = []
#for name in data_type:
#    type_counts = {'1':[], '10':[], 'std1': [], 'std10':[]}
#    for j in range(10):
#        filename = cv_dir + "/" + name + "/REP_" + str(j) + "/rank_" + name + ".csv"
#        top1 = 0
#        top10 = 0
#        row_count = 0
#        total = 0
#        with open(filename) as csvfile:
#            reader = csv.reader(csvfile)
#            for row in reader:
#                if row_count == 0:
#                    top1 = int(row[1])
#                if row_count < 10:
#                    top10 += int(row[1])
#                total += int(row[1])
#                row_count += 1
#
#        type_counts['1'].append(top1/total*100)
#        type_counts['10'].append(top10/total*100)
#    total_count.append(type_counts)
#
#perc = []
#stds = []
#ci = []
#for index in range(len(data_type)):
#    perc.append([round(mean(total_count[index]['1']), 1), round(mean(total_count[index]['10']), 1)])
#    stds.append([round(stdev(total_count[index]['1']), 1), round(stdev(total_count[index]['10']), 1)])
#    m1 = round(mean(total_count[index]['1']), 1)
#    m10 = round(mean(total_count[index]['10']), 1)
#    h1 = round(stdev(total_count[index]['1']), 1)
#    print(h1)
#    h10 = round(stdev(total_count[index]['10']), 1)
#    low1 = m1 - 2 * h1
#    u1 = m1 + 2 * h1 if (m1 + 2 * h1) < 100 else 100
#    low10 = m10 - 2 * h10
#    u10 = m10 + 2 * h10 if (m10 + 2 * h10) < 100 else 100
#    ci.append([str(round(low1, 1)) + '-' + str(round(u1, 1)),
#             str(round(low10, 1)) + '-' + str(round(u10, 1))])
#
#out_str = rank_idx[0] + "&"
#outFile.write("\\multirow{2}{*}{" + rank_idx[2] + "}&" + str(perc[0][0]) + "&" + str(perc[0][1]) 
#        + "&" + str(perc[1][0]) + "&" + str(perc[1][1]) + "\\\\ \n")
#outFile.write("& [" + ci[0][0]  + "]&" + "[" + ci[0][1]
#        + "]&" + "[" + ci[1][0] + "]&" + "[" + ci[1][1] + "]\\\\ \\hline \n")

