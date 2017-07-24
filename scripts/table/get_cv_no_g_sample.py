import csv
import sys
import os
import collections

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
outFile = open(output_dir + 'cv_sample_without_g.tex', "w")
filename = "../sample.csv"


outFile.write("\\begin{center}\n")

data_type = ["1KG", "ExAC", "IRAN"]
outFile.write("\\begin{table}[ht]\n")
outFile.write("\\caption{10-fold cross validation result on the cases which has no gestalt score in pathogenic mutation gene}\\medskip\n")
outFile.write("\\label{table:cv_sample_no_g}\n")
outFile.write("\\begin{tabular}{|c|c|c|c|c|c|c|} \\hline\n")
outFile.write("&\\multicolumn{2}{|c|}{1KG}&\\multicolumn{2}{|c|}{ExAC}&\\multicolumn{2}{|c|}{IRAN}\\\\ \\hline \n")
outFile.write("Rank&Count&pedia&Count&pedia&Count&pedia\\\\ \\hline \n")
total_count = []
total_pedia = []
for name in data_type:
    counts = []
    inputfile2 = '../../output/cv/CV_' + name + '/cv_0/'
    total_rank = [0, 0, 0, 0]
    pedia = [0, 0, 0, 0]
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        flag = 0
        for row in reader:
            outrow = [j for i, j in enumerate(row) if i != 2]
            if flag == 1 and row[5] == 'nan':
                inputname = inputfile2 + row[0] + ".csv"
                flag_2 = 0
                with open(inputname) as result_file:
                    reader_2 = csv.reader(result_file)
                    rank = 1
                    for row_2 in reader_2:
                        if flag_2 == 1:
                            if int(row_2[2]) == 1:
                                #outFile.write(row[0] + ';' + str(rank) + '\n')
                                if rank == 1:
                                    total_rank[0] += 1
                                    pedia[0] += float(row_2[1])
                                elif rank > 1 and rank <= 10:
                                    total_rank[1] += 1
                                    pedia[1] += float(row_2[1])
                                elif rank > 10 and rank <= 99:
                                    total_rank[2] += 1
                                    pedia[2] += float(row_2[1])
                                else:
                                    total_rank[3] += 1
                                    pedia[3] += float(row_2[1])
                            rank += 1
                        flag_2 = 1
            flag = 1
    total_count.append(total_rank)
    for i in range(4):
        pedia[i] = round(pedia[i] / total_rank[i], 2)
    total_pedia.append(pedia)


rank_idx = ["1", "2-10", "11-99", "100+"]

for index in range(4):
    outFile.write(rank_idx[index] + "&" + str(total_count[0][index]) + "&" + str(total_pedia[0][index])+ "&" + str(total_count[1][index]) + "&" + str(total_pedia[1][index])+ "&" + str(total_count[2][index]) + "&" + str(total_pedia[2][index]) + "\\\\ \\hline \n")

outFile.write("Total&\\multicolumn{2}{|c|}{" + str(sum(total_count[0])) + "}&\\multicolumn{2}{|c|}{" + str(sum(total_count[1])) + "}&\\multicolumn{2}{|c|}{" + str(sum(total_count[2])) +"}\\\\ \\hline \n")
outFile.write("\\end{tabular}\n")
outFile.write("\\end{table}\n")

outFile.write("\\end{center}\n")

outFile.close()
