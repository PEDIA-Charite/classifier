import csv
import sys
import os

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
outFile = open(output_dir + 'acc_cv_result.tex', "w")
#Output text
outFile.write("\\begin{center}\n")

data_type = ["1KG", "ExAC", "IRAN"]
outFile.write("\\begin{table}[ht]\n")
outFile.write("\\caption{10-fold cross validation result}\\medskip\n")
outFile.write("\\label{compare}\n")
outFile.write("\\begin{tabular}{|c|c|c|c|c|c|c|} \\hline\n")
outFile.write("&\\multicolumn{2}{|c|}{1KG}&\\multicolumn{2}{|c|}{ExAC}&\\multicolumn{2}{|c|}{IRAN}\\\\ \\hline \n")
outFile.write("Rank&Count&Cumulative(\%)&Count&Cumulative(\%)&Count&Cumulative(\%)\\\\ \\hline \n")
total_count = []
for name in data_type:
    counts = []
    filename = "../../output/CV_" + name + "/rank_" + name + ".csv"
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            counts.append(int(row[1]))
    total_count.append(counts)

total_rank = []
perc = []
for index in range(3):
    total = sum(total_count[index][0:100])
    total_rank.append([total_count[index][0], sum(total_count[index][1:10]), sum(total_count[index][10:99]), total_count[index][99]])
    perc.append([round(total_count[index][0]/total*100, 2), round(sum(total_count[index][0:10])/total*100, 2), round(sum(total_count[index][0:99])/total*100, 2), round(sum(total_count[index][0:100])/total*100, 2)])

rank_idx = ["1", "2-10", "11-99", "100+"]
for index in range(4):
    outFile.write(rank_idx[index] + "&" + str(total_rank[0][index]) + "&" + str(perc[0][index]) + "&" + str(total_rank[1][index]) + "&" + str(perc[1][index])+ "&" + str(total_rank[2][index]) + "&" + str(perc[2][index])+ "\\\\ \\hline \n")

outFile.write("\\end{tabular}\n")
outFile.write("\\end{table}\n")

outFile.write("\\end{center}\n")
outFile.close()



outFile = open(output_dir + 'gene_cv_result.tex', "w")
#Output text
outFile.write("\\begin{center}\n")

data_type = ["1KG", "ExAC", "IRAN"]
outFile.write("\\begin{table}[ht]\n")
outFile.write("\\caption{Sample list of 10-fold cross validation}\\medskip\n")
outFile.write("\\label{compare}\n")
outFile.write("\\begin{tabular}{|c|c|c|c|c|c|c|} \\hline\n")
outFile.write("\\multicolumn{2}{|c|}{1KG}&\\multicolumn{2}{|c|}{ExAC}&\\multicolumn{2}{|c|}{IRAN}\\\\ \\hline \n")
outFile.write("Rank&Sample&Rank&Sample&Rnak&Sample\\\\ \\hline \n")
total_count = []
for name in data_type:
    counts = []
    filename = "../../output/CV_" + name + "/rank_gene_" + name + ".csv"
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if int(row[1]) > 9:
                counts.append((int(row[1]), row[0]))
    total_count.append(counts)

max_len = max(max(len(total_count[0]), len(total_count[1])), len(total_count[2]))
outText = ""
for index in range(max_len):
    if len(total_count[0]) < index + 1:
        outText = outText + " & "
    else:
        outText = outText + str(total_count[0][index][0]) + "&" + total_count[0][index][1]

    outText = outText + "&"
    if len(total_count[1]) < index + 1:
        outText = outText + " & "
    else:
        outText = outText + str(total_count[1][index][0]) + "&" + total_count[1][index][1]

    outText = outText + "&"
    if len(total_count[2]) < index + 1:
        outText = outText + " & "
    else:
        outText = outText + str(total_count[2][index][0]) + "&" + total_count[2][index][1]
    outText = outText + "\\\\ \\hline \n"
outFile.write(outText)

outFile.write("\\end{tabular}\n")
outFile.write("\\end{table}\n")

outFile.write("\\end{center}\n")
outFile.close()
