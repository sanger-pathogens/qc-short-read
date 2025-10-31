include { MULTIQC         } from './assorted-sub-workflows/reporting/modules/multiqc.nf'

//
// SUBWORKFLOWS

include { MIXED_INPUT     } from './assorted-sub-workflows/mixed_input/mixed_input.nf'
include { PREPROCESSING  } from './assorted-sub-workflows/qc/preprocessing.nf'
include { QC              } from './assorted-sub-workflows/qc/qc.nf'


def logo = NextflowTool.logo(workflow, params.monochrome_logs)

log.info logo

NextflowTool.commandLineParams(workflow.commandLine, log, params.monochrome_logs)


def printHelp() {
    NextflowTool.help_message("${workflow.ProjectDir}/schema.json", 
                               ["${workflow.ProjectDir}/assorted-sub-workflows/irods_extractor/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/mixed_input/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/kraken2bracken/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/taxo_profile/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/qc/schema.json"],

    params.monochrome_logs, log)
}


workflow {
    if (params.help) {
        printHelp()
        exit 0
    }
    
    MIXED_INPUT()

    if (!params.skip_preprocessing) {
        PREPROCESSING(MIXED_INPUT.out)
        | set { reads_ch }
    }
    else {
        reads_ch = MIXED_INPUT.out
    }

    reads_ch
    | QC
    | MULTIQC

    if (!params.skip_cleanup) {
        QC.out.multiqc_input.join(MULTIQC.out.data, remainder=true)
           .flatten()
           .filter(Path)
           .map { it.delete() }
    }
    QC.out.multiqc_input.view()
    MULTIQC.out.data.view()
}


workflow.onComplete {
    NextflowTool.summary(workflow, params, log)

    log.info """
    To rerun from ${workflow.launchDir}:
    bsub -q oversubscribed -R "select[mem>4000] rusage[mem=4000]" -M4000 -o ${workflow.runName}_repeat.o -e ${workflow.runName}_repeat.e -J ${workflow.runName}_repeat ${workflow.commandLine}
    """
}