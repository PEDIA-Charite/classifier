workdir: "scripts"
configfile: "../config.yml"

subworkflow sim_workflow:
	workdir: "../3_simulation"
	snakefile: "../3_simulation/Snakefile"

subworkflow pub_sim_workflow:
	workdir: "../3_simulation/publication_simulation"
	snakefile: "../3_simulation/publication_simulation/Snakefile"

DATA_TYPE = ["1KG", "ExAC", "IRAN"]
FEATURE = ["0", "1", "2", "3", "4", "0_3", "0_4", "1_2", 
           "3_4", "0_3_4", "0_2_3_4", "0_1_3_4"]
#FEATURE = ["0", "1", "2", "3", "4", "0_1", "0_2", "0_3", "0_4", "1_2", "1_3", "1_4",
#           "2_3", "2_4", "3_4", "0_1_2", "0_1_3", "0_1_4", "0_2_3", "0_2_4", "0_3_4", "1_2_3", "1_2_4", "1_3_4", "2_3_4",
#           "0_1_2_3", "0_2_3_4", "0_1_3_4", "0_1_2_4", "1_2_3_4"]

RUN = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

data = expand("CV_{data}/run.log", data=DATA_TYPE)

SAMPLES = config["TEST_SAMPLES"]

classify_file = 'pedia.py'
mapping_file = 'mapping.py'
mapping_vcf_file = 'get_variant.py'

