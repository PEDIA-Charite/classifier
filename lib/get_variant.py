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
    parser.add_argument('-s', '--sample-index', type=int, default=0, help='index of sample in multi-vcf')

    args = parser.parse_args()
    input_vcf = args.input
    output_vcf = args.output
    pedia_path = args.pedia
    sample_index = args.sample_index

    get_variant(input_vcf, output_vcf, pedia_path, sample_index)

def get_variant(input_vcf, output_vcf, pedia_path, sample_index=0):
    # Parse gene list
    with open(pedia_path) as csvfile:
        reader = csv.DictReader(csvfile)
        gene_list = [row['gene_id'] for row in reader]

    prefix = output_vcf[0:-7]
    tmp_name = output_vcf[0:-3]
    sample_start_index = 9
    sample_final_index = sample_start_index + sample_index
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
                        outline = '\t'.join(tmp[0:9]) + '\t' + tmp[sample_final_index].strip('\n') + '\n'
                        #line = '\t'.join(tmp)
                        tmp_file.write(outline)
                    line = f.readline()
                else:
                    if "#CHROM" in line:
                        flag = 1
                        tmp = line.split('\t')
                        if sample_final_index >= len(tmp):
                            sample_final_index = 9
                            sample_index = 0
                        sample_name = tmp[sample_final_index].strip('\n')
                        comment_line = "##pedia_extract_sample_and_index={},{}\n".format(sample_name, sample_index)
                        tmp_file.write(comment_line)
                        line = '\t'.join(tmp[0:9]) + '\t' + tmp[sample_final_index].strip('\n') + '\n'
                        tmp_file.write(line)
                        line = f.readline()
                    else:
                        tmp_file.write(line)
                        line = f.readline()
    cmd = 'cat {} | bcftools view -i \'GT!~\"\.\"\' - | bgzip -f >  {}.gz'.format(tmp_name, tmp_name)
    os.system(cmd)
    cmd = 'rm -f {}'.format(tmp_name)
    os.system(cmd)

if __name__ == '__main__':
    main()
