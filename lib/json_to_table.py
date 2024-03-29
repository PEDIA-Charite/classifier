#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, getopt
import json
import glob
import csv
import numpy as np
import io
import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
console.setFormatter(formatter)
logger.addHandler(console)

def main():
    # Options
    argv = sys.argv[1:]

    inputdir = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["help","ifile=","ofile="])
    except getopt.GetoptError:
        logger.err('jsonToTable.py -i <input-folder> -o <output-file.tsv>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            logger.err('jsonToTable.py -i <input-folder> -o <output-file.tsv>')
            sys.exit(1)
        elif opt in ("-i", "--ifolder"):
            input_dir = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    logger.info('Input folder is ', input_dir)
    logger.info('Output file is ', outputfile)
    parse_json(input_dir, outputfile)

# Load data and use max for duplicates
## key is sampleid_entrezid
def getKey(case, gene_id):
    return str(case) + "_" + str(gene_id)

def parse_csv(input_dir, outputfile):
    hashedData = {}
    file_array = []
    is_folder = os.path.isdir(input_dir)
    if is_folder == True:
        for filename in glob.glob(input_dir+'/*.csv'):
            file_array.append(filename)
    else:
        file_array.append(input_dir)
    gene_name_flag = False
    if 'amelie' in input_dir or 'xrare' in input_dir:
        gene_name_flag = True

    for filename in file_array:
        logger.info("Parsing %s", filename)
        found = False
        geneIDs = []
        data = pd.read_csv(filename)
        case = os.path.basename(filename).split('.')[0]
        gene = ""
        disease_gene_df = data[data.label == True]
        if len(disease_gene_df):
            gene = disease_gene_df.gene_id.values[0]
            gene_name = disease_gene_df.gene_name.values[0]
        for _, entry in data.iterrows():
            if gene != "":
                if gene_name_flag:
                    if entry["gene_name"] == gene_name:
                        label = 1
                        found = True
                    else:
                        label = 0
                else:
                    if int(entry["gene_id"]) == int(gene):
                        label = 1
                        found = True
                    else:
                        label = 0
            else:
                label = 0
            if gene_name_flag:
                geneID = entry['gene_id']
            else:
                geneID = int(entry['gene_id'])
            geneIDs.append(geneID)
            geneSymbol = entry['gene_name']
            featureScore = entry.get("feature_score", np.nan)
            caddPhredScore = entry.get("cadd_score", np.nan)
            combinedScore = entry.get("combined_score", np.nan)
            caddRawSscore = entry.get("cadd_raw_score", np.nan)
            gestaltScore = entry.get("gestalt_score", np.nan)
            boqaScore = entry.get("boqa_score", np.nan)
            phenoScore = entry.get("pheno_score", np.nan)
            cadaScore = entry.get("cada_score", np.nan)
            liricalScore = entry.get("lirical_score", np.nan)
            xrareScore = entry.get("xrare_score", np.nan)
            exomizerScore = entry.get("exomizer_score", np.nan)
            amelieScore = entry.get("amelie_score", np.nan)
            if cadaScore < 0:
                cadaScore = 0

            if getKey(case, geneID) in hashedData:
                value = hashedData[getKey(case,geneID)]
                featureScore = max(featureScore,value["feature_score"])
                caddPhredScore = max(caddPhredScore,value["cadd_score"])
                combinedScore = max(combinedScore,value["combined_score"])
                caddRawSscore = max(caddRawSscore,value["cadd_raw_score"])
                gestaltScore = max(gestaltScore,value["gestalt_score"])
                boqaScore = max(boqaScore,value["boqa_score"])
                phenoScore = max(phenoScore,value["pheno_score"])
                cadaScore = max(cadaScore,value["cada_score"])
                liricalScore = max(gestaltScore,value["lirical_score"])
                xrareScore = max(boqaScore,value["xrare_score"])
                exomizerScore = max(phenoScore,value["exomizer_score"])
                amelieScore = max(cadaScore,value["amelie_score"])
            filter_score = caddPhredScore
            if 'amelie' in input_dir:
                filter_score = amelieScore
            if 'xrare' in input_dir:
                filter_score = xrareScore
            if 'exomiser' in input_dir:
                filter_score = exomizerScore
            if 'lirical' in input_dir:
                filter_score = liricalScore
            if 'internal' in input_dir:
                filter_score = caddPhredScore
            if pd.isna(filter_score) and int(label) == 0:
                continue
            hashedData[getKey(case,geneID)] = {"case": case, "gene_symbol": geneSymbol, "gene_id": geneID,
                                               "feature_score": featureScore, "cadd_score": caddPhredScore,
                                               "combined_score": combinedScore, "cadd_raw_score":  caddRawSscore,
                                               "gestalt_score":  gestaltScore, "boqa_score":  boqaScore,
                                               "pheno_score": phenoScore, "cada_score": cadaScore,
                                               "lirical_score": liricalScore, "xrare_score": xrareScore,
                                               "exomizer_score": exomizerScore, "amelie_score": amelieScore,
                                               "label": label}
        if not found and gene != "":
            logger.warning("Warning: Gene %s is not found in case %s", gene, case)

    with open(outputfile, 'w') as csvfile:
        fieldnames = ["case", "gene_symbol", "gene_id", "feature_score", "cadd_score", "combined_score",
                      "cadd_raw_score", "gestalt_score", "boqa_score", "pheno_score", "cada_score",
                      "lirical_score", "xrare_score", "exomizer_score", "amelie_score", "label"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in hashedData.items():
            writer.writerow(value)

def get_test_file(json_input, input_dir):
    meta = ['gene_name', 'gene_id', 'cada_score', 'cadd_score', 'gestalt_score', 'label']
    data1 = pd.json_normalize(json_input['genes'])
    file_name = json_input['case_name']
    data1.to_csv(os.path.join(input_dir, file_name) +'.csv', index=False, columns=meta)
    return file_name

def parse_json(input_dir, outputfile):
    hashedData = {}
    file_array = []
    is_folder = os.path.isdir(input_dir)
    if is_folder == True:
        for filename in glob.glob(input_dir+'/*.json'):
            file_array.append(filename)
    else:
        file_array.append(input_dir)
    gene_name_flag = False
    if 'amelie' in input_dir or 'xrare' in input_dir:
        gene_name_flag = True
    for filename in file_array:
        found = False
        geneIDs = []
        r = io.open(filename,'r',encoding='ISO-8859-1')
        data = json.loads(r.read())
        case = data['case_id']
        gene = ""
        if "genomicData" in data:
            if len(data["genomicData"]) > 0:
                gene = data["genomicData"][0]["Test Information"]["Gene ID"]
                gene_name = data["genomicData"][0]["Test Information"]["Gene Name"]

        for entry in data['geneList']:
            if gene != "":
                if gene_name_flag:
                    if entry["gene_symbol"] == gene_name:
                        label = 1
                        found = True
                    else:
                        label = 0
                else:
                    if int(entry["gene_id"]) == int(gene):
                        label = 1
                        found = True
                    else:
                        label = 0
            else:
                label = 0
            if gene_name_flag:
                geneID = entry['gene_id']
            else:
                geneID = int(entry['gene_id'])
            geneIDs.append(geneID)
            geneSymbol = entry['gene_symbol']
            featureScore = entry.get("feature_score", np.nan)
            caddPhredScore = entry.get("cadd_score", np.nan)
            combinedScore = entry.get("combined_score", np.nan)
            caddRawSscore = entry.get("cadd_raw_score", np.nan)
            gestaltScore = entry.get("gestalt_score", np.nan)
            boqaScore = entry.get("boqa_score", np.nan)
            phenoScore = entry.get("pheno_score", np.nan)
            cadaScore = entry.get("cada_score", np.nan)
            liricalScore = entry.get("lirical_score", np.nan)
            xrareScore = entry.get("xrare_score", np.nan)
            exomizerScore = entry.get("exomizer_score", np.nan)
            amelieScore = entry.get("amelie_score", np.nan)

            if getKey(case, geneID) in hashedData:
                value = hashedData[getKey(case,geneID)]
                featureScore = max(featureScore,value["feature_score"])
                caddPhredScore = max(caddPhredScore,value["cadd_score"])
                combinedScore = max(combinedScore,value["combined_score"])
                caddRawSscore = max(caddRawSscore,value["cadd_raw_score"])
                gestaltScore = max(gestaltScore,value["gestalt_score"])
                boqaScore = max(boqaScore,value["boqa_score"])
                phenoScore = max(phenoScore,value["pheno_score"])
                cadaScore = max(cadaScore,value["cada_score"])
                liricalScore = max(gestaltScore,value["lirical_score"])
                xrareScore = max(boqaScore,value["xrare_score"])
                exomizerScore = max(phenoScore,value["exomizer_score"])
                amelieScore = max(cadaScore,value["amelie_score"])
            hashedData[getKey(case,geneID)] = {"case": case, "gene_symbol": geneSymbol, "gene_id": geneID,
                                               "feature_score": featureScore, "cadd_score": caddPhredScore,
                                               "combined_score": combinedScore, "cadd_raw_score":  caddRawSscore,
                                               "gestalt_score":  gestaltScore, "boqa_score":  boqaScore,
                                               "pheno_score": phenoScore, "cada_score": cadaScore,
                                               "lirical_score": liricalScore, "xrare_score": xrareScore,
                                               "exomizer_score": exomizerScore, "amelie_score": amelieScore,
                                               "label": label}
        if not found and gene != "":
            logger.warning("Warning: Gene %s is not found in case %s", gene, case)

    with open(outputfile, 'w') as csvfile:
        fieldnames = ["case", "gene_symbol", "gene_id", "feature_score", "cadd_score", "combined_score",
                      "cadd_raw_score", "gestalt_score", "boqa_score", "pheno_score", "cada_score",
                      "lirical_score", "xrare_score", "exomizer_score", "amelie_score", "label"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in hashedData.items():
            writer.writerow(value)

def parse_json_stdin(outputfile):
    hashedData = {}

    found = False
    geneIDs = []
    data = json.load(sys.stdin)
    case = data['case_id']
    gene = data["genomicData"][0]["Test Information"]["Gene ID"]

    for entry in data['geneList']:
        if gene != "" and int(entry["gene_id"]) == int(gene):
            label = 1
            found = True
        else:
            label = 0
        geneID = int(entry['gene_id'])
        geneIDs.append(geneID)
        geneSymbol = entry['gene_symbol']
        featureScore = entry.get("feature_score", np.nan)
        caddPhredScore = entry.get("cadd_phred_score", np.nan)
        combinedScore = entry.get("combined_score", np.nan)
        caddRawSscore = entry.get("cadd_raw_score", np.nan)
        gestaltScore = entry.get("gestalt_score", np.nan)
        boqaScore = entry.get("boqa_score", np.nan)
        phenoScore = entry.get("pheno_score", np.nan)

        if getKey(case, geneID) in hashedData:
            value = hashedData[getKey(case,geneID)]
            featureScore = max(featureScore,value["feature_score"])
            caddPhredScore = max(caddPhredScore,value["cadd_phred_score"])
            combinedScore = max(combinedScore,value["combined_score"])
            caddRawSscore = max(caddRawSscore,value["cadd_raw_score"])
            gestaltScore = max(gestaltScore,value["gestalt_score"])
            boqaScore = max(boqaScore,value["boqa_score"])
            phenoScore = max(phenoScore,value["pheno_score"])

        hashedData[getKey(case,geneID)] = {"case": case, "gene_symbol": geneSymbol, "gene_id": geneID, "feature_score": featureScore, "cadd_phred_score": caddPhredScore, "combined_score":  combinedScore, "cadd_raw_score":  caddRawSscore, "gestalt_score":  gestaltScore, "boqa_score":  boqaScore, "pheno_score": phenoScore, "label": label}

    if not found:
        logger.warning("Warning: Gene %s is not found in case %s", gene, case)
        for geneID in geneIDs:
            if getKey(case, geneID) in hashedData:
                del hashedData[getKey(case, geneID)]

    if not hashedData:
        logger.error("Error: There is no pathogenic mutation gene in input case")
        sys.exit("Error: There is no pathogenic mutation gene in input case")


    with open(outputfile, 'w') as csvfile:
        fieldnames = ["case", "gene_symbol", "gene_id", "feature_score", "cadd_phred_score", "combined_score", "cadd_raw_score", "gestalt_score", "boqa_score", "pheno_score", "label"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in hashedData.items():
            writer.writerow(value)


if __name__ == '__main__':
    main()
