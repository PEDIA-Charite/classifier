import csv
import getopt
import sys
import os 
import gzip

opts, args = getopt.getopt(sys.argv[1:], "h::", ["input=", "output=", "pedia="])
for opt, arg in opts:
    if opt in ("--input"):
        filename = arg
    elif opt in ("--output"):
        newfile = arg
    elif opt in ("--pedia"):
        pedia_path = arg

gene_list = []
with open(pedia_path) as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        if count < 10:
            gene_list.append(row['gene_name'])
        count = count + 1
prefix = filename.split('/')[-1].split('.')[0]
genes = '|'.join(gene_list)
cmd = "bgzip -d -c " + filename + " | grep --line-buffered -E '" + genes + "' > " + newfile[0:-3]
os.system(cmd)
print(cmd)

with gzip.open(filename, 'r') as f:
    line = f.readline()
    flag = 1 
    print(line)
    with open('tmp.vcf', 'w') as tmp_file:
        while line and flag:
            line = line.decode('utf-8')
            if "#CHROM" in line:
                flag = 0
                tmp = line.split('\t')
                tmp[-1] = prefix
                line = '\t'.join(tmp) + '\n'
                tmp_file.write(line)
            else:
                tmp_file.write(line)
                line = f.readline()
cmd = 'cat tmp.vcf ' + newfile[0:-3] + ' > tmp && mv tmp ' + newfile[0:-3]
os.system(cmd)
cmd = 'bgzip ' + newfile[0:-3]
os.system(cmd)

