from os.path import join
import logging
import optDNTRA_utils as utils
from time import time


### Configuration Setup ### ----------------------------------------
TRANSCRIPTPREFLT = config["transcript"]


BUSCO_CMD = utils.tool_command(config, "busco_env", "busco")

### Logging Setup ### ----------------------------------------
LOG_BUSCOASMT = utils.get_logger("BUSCOASMT", VERBOSE)


### Rule ### ----------------------------------------
checkpoint busco_assessment:
    """
    Perform BUSCO assessment to evaluate transcriptome completeness
    """
    input:
        transcriptPreFlt=TRANSCRIPTPREFLT,
        transcriptPostFlt=join(TRANSEVID_DIR, "transcript.flt.final.fa"),
    output:
        buscoPreFlt=directory(
            join(BUSCO_DIR, BUSCO_LINEAGE, "busco_" + BUSCO_LINEAGE + "_preFlt")
        ),
        buscoPostFlt=directory(
            join(BUSCO_DIR, BUSCO_LINEAGE, "busco_" + BUSCO_LINEAGE + "_postFlt")
        ),
    log:
        join(ASMT_LOG_DIR, "buscoAsmt-busco_assessment.log"),
    params:
        lineage=BUSCO_LINEAGE,
        buscoPreFlt="busco_" + BUSCO_LINEAGE + "_preFlt",
        buscoPostFlt="busco_" + BUSCO_LINEAGE + "_postFlt",
        downloadPath=directory(join(BUSCO_DIR, BUSCO_LINEAGE))
    threads: THREADS
    run:
        LOG_BUSCOASMT.info("Running buscoAsmt.smk...")
        startTime = time()

        shell(
        """
        {BUSCO_CMD} \
         --in {input.transcriptPreFlt} \
         --out {params.buscoPreFlt} \
         --mode transcriptome \
         --lineage_dataset {params.lineage} \
         --cpu {threads} \
         --download_path {params.downloadPath} \
         --force \
         --out_path {params.downloadPath} \
         --quiet \
         &> {log}

        {BUSCO_CMD} \
         --in {input.transcriptPostFlt} \
         --out {params.buscoPostFlt} \
         --mode transcriptome \
         --lineage_dataset {params.lineage} \
         --cpu {threads} \
         --download_path {params.downloadPath} \
         --force \
         --out_path {params.downloadPath} \
         --quiet \
         &>> {log}
        """
        )

        endTime = time()
        elapseTime = endTime - startTime
        LOG_BUSCOASMT.info(
            f"Performed BUSCO assessment for transcriptome completeness in {elapseTime:.2f} seconds."
        )


def get_busco_summary(wildcards):
    buscoPreFlt = checkpoints.busco_assessment.get(**wildcards).output.buscoPreFlt
    buscoPostFlt = checkpoints.busco_assessment.get(**wildcards).output.buscoPostFlt
    checkpointOut = [
        join(
            buscoPreFlt,
            f"short_summary.specific.{BUSCO_LINEAGE}.busco_{BUSCO_LINEAGE}_preFlt.json",
        ),
        join(
            buscoPostFlt,
            f"short_summary.specific.{BUSCO_LINEAGE}.busco_{BUSCO_LINEAGE}_postFlt.json",
        ),
    ]
    return checkpointOut


rule generate_plot:
    """
    Generate BUSCO assessment plot
    """
    input:
        buscoSummary=get_busco_summary,
    output:
        buscoFig=join(BUSCO_DIR, BUSCO_LINEAGE, "busco_figure.png"),
    log:
        join(ASMT_LOG_DIR, "buscoAsmt-generate_plot.log"),
    params:
        buscoDir=directory(join(BUSCO_DIR, BUSCO_LINEAGE)),
        plotScript=BUSCO_CMD,
    threads: THREADS
    run:
        shell(
        """
        cp {input.buscoSummary[0]} {params.buscoDir} &> {log}
        cp {input.buscoSummary[1]} {params.buscoDir} &>> {log}
        {params.plotScript} \
         --plot {params.buscoDir} \
         --quiet \
         &>> {log}
        test -s {output.buscoFig}
        """
        )
