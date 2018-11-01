#######################################################################################
# This script generate three latex files.
# sample.tex and sample_gestalt.tex contain three tables in each file.
# The tables are the details of samples. The difference between first two files is
# that sample.tex contains all sample but sample_gestalt only contain the sample which
# have gestalt score in pathogenic gene.
# sample_detail_no_g.tex contains the detail of the sample which has no gestalt score
# in pathogenic gene.
########################################################################################

import csv
import sys
import os
import collections

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
outFile = open(output_dir + 'sample.tex', "w")
filename = "../sample.csv"
#Output text
gene_list = {}
total_sample = 0
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        if flag == 1:
            count = 0
            if row[1] in gene_list:
                count = gene_list[row[1]]
            count += 1
            gene_list.update({row[1]:count})
            total_sample += 1

        flag = 1

print(gene_list)
total_gene = len(gene_list)
print(total_sample)
outFile.write("\\begin{center}\n")

outFile.write("\\begin{longtable}{|c|c|} \\hline\n")
outFile.write("Gene&Count\\\\ \\hline \n")

od = collections.OrderedDict(sorted(gene_list.items()))
for key, value in od.items():
    outFile.write(key + "&" + str(value) + "\\\\ \\hline \n")

outFile.write(str(total_gene) + "&" + str(total_sample) + "\\\\ \\hline \n")
outFile.write("\\caption{summary table of mutation gene}  \n")
outFile.write("\\end{longtable}\n")
outFile.write("\\end{center}\n")

outFile.write("\\begin{center}\n")

outFile.write("\\begin{longtable}{|l|l|p{12cm}|} \\hline\n")
outFile.write("Case&Gene&Syndrome\\\\ \\hline \n")
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        if flag == 1:
            outFile.write("&".join(row[0:3]) + "\\\\ \\hline \n")
        flag = 1

outFile.write("\\caption{Sample} \n")
outFile.write("\\end{longtable}\n")

outFile.write("\\end{center}\n")
outFile.write("\\begin{center}\n")

outFile.write("\\begin{longtable}{|l|l|c|c|c|c|c|} \\hline\n")
outFile.write("Case&Gene&FM&CADD&Gestalt&Boqa&Pheno\\\\ \\hline \n")
filename = "../sample.csv"
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        outrow = [j for i, j in enumerate(row) if i != 2]
        if flag == 1:
            outFile.write("&".join(outrow) + "\\\\ \\hline \n")
        flag = 1

outFile.write("\\caption{Sample} \n")
outFile.write("\\end{longtable}\n")

outFile.write("\\end{center}\n")
outFile.close()

# For sample with gestalt
outFile = open(output_dir + 'sample_gestalt.tex', "w")

#Output text
gene_list = {}
total_sample = 0
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        if flag == 1 and row[5] != 'nan':
            count = 0
            if row[1] in gene_list:
                count = gene_list[row[1]]
            count += 1
            gene_list.update({row[1]:count})
            total_sample += 1

        flag = 1

print(gene_list)
total_gene = len(gene_list)
print(total_sample)
outFile.write("\\begin{center}\n")

outFile.write("\\begin{longtable}{|c|c|} \\hline\n")
outFile.write("Gene&Count\\\\ \\hline \n")

od = collections.OrderedDict(sorted(gene_list.items()))
for key, value in od.items():
    outFile.write(key + "&" + str(value) + "\\\\ \\hline \n")

outFile.write(str(total_gene) + "&" + str(total_sample) + "\\\\ \\hline \n")
outFile.write("\\caption{summary table of mutation gene with gestalt score}  \n")
outFile.write("\\end{longtable}\n")
outFile.write("\\end{center}\n")

outFile.write("\\begin{center}\n")

outFile.write("\\begin{longtable}{|l|l|p{12cm}|} \\hline\n")
outFile.write("Case&Gene&Syndrome\\\\ \\hline \n")
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        if flag == 1 and row[5] != 'nan':
            outFile.write("&".join(row[0:3]) + "\\\\ \\hline \n")
        flag = 1

outFile.write("\\caption{Sample with gestalt score} \n")
outFile.write("\\end{longtable}\n")

outFile.write("\\end{center}\n")
outFile.write("\\begin{center}\n")

outFile.write("\\begin{longtable}{|l|l|c|c|c|c|c|} \\hline\n")
outFile.write("Case&Gene&FM&CADD&Gestalt&Boqa&Pheno\\\\ \\hline \n")
filename = "../sample.csv"
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        outrow = [j for i, j in enumerate(row) if i != 2]
        if flag == 1 and row[5] != 'nan':
            outFile.write("&".join(outrow) + "\\\\ \\hline \n")
        flag = 1

outFile.write("\\caption{Sample with gestalt score} \n")
outFile.write("\\end{longtable}\n")

outFile.write("\\end{center}\n")
outFile.close()

#####################################################################3

outFile = open(output_dir + 'sample_detail_no_g.tex', "w")
outFile.write("\\begin{center}\n")

outFile.write("\\begin{longtable}{|l|l|c|c|c|c|c|}\n")
outFile.write("\\caption{Cases which has no gestalt score in pathogenic mutation gene} \n")
outFile.write("\\label{table:no_gestalt_sample} \\\\ \\hline \n")
outFile.write("Case&Gene&FM&CADD&Gestalt&Boqa&Pheno\\\\ \\hline \n")
filename = "../sample.csv"
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    flag = 0
    for row in reader:
        outrow = [j for i, j in enumerate(row) if i != 2]
        if flag == 1 and row[5] == 'nan':
            outFile.write("&".join(outrow) + "\\\\ \\hline \n")
        flag = 1

outFile.write("\\end{longtable}\n")

outFile.write("\\end{center}\n")
outFile.close()
