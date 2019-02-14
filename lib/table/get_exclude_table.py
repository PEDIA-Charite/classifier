import csv
import sys
import os
from statistics import mean
from statistics import stdev

FEATURE = ["0", "1", "2", "3", "4", "0_3", "0_4", "1_2", "3_4","0_2_3",
            "0_3_4", "0_2_3_4", "0_1_3_4"]
FEATURE = ["0", "3", "4", "0_3", "0_4", "3_4",
        "0_3_4",
        "1",
        "2", "0_2_3", 
        "0_1_3_4",
        "0_2_3_4",
        "1_2"]
FEATURE = ["0", "3", "4", "0_3", "0_4", "3_4",
        "0_3_4",
        "1", "0_1", "1_3", "1_4", "0_1_3", "0_1_4", "1_3_4",
        "2", "0_2", "2_3", "2_4", "0_2_3", "0_2_4", "2_3_4",
        "0_1_3_4",
        "0_2_3_4",
        "1_2", "0_1_2", "1_2_3", "1_2_4", "0_1_2_3", "0_1_2_4", "1_2_3_4"]
divide_row = {0: 'Photo + Exome + Feature', 6: 'Photo + Exome', 14: 'Exome + Feature', 7: 'Photo + Feature',
        21: 'Photo', 22: 'Exome', 23: 'Feature'}
f_name = {'0':'F', '1':'C', '2':'G', '3':'B', '4':'P'}
divide_idxs = [0, 6, 7, 14, 21, 22, 23]
output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

outFile = open(output_dir + 'acc_exclude_result_1002.tex', "w")
#Output text

data_type = ["1KG"]
#data_type = ["1KG", "IRAN"]
e_nums = [1, 2, 3, 4]
e_idx = {0:'1', 5:'2', 15:'3', 25:'4'}
print_idx = [4, 14, 24, 29]
input_dirs = ['../../output/exclude_g/']

############################################################################
# output header of table
###############################################################################

outFile.write("\\begin{center}\n")
outFile.write("\\begin{table}[ht]\n")
outFile.write("\\caption{Comparision results of using different scores for prioritization. First column indicates the scores used in each row.}\\medskip\n")
outFile.write("\\label{result}\n")
outFile.write("\\centering\n")
outFile.write("\\begin{tabular}{|c|c|c|} \\hline\n")
outFile.write("&\\multicolumn{2}{c|}{1KG}\\\\ \n")
outFile.write("&Top-1 (\%)&Top-10 (\%)\\\\ \\hline \n")

############################################################################
# Parse exclude
###############################################################################

cv_dir = input_dirs[0]
for idx, feature in enumerate(FEATURE):
    total_count = []
    for name in data_type:
        type_counts = {'1':[], '10':[], 'std1': [], 'std10':[]}
        cv_counts = {'1':[], '10':[]}
        for j in range(10):
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
        print(cv_counts)
        type_counts['1'].append(mean(cv_counts['1']))
        type_counts['10'].append(mean(cv_counts['10']))
        type_counts['std1'].append(stdev(cv_counts['1']))
        type_counts['std10'].append(stdev(cv_counts['10']))
        total_count.append(type_counts)
    
    feature = feature.replace('_', '-')
    e_names = feature.split('-')

    e_list = []
    for x in f_name.keys(): 
        if x not in e_names:
            e_list.append(f_name[x])
    e_name = ','.join(e_list)
    perc = []
    stds = []
    for index in range(len(data_type)):
        perc.append([round(total_count[index]['1'][0], 1), round(total_count[index]['10'][0], 1)])
        stds.append([round(total_count[index]['std1'][0], 1), round(total_count[index]['std10'][0], 1)])
        #perc.append([round(mean(total_count[index]['1']), 1), round(mean(total_count[index]['10']), 1)])
        #stds.append([round(mean(total_count[index]['std1']), 1), round(mean(total_count[index]['std10']), 1)])
    if idx in divide_idxs:
        outFile.write("\\multicolumn{3}{|c|}{\\textbf{" + divide_row[idx] + "}}\\\\ \\hline \n")
    outFile.write(e_name + "&" + str(perc[0][0]) + "&" + str(perc[0][1]) + "\\\\ \\hline \n")
    #outFile.write(e_name + "&" + str(perc[0][0]) + "&" + str(perc[0][1]) + "&" + str(perc[1][0]) + "&" + str(perc[1][1]) + "\\\\ \\hline \n")

outFile.write("\\end{tabular}\n")
outFile.write("\\end{table}\n")

outFile.write("\\end{center}\n")
outFile.close()

