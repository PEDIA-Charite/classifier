#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import os
import csv  # necessary for creating genedict
import getopt

# ===============================
# ===== main script =============
# ===============================


def mapping(filename, newpath, pedia_path, config_data=None):
    results = []
    f_prefix = filename.split('/')[-1].split('.')[0]
    pedia_name = pedia_path
    pedia = []
    with open(pedia_name) as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            tmp = {}
            tmp['cadd_score'] = float(row['cadd_score'])
            tmp['boqa_score'] = float(row['boqa_score'])
            tmp['pheno_score'] = float(row['pheno_score'])
            tmp['feature_score'] = float(row['feature_score'])
            tmp['gestalt_score'] = float(row['gestalt_score'])
            tmp['pedia_score'] = float(row['pedia_score'])
            tmp['gene_id'] = int(row['gene_id'])
            tmp['gene_name'] = row['gene_name']
            pedia.append(tmp)
    with open(filename) as f:
        file_content = json.load(f)

    file_content['pedia'] = pedia
    if config_data:
        file_content['processing'].append(config_data['command'])
    # adds the genelist to the json file
    newjson = open(newpath, "w")
    json.dump(file_content, newjson)
    newjson.close()

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "h::", ["input=", "output=", "pedia="])
    for opt, arg in opts:
        if opt in ("--input"):
            filename = arg
        elif opt in ("--output"):
            newpath = arg
        elif opt in ("--pedia"):
            pedia_path = arg
    mapping(filename, newpath, pedia_path)
