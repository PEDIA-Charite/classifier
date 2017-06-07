# classifier
## Usage:
```python oop_pedia_classifier.py -o output_path train_path test_path train_label```

* train_path is the folder which contains training data. It could be 1KG, ExAC, IRAN.
For exampl, the path is /data/8/projects/PEDIA/3_simulation/json_simulation/real/train/1KG.

* test_path is the folder which contains training data.

* train_label is for annotating which training set we used.

* output_path is the output folder. The default is current folder.

Therefore, if you run on solexa server, the command is
```python oop_pedia_classifier.py /data/8/projects/PEDIA/3_simulation/json_simulation/real/train/1KG/ /data/8/projects/PEDIA/3_simulation/json_simulation/real/test 1KG 1KG```
