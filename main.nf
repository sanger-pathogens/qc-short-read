include { FASTQC } from './modules/fastqc.nf'
include { MULTIQC } from './assorted-sub-workflows/reporting/modules/multiqc.nf'

//
// SUBWORKFLOWS
//
include { MIXED_INPUT     } from './assorted-sub-workflows/mixed_input/mixed_input.nf'
include { KRAKEN2BRACKEN  } from './assorted-sub-workflows/kraken2bracken/subworkflows/kraken2bracken.nf'

def logo = NextflowTool.logo(workflow, params.monochrome_logs)

log.info logo

NextflowTool.commandLineParams(workflow.commandLine, log, params.monochrome_logs)


def printHelp() {
    NextflowTool.help_message("${workflow.ProjectDir}/schema.json", 
                               ["${workflow.ProjectDir}/assorted-sub-workflows/mixed_input/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/irods_extractor/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/kraken2bracken/schema.json"],
    params.monochrome_logs, log)
}


workflow {
    if (params.help) {
        printHelp()
        exit 0
    }

    MIXED_INPUT
    | (FASTQC & KRAKEN2BRACKEN)

    FASTQC.out.zip.collect{it[1,2]}
    | mix(KRAKEN2BRACKEN.out.kraken2_report_for_multiqc.collect{it[1]})
    | collect
    | set { multiqc_input }

    MULTIQC(multiqc_input)

    if (!params.skip_cleanup) {
        FASTQC.out.zip.join(MULTIQC.out.data, remainder=true)
           .flatten()
           .filter(Path)
           .map { it.delete() }
    }
}

workflow.onComplete {
    NextflowTool.summary(workflow, params, log)

    log.info """
    To rerun from ${workflow.launchDir}:
    bsub -q oversubscribed -R "select[mem>4000] rusage[mem=4000]" -M4000 -o ${workflow.runName}_repeat.o -e ${workflow.runName}_repeat.e -J ${workflow.runName}_repeat ${workflow.commandLine}
    """
}