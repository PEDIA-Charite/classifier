import csv
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

output_dir = '../../latex/figures/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
#input_dir =['../../output/testing_folder/cv_param_rbf_linear_tuning_loss']
input_dir =['../../classifier_1/output/cv_param_tuning_linear']
#input_dir =['../../output/cv', '../../output/cv_g']
caption = ['all cases']
data_type = ["1KG"]
repetition = 1
PARAM_C = [pow(2,i) for i in range(-3,12)]
PARAM_G = [pow(2,i) for i in range(-8,3)]
tuning_set = []
top_1_data = []
top_10_data = []
#Output text
for cv_idx, cv_dir in enumerate(input_dir):
    for name in data_type:
        total_rep = []
        for c, c_value in enumerate(PARAM_C):
            tmp = 0
            total_top1 = []
            total_top10 = []
            for idx in range(repetition):
                filename = cv_dir + '/cv_' + str(idx) + '/param_' + str(c) + '/rank.csv'
                with open(filename, 'r') as csvfile:
                    reader = csv.reader(csvfile)
                    count = 0
                    rank = 0
                    for row in reader:
                        count += int(row[1])
                        if rank == 0:
                            total_top1.append(count)
                        elif rank == 9:
                            total_top10.append(count)
                        rank += 1
            total_rep.append([[i/count for i in total_top1], [i/count for i in total_top10]])
        print(total_rep)
        print(len(total_rep))
        avg1 = [sum(x[0])/repetition for x in total_rep] 
        avg10 = [sum(x[1])/repetition for x in total_rep]
        print(avg1)
        print(avg10)
        lab = 'top1'
        lab2 = 'top10'
        col = 'red'
        col2 = 'blue' 
        plt.figure(figsize=(18, 12))
        plt.xticks(PARAM_C)
        plt.yticks(np.arange(0, 1, 0.01))
        plt.plot(np.array(PARAM_C), np.array(avg1), color=col, alpha=0.6, label=lab, linewidth=3)
        plt.plot(np.array(PARAM_C), np.array(avg10), color='blue', alpha=0.6, label=lab2, linewidth=3)
        plt.grid(axis='y', linestyle='-')
        plt.xscale('log', basex=2)


        plt.xlabel('Parameter C', fontsize=30)
        plt.ylabel('Rank', fontsize=30)
        plt.title('Rank of using different parameter C', fontsize=30)
        plt.legend(loc='upper left', fontsize=30)
        filename = "rank_1KG_param_C.png"
        plt.savefig(filename)
        plt.close()

