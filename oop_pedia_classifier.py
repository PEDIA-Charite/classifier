# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 09:56:23 2017

@author: Martin
"""

import json, os
import warnings
import numpy as np
import sys
from matplotlib import pyplot as plt
from data import Data
from sample import Sample

def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: python %s path(simulation data)' % sys.argv[0])

    path = sys.argv[1]

    print('loading 1KG')
    onekg = Data()
    onekg.load(path + '/real/train/1KG')
    onekg.numhit(0)
    print('loading ExAC')
    exac = Data()
    exac.load(path + '/real/train/ExAC')
    exac.numhit(0)
    print('loading Iranian')
    iran = Data()
    iran.load(path + '/real/train/IRAN')
    iran.numhit(0)
    print('loading test data')
    test = Data()
    test.load(path + '/real/test')
    test.numhit(0)



    print('classifying against 1KG')
    test.classify_real(onekg)
    test.ranker('red', '1KG')
    print('classifying against ExAC')
    test.classify_real(exac)
    test.ranker('blue', 'EXAC')
    print('classifying against Iranian')
    test.classify_real(iran)
    test.ranker('purple', 'Iran')
    plt.savefig('sensitivity_rank_cor.png')

    results = []
    best = [None, [0, 0, 0]]
    print('loading 1KG')
    onekg = Data()
    onekg.load(path + '/1KG/CV')
    onekg.save_SVM(C=10 ** (-1.45))
    onekg.hyper_search(start=-3, stop=3)

    #smpl = Sample()
    #smpl.boqa = 0.5
    #smpl.phenomizer = 0.7
    #smpl.cadd_phred = 17
    #smpl.feature = 0
    #smpl.gestalt = 1.5

    #smpl.classify()



    print('classifying 1KG by SVM')
    onekg.classify_10xSVM()
    onekg.manhattan('40639')
    plt.savefig('10xSVM.png')


    onekg.ranker2('red', 'PEDIA')
    onekg.classify_10xSVM_extom()
    onekg.ranker2('blue', 'extom', score = 'extom')
    onekg.compare()


    onekg.classify_10xSVM_extom()
    onekg.ranker2('blue', 'extom no filter', score = 'extom')
    onekg.ranker2('green', 'gestalt no filter', score = 'gestalt')
    onekg2 = Data()
    onekg2.load2(path + '/1KG/CV')
    print('classifying 1KG by SVM')
    onekg2.classify_10xSVM()
    onekg2.ranker2('black', 'extom  sep. loaded')
    plt.savefig('10xSVM_extom.png')

    #onekg.ranker2('purple','gestalt',score='gestalt')
    #onekg.ranker2('orange','cadd_phred',score='cadd_phred')
    onekg.filter_gestalt()
    onekg.classify_10xSVM_extom()
    onekg.ranker3('blue', 'extom post filter', score = 'extom')


    onekg = Data()
    onekg.load(path + '/real/train/1KG')
    test = Data()
    test.load(path + '/real/test')
    test.classify_real(onekg)
    test.ranker2('red', 'PEDIA')
    onekg.filter_gestalt()
    test.classify_real(onekg)
    test.ranker2('blue', 'extom')
    plt.show()


    onekgnum = Data()
    onekgnum.load(path + '/1KG/CV')
    onekgnum.numhit(2)
    print('classifying 1KGnum by SVM')
    onekgnum.classify_10xSVM()
    onekgnum.ranker3('green', 'PEDIA num')
    onekgnum.filter_gestalt()
    onekgnum.classify_10xSVM_extom()
    onekgnum.ranker3('orange', 'extomnum', score = 'extom')


    onekg.compare()
    plt.show()

    scores=[[30, 0], [7, 0], [346, 0], [9, 0], [65, 0], [39, 0], [87, 0], [124, 0], [39, 1], [30, 0], [-1, 0]]
    scores.sort()
    scores.reverse()

    print(list(enumerate(scores)))


    print('loading 1KG')
    onekg = Data()
    onekg.load(path + '/1KG/CV')
    onekg.numhit(0)
    print('loading ExAC')
    exac = Data()
    exac.load(path + '/ExAC/CV')
    exac.numhit(0)
    print('loading Iranian')
    iran = Data()
    iran.load(path + '/IRAN/CV')
    iran.numhit(0)
    print('classifying 1KG')
    onekg.classify_10xSVM()
    onekg.ranker('red','1KG')
    print('classifying ExAC')
    exac.classify_10xSVM()
    exac.ranker('blue','EXAC')
    print('classifying Iranian')
    iran.classify_10xSVM()
    iran.ranker('purple','Iran')
    plt.show()


    test=Data()
    test.load(path + '/1KG/CV')
    test.classify_10xSVM()
    test.manhattan('97147')
    plt.show()

    os.chdir(path + '/1KG/CV')
    for i in os.listdir():
        with open(i) as json_data:
            data = json.load(json_data)
            print(data['ranks']['combined_rank'], i[:-5])

    test=Data()
    test.load(path + '/real/test')

    cases=[]
    patho=0
    for smpl in test.samples:
        if smpl.case not in cases:
            cases.append(smpl.case)
    for smpl in test.samples:
        if smpl.pathogenicity == 1:
            cases.pop(cases.index(smpl.case))


    os.chdir(path + '/real/test')
    for case in cases:
        with open(str(case)+'.json') as json_data:
            data = json.load(json_data)
            disgene=data['genomicData'][0]['Test Information']['Gene Name']
            print(disgene)
            for entry in data['geneList']:
                #print(entry['gene_symbol'])
                if entry['gene_symbol']==disgene:
                    print('here')

if __name__ == '__main__':
    main()


