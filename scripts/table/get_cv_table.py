import csv
import sys
import os
import numpy as np

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
outFile = open(output_dir + 'acc_cv_result.tex', "w")
input_dir =['../../output/cv']
#input_dir =['../../output/cv', '../../output/cv_g']
caption = ['all cases', 'the cases with gestalt in pathogenic mutation gene']
label = ['table:cv', 'table:cv_g']
data_type = ["1KG", "ExAC", "IRAN"]

#Output text
for cv_idx, cv_dir in enumerate(input_dir):
    outFile.write("\\begin{center}\n")
    outFile.write("\\begin{table}[ht]\n")
    outFile.write("\\caption{Result of 10-fold cross validation result on " + caption[cv_idx] + "}\\medskip\n")
    outFile.write("\\label{" + label[cv_idx] + "}\n")
    outFile.write("\\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|} \\hline\n")
    outFile.write("&\\multicolumn{3}{|c|}{1KG}&\\multicolumn{3}{|c|}{ExAC}&\\multicolumn{3}{|c|}{IRAN}\\\\ \\hline \n")
    outFile.write("Rank&Count&Cumu(\%)&pedia&Count&Cumu(\%)&pedia&Count&Cumu(\%)&pedia\\\\ \\hline \n")
    total_count = []
    total_pedia = []
    for name in data_type:
        counts = []
        filename = cv_dir + "/CV_" + name + "/rank_" + name + ".csv"
        with open(filename) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                counts.append(float(row[1]))

        total_count.append(counts)
        cv_pedia = []
        for cv_idx in range(2):
            pedia_score = [[], [], [], []]
            filename = cv_dir + "/CV_" + name + "/cv_" + str(cv_idx) + "/rank_gene_" + name + ".csv"
            with open(filename) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    pedia_file = cv_dir + "/CV_" + name + "/cv_" + str(cv_idx) + "/" + row[0] + ".csv"
                    flag = 0
                    with open(pedia_file) as pedia_csv:
                        reader_2 = csv.reader(pedia_csv)
                        for row_2 in reader_2:
                            if flag == 1:
                                if int(row_2[3]) == 1:
                                    if int(row[1]) == 0:
                                        pedia_score[0].append(float(row_2[2]))
                                    elif int(row[1]) > 0 and int(row[1]) <= 9:
                                        pedia_score[1].append(float(row_2[2]))
                                    elif int(row[1]) > 9 and int(row[1]) <= 98:
                                        pedia_score[2].append(float(row_2[2]))
                                    else:
                                        pedia_score[3].append(float(row_2[2]))
                            flag = 1
            cv_pedia.append([np.mean(np.array(value)) for value in pedia_score])
        cv_pedia = np.array(cv_pedia)
        total_pedia.append([np.mean(cv_pedia[:,i]) for i in range(4)])

    total_rank = []
    total_list = []
    avg_pedia = []
    perc = []
    for index in range(3):
        total = round(sum(total_count[index][0:100]))
        total_list.append(total)
        total_rank.append([round(total_count[index][0], 2), round(sum(total_count[index][1:10]), 2), round(sum(total_count[index][10:99]), 2), round(total_count[index][99], 2)])
        perc.append([round(total_count[index][0]/total*100, 2), round(sum(total_count[index][0:10])/total*100, 2), round(sum(total_count[index][0:99])/total*100, 2), round(sum(total_count[index][0:100])/total*100, 2)])
        avg_pedia.append([round(value, 2) for value in total_pedia[index]])

    rank_idx = ["1", "2-10", "11-99", "100+"]
    for index in range(4):
        outFile.write(rank_idx[index] + "&" + str(total_rank[0][index]) + "&" + str(perc[0][index]) + "&" + str(avg_pedia[0][index]) + "&" + str(total_rank[1][index]) + "&" + str(perc[1][index]) + "&" + str(avg_pedia[1][index]) + "&" + str(total_rank[2][index]) + "&" + str(perc[2][index]) + "&" + str(avg_pedia[2][index]) + "\\\\ \\hline \n")

    outFile.write("Total&\\multicolumn{3}{|c|}{" + str(total_list[0]) + "}&\\multicolumn{3}{|c|}{" + str(total_list[1]) + "}&\\multicolumn{3}{|c|}{" + str(total_list[2]) + "}\\\\ \\hline \n")
    outFile.write("\\end{tabular}\n")
    outFile.write("\\end{table}\n")

    outFile.write("\\end{center}\n")

