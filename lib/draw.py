# -*- coding: utf-8 -*-
import os
import numpy as np
import sys
import logging
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

genepos = {}
chr_sizes = [249250621, 243199373, 198022430, 191154276, 180915260, 171115067, 159138663, 146364022, 141213431, 135534747, 135006516, 133851895, 115169878, 107349540, 102531392, 90354753, 81195210, 78077248, 59128983, 63025520, 48129895, 51304566, 155270560, 59373566, 16571]

# Setup logging
logger = logging.getLogger(__name__)
console_handle = logging.StreamHandler()
console_handle.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
console_handle.setFormatter(formatter)
logger.addHandler(console_handle)

def loadPosition(pos_file):

    for line in open(pos_file):
        fields = line[:-1].split('\t')
        nm = fields[0]
        chro = fields[1]
        pos = fields[2]
        name = fields[3]
        if name not in genepos:
            genepos[name] = [chro, pos]

def manhattan(pedia, path, pos_file, ID='all'):
    """ Displays the information in Data as a manhattan plot. If the optional variable ID is set
    to a string matching a case ID, only the results of this case will be displayed."""

    if not genepos:
        loadPosition(pos_file)

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
        np_names = []
        np_names_x = []
        np_names_y = []
        if case == ID or ID == 'all':
            smpl_case = case
            score = np.array(pedia[case]['pedia_score'])
            pathogenicity = np.array(pedia[case]['label'])
            gene = np.array(pedia[case]['gene_name'])
            length = len(score) 
            rank = 0
            for index in range(length):
                rank += 1
                gene_symbol = gene[index]
                patho = pathogenicity[index]
                sc = score[index]

                if gene_symbol not in genepos and patho == 1:
                    logger.warning("Can not find gene %s in position file.", gene_symbol)

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
                        if rank <= 10:
                            if gene_symbol in np_names:
                                for i in range(len(np_names)):
                                    if np_names[i] == gene_symbol:
                                        if np_names_y[i] < sc:
                                            np_names_y[i] = sc
                            else:
                                np_names.append(gene_symbol)
                                np_names_x.append(pos)
                                np_names_y.append(sc)


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
            plt.scatter(s_pos, sanos, color='#70ACC0', alpha=0.6, marker='o', s=160, label=('neutrals'))
            plt.scatter(s_pos2, sanos2, color='#008B8B', alpha=0.6, marker='o', s=160, label=('neutrals'))
            plt.scatter(p_pos, pathos, color='red', marker='o', s=160, label='pathogenic')
            plt.axhline(y=0, linestyle='dashed', linewidth=1)

            for i in range(len(names)):
                plt.annotate(names[i], xy = (names_x[i], names_y[i]), xytext = (names_x[i], names_y[i]), fontsize=36, color='#AA1C7D')
            for i in range(len(np_names)):
                plt.annotate(np_names[i], xy = (np_names_x[i], np_names_y[i]), xytext = (np_names_x[i], np_names_y[i]), fontsize=36, color='#AA1C7D')
            plt.xlabel('chromosomal position', fontsize=28)

            ticks = []
            tick = 0
            for i in chr_sizes:
                tick += i / 2
                ticks.append(tick)
                tick += (i / 2) + 10 ** 6
            plt.xticks(ticks)
            plt.ylabel('PEDIA score', fontsize=38)
            plt.legend(loc='best', prop={'size':23}, bbox_to_anchor=(1,0.5))
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
            if len(pathos) > 0:
                y_min = min([min(sanos), min(sanos2), min(pathos)])
                y_max = max([max(sanos), max(sanos2), max(pathos)])
            else:
                y_min = min([min(sanos), min(sanos2)])
                y_max = max([max(sanos), max(sanos2)])
            plt.ylim(y_min, y_max+(y_max/10)) #ymin-(ymax/30)
            plt.xlim(0, ticks[-1]+(chr_sizes[-1]/2)+10**6)
            plt.title(ID)
            path = os.path.join(path, 'figures')
            if not os.path.exists(path):
                os.makedirs(path)
            filename = path + "/manhattan_" + ID
            print("saving Manhatten plot at " + filename)
            plt.savefig(filename + ".svg")
            plt.close()


