import csv
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('pdf')
from matplotlib import pyplot
import math
import json

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
outFile = open(output_dir + 'pedia_cv_result.tex', "w")

#Output text
input_dir =['../../output/cv_g']
type_suffix = ['_g']
caption = ['the cases with gestalt in ']
data_type = ["1KG", "ExAC", "IRAN"]
label = ['table:pedia_cv_g']

#Output text
for type_idx, type_dir in enumerate(input_dir):
    outFile.write("\\begin{center}\n")
    outFile.write("\\begin{table}[ht]\n")
    outFile.write("\\caption{Pedia score of 10-fold cross validation on " + caption[type_idx] + "pathogenic mutation gene}\\medskip\n")
    outFile.write("\\label{" + label[type_idx] + "}\n")
    outFile.write("\\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|c|c|c|} \\hline\n")
    outFile.write("&\\multicolumn{4}{|c|}{1KG}&\\multicolumn{4}{|c|}{ExAC}&\\multicolumn{4}{|c|}{IRAN}\\\\ \\hline \n")
    outFile.write("&\\multicolumn{2}{|c|}{Neutrals}&\\multicolumn{2}{|c|}{Pathogenic}&\\multicolumn{2}{|c|}{Neutrals}&\\multicolumn{2}{|c|}{Pathogenic}&\\multicolumn{2}{|c|}{Neutrals}&\\multicolumn{2}{|c|}{Pathogenic}\\\\ \\hline \n")
    outFile.write("Rank&Mean&Std&Mean&std&Mean&Std&Mean&Std&Mean&Std&Mean&Std\\\\ \\hline \n")
    total_mean = []
    total_p_mean = []
    total_std = []
    total_p_std = []
    total_pedia = []
    total_p_pedia = []
    for name in data_type:
        cv_count = []
        cv_p_count = []
        cv_pedia = []
        cv_p_pedia = []
        cv_rank = []
        cv_p_rank = []
        cv_mean = []
        cv_p_mean = []
        cv_std = []
        cv_p_std = []
        pedia_score = []
        pedia_p_score = []
        for cv_idx in range(1):
            count = [0, 0, 0, 0]
            p_count = [0, 0, 0, 0]
            rank_score = [[], [], [], []]
            rank_p_score = [[], [], [], []]
            filename = type_dir + "/CV_" + name + "/cv_" + str(cv_idx) + "/rank_gene_" + name + ".csv"
            with open(filename) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    pedia_file = type_dir + "/CV_" + name + "/cv_" + str(cv_idx) + "/" + row[0] + ".csv"
                    flag = 0
                    rank = 0
                    with open(pedia_file) as pedia_csv:
                        reader_2 = csv.reader(pedia_csv)
                        for row_2 in reader_2:
                            if flag == 1:
                                if int(row_2[3]) == 1:
                                    pedia_p_score.append(float(row_2[2]))
                                    if rank == 0:
                                        rank_p_score[0].append(float(row_2[2]))
                                        p_count[0] += 1
                                    elif rank > 0 and rank < 10:
                                        rank_p_score[1].append(float(row_2[2]))
                                        p_count[1] += 1
                                    elif rank >= 10 and rank < 99:
                                        rank_p_score[2].append(float(row_2[2]))
                                        p_count[2] += 1
                                    else:
                                        rank_p_score[3].append(float(row_2[2]))
                                        p_count[3] += 1
                                else:
                                    pedia_score.append(float(row_2[2]))
                                    if rank == 0:
                                        rank_score[0].append(float(row_2[2]))
                                        count[0] += 1
                                    elif rank > 0 and rank < 10:
                                        rank_score[1].append(float(row_2[2]))
                                        count[1] += 1
                                    elif rank >= 10 and rank < 99:
                                        rank_score[2].append(float(row_2[2]))
                                        count[2] += 1
                                    else:
                                        rank_score[3].append(float(row_2[2]))
                                        count[3] += 1
                                rank += 1
                            flag = 1
            #cv_pedia.append(pedia_score)
            #cv_p_pedia.append(pedia_p_score)
            cv_rank.append([np.mean(np.array(value)) for value in rank_score])
            cv_p_rank.append([np.mean(np.array(value)) for value in rank_p_score])
            cv_std.append([np.std(np.array(value)) for value in rank_score])
            cv_p_std.append([np.std(np.array(value)) for value in rank_p_score])
        total_pedia.append(pedia_score)
        total_p_pedia.append(pedia_p_score)
        cv_rank = np.array(cv_rank)
        cv_p_rank = np.array(cv_p_rank)
        cv_std = np.array(cv_std)
        cv_p_std = np.array(cv_p_std)
        total_mean.append([round(np.mean(cv_rank[:,i]), 2) for i in range(4)])
        total_p_mean.append([round(np.mean(cv_p_rank[:,i]), 2) for i in range(4)])
        total_std.append([round(np.mean(cv_std[:,i]), 2) for i in range(4)])
        total_p_std.append([round(np.mean(cv_p_std[:,i]), 2) for i in range(4)])
    rank_idx = ["1", "2-10", "11-99", "100+"]
    for index in range(4):
        outFile.write(rank_idx[index] + "&" + str(total_mean[0][index]) + "&" + str(total_std[0][index]) + "&" + str(total_p_mean[0][index]) + "&" + str(total_p_std[0][index]) + "&" + str(total_mean[1][index]) + "&" + str(total_std[1][index]) + "&" + str(total_p_mean[1][index]) + "&" + str(total_p_std[1][index]) + "&" + str(total_mean[2][index]) + "&" + str(total_std[2][index]) + "&" + str(total_p_mean[2][index]) + "&" + str(total_p_std[2][index]) + "\\\\ \\hline \n")
    color_list = ['#ffa347','#0064c8','#b42222','#22a5b4','#b47c22','#6db6ff']
    pyplot.figure(figsize=(8, 6), dpi=100)

    marker_type = ['o', 'v', 's']

    for idx, name in enumerate(data_type):
        bin_array = np.arange(math.floor(min(total_pedia[idx])), math.ceil(max(total_pedia[idx]))+10, 1).tolist()

        for i, j in enumerate(bin_array):
            bin_array[i] = round(bin_array[i], 2)

        n, bins, patches = pyplot.hist(total_pedia[idx], bin_array, alpha=0.6, color=color_list[0], label = 'neutrals', edgecolor='black')
        n, bins, patches = pyplot.hist(total_p_pedia[idx], bin_array, alpha=0.6, color=color_list[1], label = 'Pathogenic', edgecolor='black')

        pyplot.gca().set_yscale("log")
        pyplot.grid(True)
        pyplot.legend(loc = 2, prop = {'size':12})
        pyplot.xlabel('Value', fontsize = 18)
        pyplot.ylabel('Counts', fontsize = 18)
        pyplot.title(caption[type_idx] + name, fontsize=18)
        pyplot.savefig(output_dir + 'dist_pedia' + type_suffix[type_idx] + '_' + name + '.png', dpi = 180)
        pyplot.close()

    outFile.write("\\end{tabular}\n")
    outFile.write("\\end{table}\n")

    outFile.write("\\end{center}\n")

