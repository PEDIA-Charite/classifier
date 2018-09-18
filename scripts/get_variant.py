#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import getopt
import sys
import os
import gzip
import logging
import argparse

logger = logging.getLogger(__name__)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s', datefmt='%m-%d %H:%M')
console.setFormatter(formatter)
logger.addHandler(console)

def main():
    parser = argparse.ArgumentParser(description='Get variants in PEDIA genes')
    parser.add_argument('-i', '--input', help='path of input VCF file')
    parser.add_argument('-o', '--output', help='path of output VCF file')
    parser.add_argument('-p', '--pedia', help='path of PEDIA file')

    args = parser.parse_args()
    input_vcf = args.input
    output_vcf = args.output
    pedia_path = args.pedia

    get_variant(input_vcf, output_vcf, pedia_path)

def get_variant(input_vcf, output_vcf, pedia_path):
    # Parse gene list
    with open(pedia_path) as csvfile:
        reader = csv.DictReader(csvfile)
        gene_list = [row['gene_id'] for row in reader]

    prefix = output_vcf[0:-7]
    tmp_name = output_vcf[0:-3]
    # Filter out the variant which is not in gene list
    with gzip.open(input_vcf, 'r') as f:
        line = f.readline()
        flag = 0
        with open(tmp_name, 'w') as tmp_file:
            while line:
                line = line.decode('utf-8')
                if flag:
                    tmp = line.split('\t')
                    for info in tmp[7].split(';'):
                        if info.startswith('ANN='):
                            ann = info
                    if ann.split('|')[4] in gene_list:
                        tmp_file.write(line)
                    line = f.readline()
                else:
                    if "#CHROM" in line:
                        flag = 1
                        tmp = line.split('\t')
                        tmp[-1] = prefix
                        line = '\t'.join(tmp) + '\n'
                        tmp_file.write(line)
                        line = f.readline()
                    else:
                        tmp_file.write(line)
                        line = f.readline()
    cmd = 'bgzip ' + tmp_name
    os.system(cmd)

if __name__ == '__main__':
    main()