def manhattan_all(pedia, path, pos_file):
    """ Displays the information in Data as a manhattan plot. If the optional variable ID is set
    to a string matching a case ID, only the results of this case will be displayed."""

    if not genepos:
        loadPosition(pos_file)

    plt.figure(figsize=(32, 16))
    sanos = []
    sanos2 = []
    pathos = []
    s_pos = []
    s_pos2 = []
    p_pos = []
    names = []
    names_x = []
    names_y = []
    for case in pedia:

        smpl_case = case
        score = np.array(pedia[case]['pedia_score'])
        pathogenicity = np.array(pedia[case]['label'])
        gene = np.array(pedia[case]['gene_name'])
        length = len(score)
        for index in range(length):
            gene_symbol = gene[index]
            patho = pathogenicity[index]
            sc = score[index]

            if gene_symbol not in genepos and patho == 1:
                logger.warning("Can not find gene %s in position file.", gene_symbol)

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
                        names.append(gene_symbol + "-" + case)
                        names_x.append(pos)
                        names_y.append(sc)

    plt.scatter(s_pos, sanos, color='#70ACC0', alpha=0.6, marker='o', s=200, label=('neutrals')) #s=30
    plt.scatter(s_pos2, sanos2, color='#008B8B', alpha=0.6, marker='o', s=200, label=('neutrals')) #s=30  #385660
    plt.scatter(p_pos, pathos, color='red', marker='o', s=200, label='pathogenic') #s=30
    plt.axhline(y=0, linestyle='dashed', linewidth=1)

    for i in range(len(names)):
        plt.annotate(names[i], xy = (names_x[i], names_y[i]), xytext = (names_x[i], names_y[i]), fontsize=15, color='#AA1C7D')
    plt.xlabel('chromosomal position', fontsize=28)

    ticks = []
    tick = 0
    for i in chr_sizes:
        tick += i / 2
        ticks.append(tick)
        tick += (i / 2) + 10 ** 6
    plt.xticks(ticks)
    plt.ylabel('PEDIA score', fontsize=38)
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
    if len(pathos) > 0:
        y_min = min([min(sanos), min(sanos2), min(pathos)])
        y_max = max([max(sanos), max(sanos2), max(pathos)])
    else:
        y_min = min([min(sanos), min(sanos2)])
        y_max = max([max(sanos), max(sanos2)])
    plt.ylim(y_min, y_max+(y_max/10)) #ymin-(ymax/30)
    plt.xlim(0, ticks[-1]+(chr_sizes[-1]/2)+10**6)
    plt.title('all case')
    path = os.path.join(path, 'figures')
    if not os.path.exists(path):
        os.makedirs(path)
    filename = path + "/manhattan_all.png"
    plt.legend(loc='center left', prop={'size':23}, bbox_to_anchor=(1,0.5))
    plt.savefig(filename)
    plt.close()

def draw_rank(col, lab, path):
    """A function to evaluate (rank) the results of the classification and put into a plot.
    only to be used after data was classified."""

    # data is what is to be analyzed, it must have the structure of alldatascored in classify()
    # col is the color of the plot
    # lab is the label of the plot


    # a list that will contain lists of the IDs of each case and the rank of the respective pathogenic
    # variant, ranked by the pedia-score

    rank = []
    combined_performance = []
    filename = path + "/rank_" + lab + ".csv"

    total = 0
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rank.append(int(row[1]))
            total += int(row[1])
    c_rank = 0
    for value in rank:
        c_rank += value
        combined_performance.append(c_rank/total)

    plt.figure(figsize=(18, 12))
    plt.plot(range(1, len(combined_performance)+1), combined_performance[0:len(combined_performance)], color=col, alpha=0.6, label=lab, linewidth=3)
    plt.scatter([1, 10, 100], [combined_performance[0], combined_performance[9], combined_performance[99]], color=col, alpha=0.6, marker='o', s=50)
    logger.info("%s 1:%f 2-10:%f 100:%f", lab, combined_performance[0], combined_performance[9], combined_performance[99])

    plt.ylim(0, 1.01)
    plt.xlim(0, 100.5)
    plt.xlabel('rank-cut-off', fontsize=30)
    plt.ylabel('Sensitivity', fontsize=30)
    plt.title('Sensitivity-rank-cut-off-correlation', fontsize=30)
    plt.legend(loc='lower right', fontsize=30)
    path = os.path.join(path, 'figures')
    if not os.path.exists(path):
        os.makedirs(path)
    filename = path + "/rank_" + lab + ".png"
    plt.savefig(filename)
    plt.close()

