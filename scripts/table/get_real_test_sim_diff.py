import csv
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


case_list=[]
filename = '../../../config.yml'
flag = False
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if flag:
            case_list.append(row[0].split('-')[1].replace(' ', ''))
        if 'VCF' in row[0]:
            flag = True
        if 'SINGLE' in row[0] or 'TEST' in row[0]:
            flag = False


output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
input_dir =['../../output']
#input_dir =['../../output/cv', '../../output/cv_g']
caption = ['all cases']
data_type = ["1KG", "ExAC", "IRAN"]

print(case_list)
#Output text
for cv_idx, cv_dir in enumerate(input_dir):
    for name in data_type:
        cv_pedia = []
        cv_rank = []
        real_rank = []
        for cv_idx in range(1):
            pedia_score = []
            real_pedia_score = []
            for case in case_list:
                pedia_file = cv_dir + "/real_simulated_test/" + name + "/" + str(case) + ".csv"
                flag = 0
                with open(pedia_file) as pedia_csv:
                    reader_2 = csv.reader(pedia_csv)
                    rank = 0
                    for row_2 in reader_2:
                        if flag == 1:
                            if int(row_2[3]) == 1:
                                pedia_score.append(float(row_2[2]))
                                cv_rank.append(rank)
                        rank = rank + 1
                        flag = 1
                pedia_file = "../../output/real_test/" + name + "/" + case + ".csv"
                flag = 0
                with open(pedia_file) as pedia_csv:
                    reader_2 = csv.reader(pedia_csv)
                    rank = 0
                    for row_2 in reader_2:
                        if flag == 1:
                            if int(row_2[3]) == 1:
                                real_pedia_score.append(float(row_2[2]))
                                real_rank.append(rank)
                        rank = rank + 1
                        flag = 1

        for idx, case in enumerate(case_list):
            log = case + ':' + str(cv_rank[idx]) + ' ' + str(real_rank[idx])
            print(log)

        lab = 'simulated'
        lab2 = 'real'
        col = 'red'
        plt.figure(figsize=(18, 12))
        plt.xticks(np.array(range(1, len(case_list)+1)), case_list)
        #plt.plot(range(1, len(case_list)+1), cv_rank[0:len(case_list)], color=col, alpha=0.6, label=lab, linewidth=3)
        #plt.scatter([1, 10, 100], [combined_performance[0], combined_performance[9], combined_performance[99]], color=col, alpha=0.6, marker='o', s=50)
        plt.yticks(np.arange(0, 200, 5))
        plt.plot(np.array(range(1, len(case_list)+1)), np.array(cv_rank), color=col, alpha=0.6, label=lab, linewidth=3)
        plt.plot(np.array(range(1, len(case_list)+1)), np.array(real_rank), color='blue', alpha=0.6, label=lab2, linewidth=3)
        plt.grid(axis='y', linestyle='-')

        plt.xlabel('Case ID', fontsize=30)
        plt.ylabel('Rank', fontsize=30)
        plt.title('Rank of simulated on ' + name + ' and real exome ', fontsize=30)
        plt.legend(loc='upper left', fontsize=30)
        filename = "simulated_real_" + name + ".png"
        plt.savefig(filename)
        plt.close()

