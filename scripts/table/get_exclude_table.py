import csv
import sys
import os
FEATURE = ["0", "1", "2", "3", "4", "0_1", "0_2", "0_3", "0_4", "1_2", "1_3", "1_4",
            "2_3", "2_4", "3_4", "0_1_2", "0_1_3", "0_1_4", "0_2_3", "0_2_4", "0_3_4",
            "1_2_3", "1_2_4", "1_3_4", "2_3_4", "0_1_2_3", "0_2_3_4", "0_1_3_4", "0_1_2_4", "1_2_3_4"]

f_name = {'0':'F', '1':'C', '2':'G', '3':'B', '4':'P'}

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

outFile = open(output_dir + 'acc_exclude_result.tex', "w")
#Output text

data_type = ["1KG", "ExAC", "IRAN"]
rank_idx = ["1", "2-10", "11-99", "100+"]
e_nums = [1, 2, 3, 4]
e_idx = {0:'1', 5:'2', 15:'3', 25:'4'}
print_idx = [4, 14, 24, 29]
input_dirs = ['../../output/exclude/']
#input_dirs = ['../../output/exclude/', '../../output/exclude_g/']
label = ['table:exclude_', 'table:exclude_g_']
caption = ['using all cases on ', 'using the cases with gestalt score on ']
for input_idx, input_dir in enumerate(input_dirs):
    for name in data_type:
        outFile.write("\\begin{center}\n")
        outFile.write("\\begin{table}[ht]\n")
        outFile.write("\\caption{Result of 10-fold cross validation " + caption[input_idx] + name + " data set. The first column is the feature (s) we exclude. We divide the rows into 4 groups by the number of feature we exclude. In each column, we boldface the value which gives the best and worst cumulative percentage of mutation genes in the group.}\\medskip\n")
        outFile.write("\\label{" + label[input_idx] + name +"}\n")
        outFile.write("\\begin{tabular}{|l|c|c|c|c|c|c|c|c|} \\hline\n")
        outFile.write("&\\multicolumn{2}{|c|}{1}&\\multicolumn{2}{|c|}{2-10}&\\multicolumn{2}{|c|}{11-99}&\\multicolumn{2}{|c|}{100+}\\\\ \\hline \n")
        outFile.write("Feature&Count&Cumu(\%)&Count&Cumu(\%)&Count&Cumu(\%)&Count&Cumu(\%)\\\\ \\hline \n")
        for idx, feature in enumerate(FEATURE):
            counts = []
            if idx in e_idx:
                total_count = []
                bold_num = []
                e_name_list = []
                total_rank = []
                perc = []
                outFile.write("\\multicolumn{9}{|c|}{Exclude " + e_idx[idx] +  " feature} \\\\ \\hline \n")

            filename = input_dir + "CV_" + name + "_e_" + feature + "/rank_" + name + ".csv"
            with open(filename) as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    counts.append(float(row[1]))
            total_count.append(counts)
            feature = feature.replace('_', '-')
            e_names = feature.split('-')

            e_list = []
            for e in e_names:
                e_list.append(f_name[e])
            e_name = ','.join(e_list)
            e_name_list.append(e_name)

            total = sum(counts[0:100])
            total_rank.append([counts[0], round(sum(counts[1:10]), 2), round(sum(counts[10:99]), 2), round( counts[99], 2)])
            perc.append([round(counts[0]/total*100, 2), round(sum(counts[0:10])/total*100, 2), round(sum(counts[0:99])/total*100, 2), round(sum(counts[0:100])/total*100, 2)])

            if idx in print_idx:
                for num in range(4):
                    tmp = [j[num] for i, j in enumerate(perc)]
                    m = max(tmp)
                    bold_tmp = [i for i, j in enumerate(tmp) if j == m]
                    m = min(tmp)

                    for i, j in enumerate(tmp):
                        if j == m:
                            bold_tmp.append(i)
                    bold_num.append(bold_tmp)
                for i in range(len(total_rank)):
                    bold_str = ["", "", "", ""]
                    for num in range(len(total_rank[0])):
                        if i in bold_num[num]:
                            bold_str[num] = '\\bf'
                    outFile.write(e_name_list[i] + "&" + bold_str[0] + str(total_rank[i][0]) + "&" + bold_str[0] + str(perc[i][0]) + "&" + bold_str[1] + str(total_rank[i][1]) + "&" + bold_str[1] + str(perc[i][1])+ "&" + bold_str[2] + str(total_rank[i][2]) + "&" + bold_str[2] + str(perc[i][2])+ "&" + bold_str[3] + str(total_rank[i][3])+ "&" + bold_str[3] + str(perc[i][3]) + "\\\\ \\hline \n")

        outFile.write("\\end{tabular}\n")
        outFile.write("\\end{table}\n")

        outFile.write("\\end{center}\n")
outFile.close()

