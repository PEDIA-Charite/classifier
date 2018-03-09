workdir: "scripts"

subworkflow sim_workflow:
	workdir: "../3_simulation"
	snakefile: "../3_simulation/Snakefile"

DATA_TYPE = ["1KG", "ExAC", "IRAN"]
FEATURE = ["0", "1", "2", "3", "4", "0_1", "0_2", "0_3", "0_4", "1_2", "1_3", "1_4",
           "2_3", "2_4", "3_4", "0_1_2", "0_1_3", "0_1_4", "0_2_3", "0_2_4", "0_3_4", "1_2_3", "1_2_4", "1_3_4", "2_3_4",
           "0_1_2_3", "0_2_3_4", "0_1_3_4", "0_1_2_4", "1_2_3_4"]


data = expand("CV_{data}/run.log", data=DATA_TYPE),


classify_file = 'pedia.py'
mapping_file = 'mapping.py'
mapping_vcf_file = 'get_variant.py'

rule all:
    input:
        expand("../output/cv/CV_{data}/run.log", data=DATA_TYPE),
        expand("../output/loocv/LOOCV_{data}/run.log", data=DATA_TYPE),
        expand("../output/exclude/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)

rule test:
    input:
        train = "/home/la60312/pedia/3_simulation/json_simulation/real/train/{data}/",
        json = sim_workflow("json_simulation/real/test/{sample}.json")
    output:
        csv = "../output/test/{data}/{sample}/{sample}.csv"
    params:
        label = "{data}",
        dir = "../output/test/{data}/{sample}"
    shell:
        """
        python {classify_file} '{input.train}' '{params.label}' -t {input.json} -g -o '{params.dir}';
        """

rule map_pedia:
    input:
        csv = "../output/test/{data}/{sample}/{sample}.csv",
        json = sim_workflow("json_simulation/real/test/{sample}.json")
    output:
        json = "../output/test/{data}/{sample}/{sample}_pedia.json",
    params:
        label = "{data}",
        dir = "../output/test/{data}/{sample}/"
    shell:
        """
        python {mapping_file} --input '{input.json}' --pedia '{input.csv}' --output '{output.json}';
        """

rule map_vcf:
    input:
        csv = "../output/test/{data}/{sample}/{sample}.csv",
        vcf = sim_workflow("vcf_annotation/{sample}.annotation.vcf.gz")
    output:
        vcf = "../output/test/{data}/{sample}/{sample}.vcf.gz",
    params:
        label = "{data}",
        dir = "../output/test/{data}/{sample}/"
    shell:
        """
        python {mapping_vcf_file} --input '{input.vcf}' --pedia '{input.csv}' --output '{output.vcf}';
        """

rule map:
    input:
        vcf = "../output/test/{data}/{sample}/{sample}.vcf.gz",
        json = "../output/test/{data}/{sample}/{sample}_pedia.json",
    output:
        out = touch("../output/test/{data}/{sample}/{sample}.out")
    params:
        label = "{data}",
        dir = "../output/test/{data}/{sample}/"

rule CV:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV/{data}.csv")
    output:
        "../output/cv/CV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/cv/CV_{data}",
        train = "../../3_simulation/json_simulation/{data}/CV/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -c 10 -g -o '{params.dir}';
        """

rule CV_all:
    input:
        expand("../output/cv/CV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/cv/CV_all.log")

rule CV_exclude:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV/{data}.csv")
    output:
        "../output/exclude/CV_{data}_e_{exclude}/run.log"
    params:
        label = "{data}",
        dir = "../output/exclude/CV_{data}_e_{exclude}",
        exclude_feature = "{exclude}",
        train = "../../3_simulation/json_simulation/{data}/CV/"
    shell:
        """
        python {classify_file} {params.train} {params.label} -c 10 -g -e {params.exclude_feature} -o {params.dir};
        """

rule CV_exclude_all:
    input:
        expand("../output/exclude/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)
    output:
        touch("../output/exclude/CV_exclude_all.log")

rule LOOCV:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV/{data}.csv")
    output:
        "../output/loocv/LOOCV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/loocv/LOOCV_{data}",
        train = "../../3_simulation/json_simulation/{data}/CV/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -l -g -o '{params.dir}';
        """

rule LOOCV_all:
    input:
        expand("../output/loocv/LOOCV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/loocv/LOOCV_all.log")

rule CV_g:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV/{data}.csv")
    output:
        "../output/cv_g/CV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/cv_g/CV_{data}",
        train = "../../3_simulation/json_simulation/{data}/CV/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -c 10 -g -f 2 -o '{params.dir}';
        """

rule CV_all_g:
    input:
        expand("../output/cv_g/CV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/cv_g/CV_all.log")

rule LOOCV_g:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV/{data}.csv")
    output:
        "../output/loocv_g/LOOCV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/loocv_g/LOOCV_{data}",
        train = "../../3_simulation/json_simulation/{data}/CV/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -l -g -f 2 -o '{params.dir}';
        """

rule LOOCV_all_g:
    input:
        expand("../output/loocv_g/LOOCV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/loocv_g/LOOCV_all.log")

rule CV_exclude_g:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV/{data}.csv")
    output:
        "../output/exclude_g/CV_{data}_e_{exclude}/run.log"
    params:
        label = "{data}",
        dir = "../output/exclude_g/CV_{data}_e_{exclude}",
        exclude_feature = "{exclude}",
        train = "../../3_simulation/json_simulation/{data}/CV/"
    shell:
        """
        python {classify_file} {params.train} {params.label} -c 10 -f 2 -g -e {params.exclude_feature} -o {params.dir};
        """

rule CV_exclude_all_g:
    input:
        expand("../output/exclude_g/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)
    output:
        touch("../output/exclude_g/CV_exclude_all.log")

rule Report:
    shell:
        """
        cd latex;
        pdflatex report.tex;
        cd ..
        """
