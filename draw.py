import json, os
import warnings
import numpy as np
import sys
import logging
import csv
from matplotlib import pyplot as plt

logging.basicConfig(filename='run.log', level=logging.INFO)
logger = logging.getLogger(__name__)


genepos={}
chr_sizes=[249250621, 243199373, 198022430, 191154276, 180915260, 171115067, 159138663, 146364022, 141213431, 135534747, 135006516, 133851895, 115169878, 107349540, 102531392, 90354753, 81195210, 78077248, 59128983, 63025520, 48129895, 51304566, 155270560, 59373566, 16571]

def loadPosition():

    for line in open('allgenepositions.txt'):
        fields = line[:-1].split('\t')
        nm = fields[0]
        chro = fields[1]
        pos = fields[2]
        name = fields[3]
        if name not in genepos:
            genepos[name] = [chro, pos]

def manhattan(pedia, path, ID='all'):
    """ Displays the information in Data as a manhattan plot. If the optional variable ID is set
    to a string matching a case ID, only the results of this case will be displayed."""

    if not genepos:
        loadPosition()

    for case in pedia:
        sanos = []
        sanos2 = []
        pathos = []
        s_pos = []
        s_pos2 = []
        p_pos = []
        names = []
        names_x = []
        names_y = []
        if case == ID or ID == 'all':
            smpl_case = case
            score = np.array(pedia[case][0])
            pathogenicity = np.array(pedia[case][1])
            gene = np.array(pedia[case][2])
            length = len(score)

            for index in range(length):
                gene_symbol = gene[index]
                patho = pathogenicity[index]
                sc = score[index]

                if gene_symbol not in genepos and patho == 1:
                    print(gene_symbol)

                if gene_symbol in genepos:
                    chrom = genepos[gene_symbol][0][3:]
                    if chrom == 'X':
                        chrom = 23
                    elif chrom == 'Y':
                        chrom = 24
                    elif chrom == 'M':
                        chrom = 25
                    else:
                        chrom = int(chrom)

                    pos = 0
                    for i in range(chrom - 1):
                        pos += chr_sizes[i] + 10 ** 6
                    pos += int(genepos[gene_symbol][1])

                    if patho == 0:
                        if chrom % 2 == 0:
                            sanos2.append(sc)
                            s_pos2.append(pos)
                        else:
                            sanos.append(sc)
                            s_pos.append(pos)

                    if patho == 1:
                        pathos.append(sc)
                        p_pos.append(pos)
                        if gene_symbol in names:
                            for i in range(len(names)):
                                if names[i] == gene_symbol:
                                    if names_y[i] < sc:
                                        names_y[i] = sc
                        if gene_symbol not in names:
                            names.append(gene_symbol)
                            names_x.append(pos)
                            names_y.append(sc)

            plt.figure(figsize=(32, 16))
            plt.scatter(s_pos, sanos, color='#70ACC0', alpha=0.6, marker='o', s=200, label=('neutrals')) #s=30
            plt.scatter(s_pos2, sanos2, color='#008B8B', alpha=0.6, marker='o', s=200, label=('neutrals')) #s=30  #385660
            plt.scatter(p_pos, pathos, color='red', marker='o', s=200, label='pathogenic') #s=30

            for i in range(len(names)):
                plt.annotate(names[i], xy = (names_x[i], names_y[i]), xytext = (names_x[i], names_y[i]), fontsize=50, color='#AA1C7D')
            plt.xlabel('chromosomal position', fontsize=28)

            ticks = []
            tick = 0
            for i in chr_sizes:
                tick += i / 2
                ticks.append(tick)
                tick += (i / 2) + 10 ** 6
            plt.xticks(ticks)
            plt.ylabel('pedia score', fontsize=38)
            plt.legend(loc='upper left', fontsize=25)
            frame1 = plt.gca()
            chr_names = []

            for i in range(1,26):
                if i == 23:
                    chr_names.append('X')
                elif i == 24:
                    chr_names.append('Y')
                elif i == 25:
                    chr_names.append('M')
                else:
                    chr_names.append(str(i))

            frame1.axes.xaxis.set_ticklabels(chr_names, fontsize=25)
            frame1.axes.tick_params(axis='x',length=0)
            frame1.axes.tick_params(axis='y', labelsize=25)
            y_min = min([min(sanos), min(sanos2), min(pathos)])
            y_max = max([max(sanos), max(sanos2), max(pathos)])
            plt.ylim(y_min, y_max+(y_max/10)) #ymin-(ymax/30)
            plt.xlim(0, ticks[-1]+(chr_sizes[-1]/2)+10**6)
            plt.title(ID)
            filename = path + "/manhattan_" + ID + ".png"
            plt.savefig(filename)



def rank(pedia, col, lab, path, score='pedia'):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # col is the color of the plot
    # lab is the label of the plot

    print('ranking results based on', lab)

    # a list that will contain lists of the IDs of each case and the rank of the respective pathogenic
    # variant, ranked by the pedia-score
    combined_rank = []
    #n_cases = len(self.casedisgene)

    combined_performance = []
    # will evalute ranks in range 0 to 101)
    counts = []
    filename = path + '/rank_gene_' + lab + ".csv"
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        for i in range(101):
            count = 0
            for case in pedia:
                if pedia[case][1][i] == 1:
                    count += 1
                    writer.writerow([case, i])
            counts.append(count)
                # the absolute number is divided by the total number of cases, so that one has the
                # fraction of cases having a patho rank not higher than i
                # appends sens to i, so that combined rank is a list of floats, each float describing
                # the fraction of cases that have a pathorank lower or eqaul to its index
                #combined_performance.append(sens)

    total = len(pedia)
    tmp = 0

    filename = path + '/rank_' + lab + ".csv"
    with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile)
        rank = 1
        for count in counts:
            writer.writerow([rank, count])
            rank += 1
            tmp += count
            combined_performance.append(tmp / total)



    plt.figure(figsize=(18, 12))
    plt.plot(range(1, len(combined_performance)), combined_performance[0:], color=col, alpha=0.6, label=lab, linewidth=3)
    plt.scatter([1, 10, 100], [combined_performance[0], combined_performance[9], combined_performance[99]], color=col, alpha=0.6, marker='o', s=50)
    print(lab, [combined_performance[0], combined_performance[9], combined_performance[99]])
    #print(lab,[combined_performance[1],combined_performance[10],combined_performance[100]],'fraction passed filter:',(npf/n_cases))

    #the last lines of code are only needed to display the results
    plt.ylim(0, 1.01)
    plt.xlim(0, 100.5)
    plt.xlabel('rank-cut-off', fontsize=30)
    plt.ylabel('Sensitivity', fontsize=30)
    plt.title('Sensitivity-rank-cut-off-correlation', fontsize=30)
    plt.legend(loc='lower right', fontsize=30)
    filename = path + "/rank_" + lab + ".png"
    plt.savefig(filename)

