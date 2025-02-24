include { FASTQC } from './modules/fastqc.nf'
include { MULTIQC } from './modules/multiqc.nf'

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

    MULTIQC(
        FASTQC.out.zip.collect{it[1,2]},
        KRAKEN2BRACKEN.out.kraken2_report_for_multiqc.collect{it[1]}
    )

    if (!params.skip_cleanup) {
        FASTQC.out.zip.join(MULTIQC.out.data, remainder=true)
           .flatten()
           .filter(Path)
           .map { it.delete() }
    }
}