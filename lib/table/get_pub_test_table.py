import csv
import sys
import os
import numpy as np
import pandas as pd
from statistics import mean
from statistics import stdev
from scipy.stats import sem, t
from scipy import mean

################################################################3
# It is for generating the Sup table 3
#############################################################33333333333333333333

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
outFile = open(output_dir + 'acc_pub_test.tex', "w")
input_dir =['../../output/publication_simulation_test/1KG/']

############################################################################
# output header of table
###############################################################################

outFile.write("\\begin{longtable}[ht]{|c|p{3.4cm}|p{8.4cm}|c|c|}\n")
outFile.write("\\caption{Comparision of results by using DeepGestalt and PEDIA on DeepGestalt publication test set. The PEDIA rank is the average rank.}\\\\  \\hline\n")
outFile.write("Index&Syndrome Name&Photo Link&DeepGestalt&PEDIA\\\\ \\hline \n")

############################################################################
# Parse CV_g - 10 fold CV with gestalt support cases
###############################################################################

cv_dir = input_dir[0]
# init
ranks = []
for i in range(1, 330):
    ranks.append(np.array([0]*10))

# Paring results
for j in range(10):
    filename = cv_dir + "/REP_" + str(j) + "/rank.csv"
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            case_id = int(row[0].split('_')[1])
            ranks[case_id-1][j] = int(row[1])
            if int(row[1]) > 50:
                print(j)
                print(row)
med_ranks = np.mean(np.array(ranks), axis=1)
print(med_ranks)

df = pd.read_csv('../../../DG_pub.csv')
df['PEDIA Rank'] = med_ranks
#df = df[df['PEDIA Rank'] > 0]
print(df.loc[23])
for i in range(df.shape[0]):
    x = df.loc[i]
    if x['PEDIA Rank'] == 0:
        continue
    outFile.write(str(x['Index']) + "&" + x['Syndrome Name'].replace('\n', ' ') + "&" + x['Links'] + '&' + str(x['DeepGestalt Rank']) + '&' + str(x['PEDIA Rank']) + "\\\\ \\hline \n")





#if idx in divide_idxs:
#    outFile.write("\\multicolumn{3}{|c|}{\\textbf{" + divide_row[idx] + "}}\\\\ \\hline \n")
#outFile.write(e_name  + "&" + str(perc[0][0]) + " \\small{[" + ci[0][0]  + "]} & " + str(perc[0][1]) +
#            " \\small{[" + ci[0][1] + "]}
#
outFile.write("\\end{longtable}\n")
