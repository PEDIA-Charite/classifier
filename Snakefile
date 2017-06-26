workdir: "scripts"

DATA_TYPE = ["1KG", "ExAC", "IRAN"]
FEATURE = ["0", "1", "2", "3", "4", "0_1", "0_2", "0_3", "0_4", "1_2", "1_3", "1_4",
           "2_3", "2_4", "3_4", "0_1_2", "0_1_3", "0_1_4", "0_2_3", "0_2_4", "0_3_4", "1_2_3", "1_2_4", "1_3_4", "2_3_4",
           "0_1_2_3", "0_2_3_4", "0_1_3_4", "0_1_2_4", "1_2_3_4"]


data = expand("CV_{data}/run.log", data=DATA_TYPE),


classify_file = 'oop_pedia_classifier.py'

rule all:
    input:
        expand("../output/cv/CV_{data}/run.log", data=DATA_TYPE),
        expand("../output/loocv/LOOCV_{data}/run.log", data=DATA_TYPE),
        expand("../output/exclude/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)

rule CV:
    input:
        train = "/data/8/projects/PEDIA/3_simulation/json_simulation/{data}/CV/"
    output:
        "../output/cv/CV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/cv/CV_{data}"
    shell:
        """
        python {classify_file} '{input.train}' '{params.label}' -c 10 -o '{params.dir}';
        """

rule CV_all:
    input:
        expand("../output/cv/CV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/cv/CV_all.log")

rule CV_exclude:
    input:
        train = "/data/8/projects/PEDIA/3_simulation/json_simulation/{data}/CV/"
    output:
        "../output/exclude/CV_{data}_e_{exclude}/run.log"
    params:
        label = "{data}",
        dir = "../output/exclude/CV_{data}_e_{exclude}",
        exclude_feature = "{exclude}"
    shell:
        """
        python {classify_file} {input.train} {params.label} -c 10 -e {params.exclude_feature} -o {params.dir};
        """

rule CV_exclude_all:
    input:
        expand("../output/exclude/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)
    output:
        touch("../output/exclude/CV_exclude_all.log")

rule LOOCV:
    input:
        train = "/data/8/projects/PEDIA/3_simulation/json_simulation/{data}/CV/"
    output:
        "../output/loocv/LOOCV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/loocv/LOOCV_{data}"
    shell:
        """
        python {classify_file} '{input.train}' '{params.label}' -l -o '{params.dir}';
        """

rule LOOCV_all:
    input:
        expand("../output/loocv/LOOCV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/loocv/LOOCV_all.log")

rule Report:
    shell:
        """
        cd latex;
        pdflatex report.tex;
        cd ..
        """
