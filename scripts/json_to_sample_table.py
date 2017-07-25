#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, getopt
import json
import glob
import csv
import numpy as np
import io
import logging


def main():
    # Options
    argv = sys.argv[1:]

    inputdir = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","ifile=","ofile="])
    except getopt.GetoptError:
        print('jsonToTable.py -i <input-folder> -o <output-file.tsv>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('jsonToTable.py -i <input-folder> -o <output-file.tsv>')
            sys.exit(1)
        elif opt in ("-i", "--ifolder"):
            input_dir = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input folder is ',input_dir)
    print('Output file is ',outputfile)
    parse_json(input_dir, outputfile)

# Load data and use max for duplicates
## key is sampleid_entrezid
def getKey(case, gene_id):
    return str(gene_id) + "_" + str(case)


def parse_json(input_dir, outputfile):
    hashedData = {}

    for filename in glob.glob(input_dir+'/*.json'):
        found = False
        geneIDs = []
        r = io.open(filename,'r',encoding='ISO-8859-1')
        data = json.loads(r.read())
        case = data['case_id']
        gene = data["genomicData"][0]["Test Information"]["Gene Name"]
        syn = data["ranks"]["syndrome_name"]
        if gene == 'MLL2':
            gene = 'KMT2D'
        elif gene == 'MLL':
            gene = 'KMT2A'
        elif gene == 'B3GALTL':
            gene = 'B3GLCT'
        elif gene == 'CASKIN1':
            gene = 'KIAA1306'
        for entry in data['geneList']:
            if entry["gene_symbol"] == gene:
                found = True
                geneID = entry['gene_id']
                geneIDs.append(geneID)
                geneSymbol = entry['gene_symbol']
                featureScore = entry.get("feature_score", np.nan)
                caddPhredScore = entry.get("cadd_phred_score", np.nan)
                gestaltScore = entry.get("gestalt_score", np.nan)
                boqaScore = entry.get("boqa_score", np.nan)
                phenoScore = entry.get("pheno_score", np.nan)

                if getKey(case, geneID) in hashedData:
                    value = hashedData[getKey(case,geneID)]
                    featureScore = max(featureScore,value["feature_score"])
                    caddPhredScore = max(caddPhredScore,value["cadd_phred_score"])
                    gestaltScore = max(gestaltScore,value["gestalt_score"])
                    boqaScore = max(boqaScore,value["boqa_score"])
                    phenoScore = max(phenoScore,value["pheno_score"])

                hashedData[getKey(case,geneID)] = {"case": case, "gene_symbol": geneSymbol, "syndrome": syn, "feature_score": round(featureScore, 3), "cadd_phred_score": round(caddPhredScore, 3), "gestalt_score":  round(gestaltScore, 3), "boqa_score": round(boqaScore, 3), "pheno_score": round(phenoScore, 3)}

        if not found:
            print("problem with", case, gene)
            for geneID in geneIDs:
                if getKey(case, geneID) in hashedData:
                    del hashedData[getKey(case,geneID)]

    key_list = [k for k in hashedData.keys()]
    key_list.sort()

    with open(outputfile, 'w') as csvfile:
        fieldnames = ["case", "gene_symbol", "syndrome", "feature_score", "cadd_phred_score", "gestalt_score", "boqa_score", "pheno_score"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key in key_list:
            writer.writerow(hashedData[key])
        #for key, value in hashedData.items():
        #	writer.writerow(value)


if __name__ == '__main__':
    main()
