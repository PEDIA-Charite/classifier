#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import os
import csv  # necessary for creating genedict
import getopt
import pandas as pd

# ===============================
# ===== main script =============
# ===============================


def mapping(filename, newpath, pedia_path, config_data=None):
    results = []
    f_prefix = filename.split('/')[-1].split('.')[0]
    pedia = []
    df = pd.read_csv(pedia_path)
    with open(filename) as f:
        file_content = json.load(f)

    file_content['pedia'] = json.loads(df.to_json(orient='records'))
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