outFile.close()
sample_filename = "../../output/cv_g/CV_1KG/train.csv"
sample_dict = {}
label = ['table:cv_poor_case']

with open(sample_filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        if flag == 1:
            if int(row[-1]) == 1:
                sample_dict.update({row[0]: row[3:10]})
        flag = 1
caption = ['all cases', 'the cases with gestalt in pathogenic mutation gene']
outFile = open(output_dir + '/pedia_cv_poor_sample.tex', "w")
for idx, input_type in enumerate(input_dir):
    pedia_score_0 = []
    pedia_score_1 = []
    name = '1KG'
    cv_idx = 0
    filename = input_type + "/CV_" + name + "/cv_" + str(cv_idx) + "/rank_gene_" + name + ".csv"
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            pedia_file = input_type + "/CV_" + name + "/cv_" + str(cv_idx) + "/" + row[0] + ".csv"
            json_data = json.load(open('../../../3_simulation/json_simulation/1KG/CV_gestalt/' + row[0] + '.json'))
            syndrome = json_data['selected_syndromes'][0]['syndrome_name']
            flag = 0
            rank = 1
            with open(pedia_file) as pedia_csv:
                reader_2 = csv.reader(pedia_csv)
                for row_2 in reader_2:
                    if flag == 1:
                        if int(row_2[3]) == 1:
                            value = sample_dict[row[0]]
                            if float(row_2[2]) < 0:
                                pedia_score_0.append([row[0], str(round(float(row_2[2]), 2)), str(rank), str(round(float(value[0]),1)), str(round(float(value[1]), 1)), str(round(float(value[4]), 1)), str(round(float(value[5]), 1)), str(round(float(value[6]), 1))])
                            if float(row_2[2]) >= 0 and float(row_2[2]) < 1:
                                pedia_score_1.append([row[0], str(round(float(row_2[2]), 2)), str(rank), str(round(float(value[0]),1)), str(round(float(value[1]), 1)), str(round(float(value[4]), 1)), str(round(float(value[5]), 1)), str(round(float(value[6]), 1))])
                        rank += 1
                    flag = 1

    outFile.write("\\begin{center}\n")
    outFile.write("\\begin{longtable}{|c|c|c|c|c|c|c|c|}\n")
    outFile.write("\\caption{Cases with poor performance on " + caption[idx] + "}\\\\ \n")
    outFile.write("\\hline \n")
    outFile.write("\\label{" + label[idx] + "}\n")
    outFile.write("Case&Pedia&Rank&FM&CADD&Gestalt&Boqa&PHENO\\\\ \\hline \n")
    outFile.write("\\multicolumn{8}{|c|}{Pedia under 0}\\\\ \\hline \n")
    for pedia in pedia_score_0:
        outFile.write("&".join(pedia) + "\\\\ \\hline \n")
    outFile.write("\\multicolumn{8}{|c|}{Pedia between 0 and 1}\\\\ \\hline \n")
    for pedia in pedia_score_1:
        outFile.write("&".join(pedia) + "\\\\ \\hline \n")
    outFile.write("\\end{longtable}\n")
    outFile.write("\\end{center}\n")
outFile.close()
