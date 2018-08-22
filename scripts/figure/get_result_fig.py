import csv
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


case_list=[]

output_dir = '../../latex/table/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
input_dir =['../../output']
#input_dir =['../../output/cv', '../../output/cv_g']
caption = ['all cases']
data_type = ["1KG", "ExAC", "IRAN"]

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
    for cv_idx in range(7):
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
        col2 = 'blue' 
        plt.figure(figsize=(18, 12))
        plt.xticks(np.array(range(1, len(case_list)+1)), case_list)
        #plt.plot(range(1, len(case_list)+1), cv_rank[0:len(case_list)], color=col, alpha=0.6, label=lab, linewidth=3)
        #plt.scatter([1, 10, 100], [combined_performance[0], combined_performance[9], combined_performance[99]], color=col, alpha=0.6, marker='o', s=50)
        plt.yticks(np.arange(0, 200, 5))
        plt.bar(np.array(range(1, len(case_list)+1)), np.array(cv_rank), color=col, alpha=0.6, label=lab, linewidth=3)
        plt.bar(np.array(range(1, len(case_list)+1)), np.array(real_rank), color='blue', alpha=0.6, label=lab2, linewidth=3)
        plt.grid(axis='y', linestyle='-')

        plt.xlabel('Case ID', fontsize=30)
        plt.ylabel('Rank', fontsize=30)
        plt.title('Rank of simulated on ' + name + ' and real exome ', fontsize=30)
        plt.legend(loc='upper left', fontsize=30)
        filename = "simulated_real_" + name + ".png"
        plt.savefig(filename)
        plt.close()