#####################################################################
## the cases with gestalt
#####################################################################
#outFile.write("\\begin{center}\n")
#
#data_type = ["1KG", "ExAC", "IRAN"]
#outFile.write("\\begin{table}[ht]\n")
#outFile.write("\\caption{10-fold cross validation result on the cases which has gestalt score in pathogenic mutation gene}\\medskip\n")
#outFile.write("\\label{compare}\n")
#outFile.write("\\begin{tabular}{|c|c|c|c|c|c|c|c|c|c|} \\hline\n")
#outFile.write("&\\multicolumn{3}{|c|}{1KG}&\\multicolumn{3}{|c|}{ExAC}&\\multicolumn{3}{|c|}{IRAN}\\\\ \\hline \n")
#outFile.write("Rank&Count&Cumu(\%)&pedia&Count&Cumu(\%)&pedia&Count&Cumu(\%)&pedia\\\\ \\hline \n")
#total_count = []
#total_pedia = []
#for name in data_type:
#    counts = []
#    pedia_score = [0, 0, 0, 0]
#    filename = "../../output/cv_g/CV_" + name + "/rank_" + name + ".csv"
#    with open(filename) as csvfile:
#        reader = csv.reader(csvfile)
#        for row in reader:
#            counts.append(float(row[1]))
#    total_count.append(counts)
#
#    filename = "../../output/cv_g/CV_" + name + "/cv_0/rank_gene_" + name + ".csv"
#    with open(filename) as csvfile:
#        reader = csv.reader(csvfile)
#        for row in reader:
#            pedia_file = "../../output/cv_g/CV_" + name + "/cv_0/" + row[0] + ".csv"
#            flag = 0
#            with open(pedia_file) as pedia_csv:
#                reader_2 = csv.reader(pedia_csv)
#                for row_2 in reader_2:
#                    if flag == 1:
#                        if int(row_2[2]) == 1:
#                            if int(row[1]) == 0:
#                                pedia_score[0] += float(row_2[1])
#                            elif int(row[1]) > 0 and int(row[1]) <= 9:
#                                pedia_score[1] += float(row_2[1])
#                            elif int(row[1]) > 9 and int(row[1]) <= 98:
#                                pedia_score[2] += float(row_2[1])
#                            else:
#                                pedia_score[3] += float(row_2[1])
#                    flag = 1
#    total_pedia.append(pedia_score)
#total_rank = []
#total_list = []
#perc = []
#avg_pedia = []
#print(total_count)
#for index in range(3):
#    total = round(sum(total_count[index][0:100]))
#    total_list.append(total)
#    total_rank.append([round(total_count[index][0], 2), round(sum(total_count[index][1:10]), 2), round(sum(total_count[index][10:99]), 2), round(total_count[index][99], 2)])
#    perc.append([round(total_count[index][0]/total*100, 2), round(sum(total_count[index][0:10])/total*100, 2), round(sum(total_count[index][0:99])/total*100, 2), round(sum(total_count[index][0:100])/total*100, 2)])
#    avg_pedia.append([round(value / round(total_rank[index][idx]), 2) for idx, value in enumerate(total_pedia[index])])
#
#rank_idx = ["1", "2-10", "11-99", "100+"]
#for index in range(4):
#    outFile.write(rank_idx[index] + "&" + str(total_rank[0][index]) + "&" + str(perc[0][index]) + "&" + str(avg_pedia[0][index]) + "&" + str(total_rank[1][index]) + "&" + str(perc[1][index]) + "&" + str(avg_pedia[1][index]) + "&" + str(total_rank[2][index]) + "&" + str(perc[2][index]) + "&" + str(avg_pedia[2][index]) + "\\\\ \\hline \n")
#
#outFile.write("Total&\\multicolumn{3}{|c|}{" + str(total_list[0]) + "}&\\multicolumn{3}{|c|}{" + str(total_list[1]) + "}&\\multicolumn{3}{|c|}{" + str(total_list[2]) + "}\\\\ \\hline \n")
#outFile.write("\\end{tabular}\n")
#outFile.write("\\end{table}\n")
#
#outFile.write("\\end{center}\n")
#outFile.close()
#outFile = open(output_dir + 'gene_cv_result.tex', "w")
##Output text
#outFile.write("\\begin{center}\n")
#
#data_type = ["1KG", "ExAC", "IRAN"]
#outFile.write("\\begin{table}[ht]\n")
#outFile.write("\\caption{Sample list of 10-fold cross validation}\\medskip\n")
#outFile.write("\\label{compare}\n")
#outFile.write("\\begin{tabular}{|c|c|c|c|c|c|c|} \\hline\n")
#outFile.write("\\multicolumn{2}{|c|}{1KG}&\\multicolumn{2}{|c|}{ExAC}&\\multicolumn{2}{|c|}{IRAN}\\\\ \\hline \n")
#outFile.write("Rank&Sample&Rank&Sample&Rnak&Sample\\\\ \\hline \n")
#total_count = []
#for name in data_type:
#    counts = []
#    filename = "../../output/CV_" + name + "/rank_gene_" + name + ".csv"
#    with open(filename) as csvfile:
#        reader = csv.reader(csvfile)
#        for row in reader:
#            if int(row[1]) > 9:
#                counts.append((int(row[1]), row[0]))
#    total_count.append(counts)
#
#max_len = max(max(len(total_count[0]), len(total_count[1])), len(total_count[2]))
#outText = ""
#for index in range(max_len):
#    if len(total_count[0]) < index + 1:
#        outText = outText + " & "
#    else:
#        outText = outText + str(total_count[0][index][0]) + "&" + total_count[0][index][1]
#
#    outText = outText + "&"
#    if len(total_count[1]) < index + 1:
#        outText = outText + " & "
#    else:
#        outText = outText + str(total_count[1][index][0]) + "&" + total_count[1][index][1]
#
#    outText = outText + "&"
#    if len(total_count[2]) < index + 1:
#        outText = outText + " & "
#    else:
#        outText = outText + str(total_count[2][index][0]) + "&" + total_count[2][index][1]
#    outText = outText + "\\\\ \\hline \n"
#outFile.write(outText)
#
#outFile.write("\\end{tabular}\n")
#outFile.write("\\end{table}\n")
#
#outFile.write("\\end{center}\n")
#outFile.close()