rule all:
    input:
        expand("../output/cv/CV_{data}/run.log", data=DATA_TYPE),
        expand("../output/loocv/LOOCV_{data}/run.log", data=DATA_TYPE),
        expand("../output/exclude/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)

#################################################################
# Test the publication data set in Deep Gestalt paper 
#################################################################

rule publication_simulation_test:
    input:
        train = pub_sim_workflow("{background}_{run}_train.log"),
        test = pub_sim_workflow("{background}_{run}_test.log")
    output:
        csv = "../output/publication_simulation_test/{background}/REP_{run}/run.log"
    params:
        label = "{background}",
        dir = "../output/publication_simulation_test/{background}/REP_{run}",
        train = "../../3_simulation/publication_simulation/REP_{run}/json_simulation/{background}/train/",
        test = "../../3_simulation/publication_simulation/REP_{run}/json_simulation/{background}/CV/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -t {params.test} -g -o '{params.dir}' -p 5;
        """

rule publication_simulation_test_all:
    input:
        expand("../output/publication_simulation_test/{data}/REP_{rep}/run.log", data=DATA_TYPE, rep=RUN)
    output:
        touch("../output/publication_simulation_test/all.log")

##########################################################################
# Test the cases with real exome but we used the simulated exome instead of
# real exome. We would like to compare the performace between using real 
# exome and simulated one
##########################################################################

rule test_simulated:
    input:
        train = sim_workflow("performanceEvaluation/data/Real/train_{data}.csv"),
        test = sim_workflow("performanceEvaluation/data/Real/test_simulated_{data}.csv")
    output:
        csv = "../output/real_simulated_test/{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/real_simulated_test/{data}/",
        train = "../../3_simulation/json_simulation/real/train/{data}/",
        test = "../../3_simulation/json_simulation/real/test_{data}/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -t {params.test} -g -o '{params.dir}' -p 5;
        """

rule test_simulated_all:
    input:
        expand("../output/real_simulated_test/{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/real_simulated_test/all.log")

#########################################################################
# Train the model with simulated cases and test the cases with real exome
#########################################################################

rule test:
    input:
        train = sim_workflow("performanceEvaluation/data/Real/train_{data}.csv"),
        test = sim_workflow("performanceEvaluation/data/Real/test_real.csv")
    output:
        csv = "../output/real_test/{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/real_test/{data}/",
        train = "../../3_simulation/json_simulation/real/train/{data}/",
        test = "../../3_simulation/json_simulation/real/test/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -t {params.test} -g -o '{params.dir}' -p 5;
        """

rule test_all:
    input:
        expand("../output/real_test/{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/real_test/all.log")

############################################################################
# Test the case with unknown diagnosis
############################################################################

rule test_unknown:
    input:
        train = sim_workflow("performanceEvaluation/data/CV/{data}.csv"),
        json = sim_workflow("json_simulation/real/unknown_test/{sample}.json")
    output:
        csv = "../output/test/{data}/{sample}/{sample}.csv"
    params:
        label = "{data}",
        dir = "../output/test/{data}/{sample}",
        train = "../../3_simulation/json_simulation/{data}/CV"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -t {input.json} -g -o '{params.dir}';
        """

rule map_pedia:
    input:
        csv = "../output/test/{data}/{sample}/{sample}.csv",
        json = sim_workflow("json_simulation/real/unknown_test/{sample}.json")
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
        #vcf = "../../3_simulation/vcf_annotation/{sample}.annotation.vcf.gz"
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
        out = touch("../output/test/{data}/{sample}/run.out")
    params:
        label = "{data}",
        dir = "../output/test/{data}/{sample}/"

rule map_all:
    input:
        expand("../output/test/{data}/{sample}/run.out", data='1KG', sample=SAMPLES)
    output:
        touch("../output/test/all")


############################################################################
# Run k-fold cross-validation. Default k: 10
############################################################################

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
        python {classify_file} '{params.train}' '{params.label}' -c 10 -g -o '{params.dir}' -p 5 --cv-rep 10;
        """

rule CV_all:
    input:
        expand("../output/cv/CV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/cv/CV_all.log")

############################################################################
# Run 10 fold cross validation with different scores
# We define the scores in FEATURE
# We would like to compare the performace of using 
# different scores.
###########################################################################

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
        python {classify_file} {params.train} {params.label} -c 10 -e {params.exclude_feature} -o {params.dir} --cv-cores 5;
        """

rule CV_exclude_all:
    input:
        expand("../output/exclude/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)
    output:
        touch("../output/exclude/CV_exclude_all.log")

###########################################################################
# Perform LOOCV on disease causing gene
###########################################################################

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
        python {classify_file} '{params.train}' '{params.label}' -l -g -o '{params.dir}' -p 5 --cv-rep 5 --cv-cores 5;
        """

rule LOOCV_all:
    input:
        expand("../output/loocv/LOOCV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/loocv/LOOCV_all.log")

###########################################################################
# Perform 10 fold CV on cases with gestalt support
###########################################################################

rule CV_g:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV_gestalt/{data}.csv")
    output:
        "../output/cv_g/CV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/cv_g/CV_{data}",
        train = "../../3_simulation/json_simulation/{data}/CV_gestalt/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -c 10 -g  -o '{params.dir}' --cv-rep 10 --cv-cores 5 -p 5;
        """

rule CV_all_g:
    input:
        expand("../output/cv_g/CV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/cv_g/CV_all.log")

###########################################################################
# Perform 10 fold LOOCV on cases with gestalt support
###########################################################################

rule LOOCV_g:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV_gestalt/{data}.csv")
    output:
        "../output/loocv_g/LOOCV_{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/loocv_g/LOOCV_{data}",
        train = "../../3_simulation/json_simulation/{data}/CV_gestalt/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -l -g -o '{params.dir}' --cv-cores 5 -p 5 ;
        """

rule LOOCV_all_g:
    input:
        expand("../output/loocv_g/LOOCV_{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/loocv_g/LOOCV_all.log")

###########################################################################
# Perform 10 fold CV on cases with gestalt support by using different
# scores
###########################################################################

rule CV_exclude_g:
    input:
        sum_file = sim_workflow("performanceEvaluation/data/CV_gestalt/{data}.csv")
    output:
        "../output/exclude_g/CV_{data}_e_{exclude}/run.log"
    params:
        label = "{data}",
        dir = "../output/exclude_g/CV_{data}_e_{exclude}",
        exclude_feature = "{exclude}",
        train = "../../3_simulation/json_simulation/{data}/CV_gestalt/"
    shell:
        """
        python {classify_file} {params.train} {params.label} -c 10 -g -e {params.exclude_feature} -o {params.dir} --cv-cores 5;
        """

rule CV_exclude_all_g:
    input:
        expand("../output/exclude_g/CV_{data}_e_{exclude}/run.log", data=DATA_TYPE, exclude=FEATURE)
    output:
        touch("../output/exclude_g/CV_exclude_all.log")

##########################################################################
# Test the cases with real exome but we used the simulated exome instead of
# real exome. We would like to compare the performace between using real 
# exome and simulated one
##########################################################################

rule test_simulated_g:
    input:
        train = sim_workflow("performanceEvaluation/data/Real/gestalt/train_{data}.csv"),
        test = sim_workflow("performanceEvaluation/data/Real/gestalt/test_simulated_{data}.csv")
    output:
        csv = "../output/real_simulated_test_g/{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/real_simulated_test_g/{data}/",
        train = "../../3_simulation/json_simulation/real/gestalt/train/{data}/",
        test = "../../3_simulation/json_simulation/real/gestalt/test_{data}/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -t {params.test} -g -o '{params.dir}' -p 5;
        """

rule test_simulated_g_all:
    input:
        expand("../output/real_simulated_test_g/{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/real_simulated_test_g/all.log")

#########################################################################
# Train the model with simulated cases and test the cases with real exome
#########################################################################

rule test_g:
    input:
        train = sim_workflow("performanceEvaluation/data/Real/gestalt/train_{data}.csv"),
        test = sim_workflow("performanceEvaluation/data/Real/gestalt/test_real.csv")
    output:
        csv = "../output/real_test_g/{data}/run.log"
    params:
        label = "{data}",
        dir = "../output/real_test_g/{data}/",
        train = "../../3_simulation/json_simulation/real/gestalt/train/{data}/",
        test = "../../3_simulation/json_simulation/real/gestalt/test/"
    shell:
        """
        python {classify_file} '{params.train}' '{params.label}' -t {params.test} -g -o '{params.dir}' -p 5;
        """

rule test_g_all:
    input:
        expand("../output/real_test_g/{data}/run.log", data=DATA_TYPE)
    output:
        touch("../output/real_test_g/all.log")

rule Report:
    shell:
        """
        cd latex;
        pdflatex report.tex;
        cd ..
        """
