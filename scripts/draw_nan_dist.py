import os
import sys
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import collections

# This script is to check the nan distribution on all feature vector.
# the output files will be in output/nan_dist/'name you type in argument'
# nan_dist.png and pa_nan_dist.png are the figures which show the distribution
# of nan frequency.
# The prefix 'pa' means that it is for pathogenic gene.
# nan_feature.png and pa_nan_feature.png are the figures which show the number
# of sample which don't have the corresponding feature.
# feature_count.png and pa_feature_count.png are the figures which show the
# number of sample which have the corresponding feature
# Each *.csv file has a list of sample and gene which have the corresponding
# feature.

def autolabel(rects, ax):
    # Get y-axis height to calculate label position from.
    (y_bottom, y_top) = ax.get_ylim()
    y_height = y_top - y_bottom

    for rect in rects:
        height = rect.get_height()

        # Fraction of axis height taken up by this rectangle
        p_height = (height / y_height)

        # If we can fit the label above the column, do that;
        # otherwise, put it inside the column.
        if p_height > 0.95: # arbitrary; 95% looked good to me.
            label_position = height - (y_height * 0.05)
        else:
            label_position = height + (y_height * 0.01)

        ax.text(rect.get_x() + rect.get_width()/2., label_position, '%d' % int(height), ha='center', va='bottom')


def freqDist(x, y, xticks, filename, title, xlabel, total_count):
    # Draw nan distribution
    fig, ax = plt.subplots()
    width = 0.75
    rect = ax.bar(x, y, width, color='r')
    ax.set_xticks(x)
    ax.set_xticklabels(xticks)

    plt.title("Nan distribution on " + title + ", total:" + str(total_count))
    plt.xlabel(xlabel)
    plt.ylabel("Number of gene")

    autolabel(rect, ax)

    plt.savefig(filename)


# input file is the csv file which is generated from jsonToTable.py
input_file = sys.argv[1]
output_dir = "../output/nan_dist/" + sys.argv[2] + "/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

nan_count_list = []
pa_nan_count_list = []


pa_nan = [0, 0, 0, 0, 0, 0]
nan = [0, 0, 0, 0, 0, 0]

feature_count = [0, 0, 0, 0, 0, 0]
pa_feature_count = [0, 0, 0, 0, 0, 0]
feature_compact = [[], [], [], [], [], []]
pa_feature_compact = [[], [], [], [], [], []]


with open(input_file) as csvfile:
    reader = csv.DictReader(csvfile)
    case = ""
    data = {}

    g_count = 0
    total_count = 0
    total_pa_count = 0

    for row in reader:
        case = row["case"]
        if not case in data:
            data.update({case:[[], [], []]})

        x = data[case][0]
        y = data[case][1]

        gene = data[case][2]

        feature = [row["feature_score"], row["cadd_phred_score"], row["combined_score"], row["gestalt_score"], row["boqa_score"], row["pheno_score"]]
        x.append(feature)
        y.append(int(row["label"]))

        gene.append(row["gene_symbol"])
        nan_count = np.count_nonzero(np.isnan(np.array(feature).astype(float)))
        nan_count_list.append(nan_count)
        if int(row["label"]) == 1:
            pa_nan_count_list.append(nan_count)
            total_pa_count += 1
            for index in range(6):
                if feature[index] == 'nan':
                    pa_nan[index] += 1
                else:
                    pa_feature_count[index] += 1
                    pa_feature_compact[index].append(case+","+row["gene_symbol"])

        for index in range(6):
            if feature[index] == 'nan':
                nan[index] += 1
            else:
                feature_count[index] += 1
                feature_compact[index].append(case+","+row["gene_symbol"])

        total_count += 1
        if row["gestalt_score"] != 'nan':
            g_count += 1

    num = 0
    for key in data:
        num += 1
        x = data[key][0]
        y = data[key][1]
        if y.count(1) > 1:
            print(key)
        x = np.array(x)
        y = np.array(y)
        data[key][0] = x
        data[key][1] = y

print(pa_nan)
print("Total: gene and case:" + str(total_count))
print("Number of gstalt:" + str(g_count))

# Freq of feature vector without corresponding number of feature
filename = output_dir + "nan_dist.png"
counter = collections.Counter(nan_count_list)
y = []
[y.append(v) for k,v in counter.items()]
x = np.arange(len(y))
xticks = x
xlabel = "Nan Frequency"
title = "Nan distribution on all gene"
freqDist(x, y, xticks, filename, title, xlabel, total_count)

filename = output_dir + "pa_nan_dist.png"
counter = collections.Counter(pa_nan_count_list)
y = []
[y.append(v) for k,v in counter.items()]
x = np.arange(len(y))
xticks = x
xlabel = "Nan Frequency"
title = "Nan distribution on pathogenic gene"
freqDist(x, y, xticks, filename, title, xlabel, total_pa_count)

# Freq of feature vector without corresponding featrue
filename = output_dir + "nan_feature.png"
y = nan
x = np.arange(len(y))
xticks = ['feature', 'CADD', 'combined', 'gstalt', 'boqa', 'phenomize']
xlabel = "Nan Feature"
title = "Nan distribution on all gene"
freqDist(x, y, xticks, filename, title, xlabel, total_count)

y = pa_nan
x = np.arange(len(y))
filename = output_dir + "pa_nan_feature.png"
xlabel = "Nan Feature"
title = "Nan distribution on pathogenic gene"
freqDist(x, y, xticks, filename, title, xlabel, total_pa_count)

# Freq of feature vector with corresponding featrue
filename = output_dir + "feature_count.png"
y = feature_count
x = np.arange(len(y))
xlabel = "Feature"
title = "Feature distribution on all gene"
freqDist(x, y, xticks, filename, title, xlabel, total_count)

filename = output_dir + "pa_feature_count.png"
y = pa_feature_count
x = np.arange(len(y))
xlabel = "Feature"
title = "Feature distribution on pathogenic gene"
freqDist(x, y, xticks, filename, title, xlabel, total_pa_count)

# Save the list of feature vector which has the corresponding feature
filename = ["feature.csv", "cadd.csv", "", "", "boqa.csv", "phenomize.csv"]
index_list = [0, 1, 4, 5]
for index in index_list:
    with open(output_dir + filename[index], 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for item in feature_compact[index]:
            writer.writerow([item])

filename = ["feature.csv", "cadd.csv", "", "", "boqa.csv", "phenomize.csv"]
index_list = [0, 1, 4, 5]
for index in index_list:
    with open(output_dir + "pa_" + filename[index], 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for item in pa_feature_compact[index]:
            writer.writerow([item])
