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


if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], "h::", ["input=", "output=", "pedia="])
    for opt, arg in opts:
        if opt in ("--input"):
            filename = arg
        elif opt in ("--output"):
            newpath = arg
        elif opt in ("--pedia"):
            pedia_path = arg
    results = []
    defaultfeatures = ["combined_score",
                       "feature_score", "gestalt_score", "has_mask"]
    f_prefix = filename.split('/')[-1].split('.')[0]
    pedia_name = pedia_path
    pedia = {}
    with open(pedia_name) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            pedia.update({row['gene_id']:row['pedia_score']})
    file_content = json.load(open(filename))
    result = [] 
    result.append(filename)
    result.append(file_content['genomicData'])
    results.append(result)
    geneList = []
    file_content["genomicData"] = result
    for gene_entry in file_content["geneList"]:
        gene_id = gene_entry['gene_symbol']
        score = pedia[gene_id]
        gene_entry.update({'pedia_score':score})
        geneList.append(gene_entry)

    # adds the genelist to the json file
    file_content["gene_list"] = geneList
    submitter = file_content['submitter']
    submitter_out = {'user_email':submitter['user_email'], 'user_name':submitter['user_name'], 'user_team':submitter['user_team']}
    file_content['submitter'] = submitter_out
    newjson = open(newpath, "w")
    json.dump(file_content, newjson)
