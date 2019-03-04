# classifier
## Usage:
```
python pedia.py train_path train_label -t test_path -o output_path
```

The following parameters are required to run pedia:

* train_path is the folder which contains training data. It could be 1KG, ExAC, IRAN.
For example, the path is PEDIA/3_simulation/jsons/real/train/1KG.

* train_label is for annotating which training set we used (1KG, ExAC or IRAN).

* -o output_path is the output folder. The default is current folder.

For the following parameters, you should assign exact one parameter to specify which mode you want to run.

* -t test_path. The path could be either the folder which contains testing data or the JSON file.

* -c fold number. This parameter enables k-fold cross validation (default 10).

* -p how many fold use in parameter tuning. If it is not set, we use the defult parameter C.

* --cv-cores Cores using in cross validation, default 5

* -l Flag enables leave one group out cross validation. The grouping is based on the mutation gene.

The optional parameters are:

* -e feature. Exclude specific features. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use _ to separate them.

* -f feature. Filter cases which don't have specific features in pathogenic mutation gene. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. We only support using one feature.

## Download training data
* You could download the training data we used in PEDIA paper in the following link (https://pedia-study.org/pedia_services/download)
* jsons/1KG/CV_gestalt/* .json could be use for training the model

## Example:
Execute the following command. The output will be in output/ directory.
If you want to prioritize one case, then typing the file name in testing argument.
```
python pedia.py jsons/1KG/CV/ 1KG -t your_filename.json -o output/1KG
```

The command for 10-fold cross validation is
```
python pedia.py /projects/PEDIA/3_simulation/jsons/1KG/CV/ 1KG -o output/cv/1KG -c 10
```
The command for loocv is
```
python pedia.py /projects/PEDIA/3_simulation/jsons/1KG/CV/ 1KG -o output/loocv/1KG -l
```
The command for 10-fold cv and excluding gestalt and feature match score is
```
python pedia.py /projects/PEDIA/3_simulation/jsons/1KG/CV/ 1KG -o output/exclude/1KG -c 10 -e 0_2
```

## Snakemake

You can use snakemake to run different kind of experiments automatically.

### Requirement

1. Install [snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). 

2. Create an environment with the required software
```
conda env create --name classifier --file environment.yaml
```

3. Activate the environment
```
source activate classifier
```

### Usage
* To obtain all the output files for a case which we want to upload to DPDL. We will get all the output files in folder output/test/1KG/case_id/.
```
snakemake -p output/test/1KG/case_id/case_id.out
```
case_id_pedia.json is the file which append PEDIA scores to genelist.
case_id.vcf.gz is the file which includes the variants in the top 10 genes.


* Run 10-fold cross validation on 1KG, ExAC and Iran data sets respectively.
```
snakemake -p CV_all --cores 3
```

* Run loocv on 1KG, ExAC and Iran data sets respectively.
```
snakemake -p LOOCV_all --cores 3
```

* Using all feature combination to run 10-fold cross validation on 1KG, ExAC and Iran data sets respectively.
```
snakemake -p CV_exclude_all --cores 3
```
