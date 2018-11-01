import csv
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from statistics import mean
from statistics import stdev
import pandas as pd


case_list=[]
filename = '../../../config_gestalt.yml'
flag = False
with open(filename) as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if 'SINGLE' in row[0] or 'TEST' in row[0]:
            flag = False
        if flag:
            print(row[0])
            case_list.append(row[0].split('-')[1].replace(' ', ''))
        if 'VCF' in row[0]:
            flag = True


output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
input_dir =['../../output']
caption = ['all cases']
data_type = ["1KG", "IRAN"]

print(case_list)
#Output text
for cv_idx, cv_dir in enumerate(input_dir):
    for name in data_type:
        cv_pedia = []
        total_cv_rank = []
        total_real_rank = []
        for case in case_list:
            cv_rank = []
            real_rank = []
            pedia_score = []
            real_pedia_score = []
            for cv_idx in range(10):
                pedia_file = cv_dir + "/real_simulated_test_g_paper/" + name + "/" + str(cv_idx) + "/" + str(case) + ".csv"
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
                pedia_file = "../../output/real_test_g/" + name + "/" + str(cv_idx) + '/' + case + ".csv"
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
            total_cv_rank.append(cv_rank)
            total_real_rank.append(real_rank)
        print(total_real_rank)
        #for idx, case in enumerate(case_list):
        #    log = case + ':' + str(cv_rank[idx]) + ' ' + str(real_rank[idx])
        #    print(log)
        data = []
        data.append([mean(x) for x in total_cv_rank])
        data.append([mean(x) for x in total_real_rank])
        df = pd.DataFrame(data, index = ['Simulated', 'Real'], columns = case_list).T
        data = []
        data.append([stdev(x) for x in total_cv_rank])
        data.append([stdev(x) for x in total_real_rank])
        df_err = pd.DataFrame(data, index = ['Simulated', 'Real'], columns = case_list).T

        plt.figure(figsize=(18, 12))
        fig2,ax2 = plt.subplots()
        print(df)

        df.plot(kind='bar',yerr=df_err, ax=ax2, figsize=(18, 12), rot=0, fontsize=18)
        #print(total_cv_rank[1])
        #print(total_real_rank[1])
        #lab = 'simulated exome'
        #lab2 = 'real exome'
        #col = 'red'
        #col2 = 'blue' 
        #plt.figure(figsize=(18, 12))
        #fig2,ax2 = plt.subplots()

        #plt.xticks(np.array(range(1, len(case_list)+1)), case_list)
        #plt.yticks(np.arange(0, 200, 1))
        #plt.bar(np.array(range(1, len(case_list)+1)), np.array(cv_rank), color=col, alpha=0.6, label=lab, linewidth=3)
        #plt.bar(np.array(range(1, len(case_list)+1)), np.array(real_rank), color='blue', alpha=0.6, label=lab2, linewidth=3)
        plt.grid(axis='y', linestyle='-')

        plt.xlabel('Case ID', fontsize=30)
        plt.ylabel('Rank', fontsize=30)
        plt.title('Rank of simulated on ' + name + ' and real exome ', fontsize=30)
        plt.legend(loc='upper right', fontsize=30)
        filename = "simulated_real_" + name + ".png"
        plt.savefig(filename)
        plt.close()

