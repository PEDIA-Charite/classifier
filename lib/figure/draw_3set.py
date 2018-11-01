import os
import numpy as np
import sys
import csv
from matplotlib import pyplot as plt


# data is what is to be analyzed, it must have the structure of alldatascored in classify()
# col is the color of the plot
# lab is the label of the plot


labs = ["1KG", "ExAC", "IRAN"]
cols = ['red','blue','green']
markers = ['o', 'D', '^']

# will evalute ranks in range 0 to 101)
counts = []

output_list = []
for lab in labs:
    total_count = 0
    performance = []
    filename = lab + '_cv_g/rank_' + lab + "_cv_g.csv"
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            total_count += int(row[1])
            performance.append(total_count)

    output_list.append([x / total_count for x in performance])

plt.figure(figsize=(18, 12))
for index in range(3):
    plt.plot(range(1, len(output_list[index])+1), output_list[index][0:len(output_list[index])], color=cols[index], label=labs[index], linewidth=3)
    plt.scatter([1, 10, 100], [output_list[index][0], output_list[index][9], output_list[index][99]], color=cols[index], alpha=0.6, marker=markers[index], s=50)

plt.tick_params(labelsize=20)
#the last lines of code are only needed to display the results
plt.ylim(0, 1.01)
plt.xlim(0, 100.5)
plt.xlabel('rank-cut-off', fontsize=30)
plt.ylabel('Sensitivity', fontsize=30)
plt.title('Sensitivity-rank-cut-off-correlation', fontsize=30)
plt.legend(loc='lower right', fontsize=30)
filename = "rank_cv_g.png"
plt.savefig(filename)

