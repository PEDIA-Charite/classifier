# classifier
## Usage:
```
python oop_pedia_classifier.py train_path train_label -t test_path -o output_path
```

The following parameters are required to run pedia:

* train_path is the folder which contains training data. It could be 1KG, ExAC, IRAN.
For example, the path is /data/8/projects/PEDIA/3_simulation/json_simulation/real/train/1KG.

* train_label is for annotating which training set we used.

* -o output_path is the output folder. The default is current folder.

For the following parameters, you should assign exact one parameter to specify which mode you want to run.

* -t test_path. The path is the folder which contains testing data.

* -c fold number. This parameter enables k-fold cross validation (default 10).

* -l Flag enables leave one group out cross validation. The grouping is based on the mutation gene.

The optional parameters are:

* -e feature. Exclude specific features. 0: Feature match, 1: CADD, 2: Gestalt, 3: BOQA, 4: PHENO. If features are more than one, use _ to separate them.

## Example:
Therefore, if you run on solexa server, the command for testing on another data set is
```
python oop_pedia_classifier.py /data/8/projects/PEDIA/3_simulation/json_simulation/real/train/1KG/ 1KG -t /data/8/projects/PEDIA/3_simulation/json_simulation/real/test -o output/1KG
```
The command for 10-fold cross validation is
```
python oop_pedia_classifier.py /data/8/projects/PEDIA/3_simulation/json_simulation/real/train/1KG/ 1KG -o output/cv/1KG -c 10
```
The command for loocv is
```
python oop_pedia_classifier.py /data/8/projects/PEDIA/3_simulation/json_simulation/real/train/1KG/ 1KG -o output/loocv/1KG -l
```
The command for 10-fold cv and excluding gestalt and feature match score is
```
python oop_pedia_classifier.py /data/8/projects/PEDIA/3_simulation/json_simulation/real/train/1KG/ 1KG -o output/exclude/1KG -c 10 -e 0_2
```

