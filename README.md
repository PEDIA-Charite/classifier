# classifier

## Contents
* [General information](#general-information)
* [Download dataset](#download-dataset)
* [Evaluation](#evaluation)
 * [PEDIA cohort](#pedia-cohort)
 * [Deep-Gestalt publication test set](#deep-gestalt-publication-test-set) 
* [Usage](#usage)
* [Snakemake](#snakemake)
* [Results](#results)
* [JSON format](#json-format)

## General information
Classifier is a submodule in [PEDIA-workflow](https://github.com/PEDIA-Charite/PEDIA-workflow).
To run classifier, it requires the JSON file which is the output from PEDIA-workflow in this
[JSON format](#json-format). The gestalt score of facial analysis from Deep-Gestalt paper
([Gurovich et al.](https://www.nature.com/articles/s41591-018-0279-0)) is provided by FDNA.
It requires the **Key and Secret** to fetch the gestalt score and patient data from
face2gene platform. Therefore, you are not able to run the PEDIA-workflow without the Key and Secret.
However, we provide the PEDIA datasets which is described in PEDIA paper. You could run the classifier
by downloading the datasets from [pedia-study.org](https://pedia-study.org/pedia_services/download).
If you are interested in using PEDIA to analyze your patient, please contact
Prof. Peter Krawitz (pkrawitz@uni-bonn.de) for the authentication you need.

## Download dataset
Please download the PEDIA datasets we used in PEDIA paper in the following link
[https://pedia-study.org/pedia_services/download](https://pedia-study.org/pedia_services/download).
The download link requires registration to pedia-study.org.
The PEDIA datasets contain the following two data sets.
 * PEDIA cohort
 * Deep-Gestalt publication test set


## Evaluation
Once you download the PEDIA datasets, you could reproduce the results described in PEDIA paper by
the following steps.
### PEDIA cohort
In pedia_jsons_v1.2/jsons/1KG/CV folder, there are 679 json files simulated by 1KGP dataset.
For each case, you will find 'geneList' in case_id.json which contains the scores from five
different scoring methods for each gene.
The dataset could be used for cross-validation evaluation which is performed in PEDIA paper.
In addition to the cross-validation, it could be also used for training the model and
further testing on the new patient.

```
  # 679 cases in PEDIA cohort
  pedia_jsons_v1.2/jsons/1KG/CV/*.json

  # Performed 10 fold cross-validation
  python pedia.py pedia_jsons_v1.2/jsons/1KG/CV/ 1KG -c 10 -o output_dir --cv-cores 5 -p 5
```

### Deep-Gestalt publication test set
In Deep-Gestalt paper ([Gurovich et al.](https://www.nature.com/articles/s41591-018-0279-0)),
they provided 329 cases with frontal images for evaluation.
We selected 260 out of 329 cases which is suitable for exome sequencing analysis.
The cases with the disorders that are confirmed by other tests than exome
sequencing such as Down syndrome were removed in this analysis.

In order to compare the performance between Deep-Gestalt and PEDIA, we randomly selected the
cases in PEDIA cohort with the same diagnosis as the one in Deep-Gestalt publication test set,
and further assigned the features and disease-causing mutations to the case in Deep-Gestalt test set.
Then we took the PEDIA cohort as the training set.
To avoid over-fitting, we removed the cases with the same disease-causing mutations in PEDIA
cohort because the same mutation leads to the same CADD score.
The number of cases in training set ranges from 381 to 404 due to random selection.

In publication_simulation folder, there are 10 folder with REP prefix and number as
suffix which contains the deep gestalt publication data set simulated by the PEDIA cohort.
We simulated the cases randomly, so we ran the experiments for ten times.
The suffix indicates the number of run. In this experiment, we train on the PEDIA cohort,
then test the model with the simulated Deep-Gestalt cases.

```
  # training and testing set
  publication_simulation_v1.2/REP_0/jsons/1KG/train/
  publication_simulation_v1.2/REP_0/jsons/1KG/test/

  # Train on training set and test on deepgestalt publication test set
  python pedia.py publication_simulation_v1.2/REP_0/jsons/1KG/train/ 1KG -t publication_simulation_v1.2/REP_0/jsons/1KG/test/ -o output_dir -p 5
```

## Requirement

1. Create an environment with the required software
```
conda env create --name classifier --file environment.yaml
```

2. Activate the environment
```
source activate classifier
```

## Usage
```
python pedia.py train_path train_label -t test_path -o output_path
```

The following parameters are required to run pedia:

* train_path is the folder which contains training data. It could be 1KG, ExAC, IRAN.
For example, you could use either pedia_jsons_v1.2/jsons/1KG/CV/ or publication_simulation_v1.2/REP_0/jsons/1KG/train/

* train_label is for annotating which training set we used (1KG, ExAC or IRAN).

* -o output_path is the output folder. The default is current folder.

For the following parameters, you should assign exact one parameter to specify which mode you want to run.

* -t test_path. The path could be either the folder which contains testing data or the JSON file.
For example, you could use publication_simulation_v1.2/REP_0/jsons/1KG/test/.

* -c fold number. This parameter enables k-fold cross validation (default 10).


The optional parameters are:

* -p how many fold use in parameter tuning. If it is not set, we use the defult parameter C.

* --cv-cores Cores using in cross validation, default 5. You could run parameter tunning in parallel with this parameter.

* -e feature. Exclude specific features. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use _ to separate them.


### Example
Execute the following command. The output will be in output_dir directory.
If you want to prioritize one case, then typing the file name in testing argument.
```
python pedia.py jsons/1KG/CV/ 1KG -t your_filename.json -o output_dir/1KG
```

If you don't have the authentication from Face2Gene platform, you could use the 
test sample in PEDIA-workflow/tests/data/. The PEDIA-workflow will trigger the classifier
after the preprocessing.

```
cd ../
python3 preprocess.py -s tests/data/cases/123.json -v tests/data/vcfs/123.vcf.gz

# if you want to run the whole pipeline, you need the files in ../data folder.
# Please check PEDIA-workflow repository for further information
```

The command for 10-fold cross validation is
```
python pedia.py pedia_jsons_v1.2/jsons/1KG/CV/ 1KG -c 10 -o output_dir --cv-cores 5 -p 5
```

The command for 10-fold cv and excluding gestalt and feature match score is
```
python pedia.py pedia_jsons_v1.2/jsons/1KG/CV/ 1KG -c 10 -o output_dir --cv-cores 5 -p 5 -e 0_2
```


## Snakemake

You can use snakemake to run different kind of experiments automatically.

1. Install [snakemake](https://snakemake.readthedocs.io/en/stable/getting_started/installation.html). 

2. Create an environment with the required software
```
conda env create --name classifier --file environment.yaml
```

3. Activate the environment
```
source activate classifier
```

**Note: to use Snakemake, please put the the following files in the corresponding path.**
* pedia_jsons_v1.2/jsons/1KG/CV -> PEDIA-workflow/3_simulation/jsons/1KG/CV


### Usage

* Run 10-fold cross validation on 1KG data set.
```
snakemake -p CV_all
```

* Using all feature combination to run 10-fold cross validation on 1KG data set.
```
snakemake -p CV_exclude_all --cores 3
```

## Results
You will find the results in the output dir you specified in the command.

```
ls output_dir/cv_0/
# *.csv contain all five scores and pedia score for each gene in csv format
# *.json contain the PEDIA score in JSON format
# count_*.csv list the number of cases in each rank
# rank_*.csv list the rank of each case
```

**45254.csv**

Here, we listed the top ten genes in 45254.csv. You will find the five scores and PEDIA score.
The label indicates whether this gene is disease-causing gene or not.
In this case, ARID1B has the highest PEDIA score and it is the disease-causing gene of this case.

```
gene_name gene_id pedia_score feature_score cadd_score gestalt_score boqa_score pheno_score label
ARID1B    57492   4.509       0.836         25.0       0.721         0.0        0.9982      1
ARID1A    8289    1.238       0.836         0.001      0.721         0.0        0.9982      0
SMARCB1   6598    1.238       0.836         0.001      0.721         0.0        0.9982      0
SOX11     6664    1.238       0.836         0.001      0.721         0.0        0.9982      0
SMARCE1   6605    1.238       0.836         0.001      0.721         0.0        0.9982      0
SMARCA4   6597    1.238       0.836         0.001      0.721         0.0        0.9982      0
FIG4      9896    0.942       0.738         38.0       0.0           0.0        0.0         0
CYP26C1   340665  0.074       0.0           24.0       0.273         0.0        0.0         0
RFT1      91869   0.0207      0.0           35.0       0.0           0.0        0.0         0
VEGFC     7424    -0.110      0.0           34.0       0.0           0.0        0.0         0
```

## JSON format
Please find the structure of the JSON format of each case in the dataset below.
We only listed part of the data here, for the complete information, please
check the original JSON file.

```
  {
      "case_id": 45254,
      "features": [
          "HP:0000316",
          "HP:0010541",
          "HP:0000729"
      ],
      "geneList": [
          {
              "gene_symbol": "ARID1B",
              "cadd_phred_score": 25,
              "syndrome_name": "Coffin-Siris Syndrome",
              "gestalt_score": 0.7211414282399627,
              "gene_omim_id": "614556",
              "has_mask": true,
              "feature_score": 0.8369029469,
              "pheno_score": 0.9977,
              "boqa_score": 0,
              "gene_id": "57492"
          },
          {
              "cadd_phred_score": 8.507,
              "syndrome_name": "Laron Syndrome",
              "gestalt_score": 0.026714321059580264,
              "gene_omim_id": "600946",
              "has_mask": true,
              "feature_score": 0,
              "pheno_score": 0,
              "boqa_score": 0,
              "gene_id": "2690"
          }
      ],
      "genomicData": [
          {
              "Mutations": {
                  "result": "VARIANTS_DETECTED",
                  "Build": "GRCh37",
                  "HGVS-code": "NM_020732.3:c.5737C>T",
                  "additional info": "",
                  "Inheritance Mode": ""
              },
              "Test Information": {
                  "Gene Name": "ARID1B",
                  "Gene ID": 57492,
                  "Genotype": "HETEROZYGOUS",
                  "Notation": "CDNA_LEVEL",
                  "Mutation Type": "TARGETED_TESTING",
                  "Molecular Test": "TARGETED_TESTING"
              }
          }
      ],
      "selected_syndromes": [
          {
              "has_mask": 0,
              "omim_id": 135900,
              "diagnosis": "MOLECULARLY_DIAGNOSED",
              "syndrome_name": "Coffin-Siris Syndrome1; CSS1"
          },
          {
              "has_mask": 1,
              "omim_id": [
                  614608,
                  614609,
                  616938,
                  135900,
                  614607
              ],
              "diagnosis": "MOLECULARLY_DIAGNOSED",
              "syndrome_name": "Coffin-Siris Syndrome"
          }
      ]
  }
```
