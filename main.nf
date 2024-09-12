include { FASTQC } from './modules/fastqc.nf'
include { MULTIQC } from './modules/multiqc.nf'

//
// SUBWORKFLOWS
//
include { COMBINE_IRODS ; 
          COMBINE_READS   } from './assorted-sub-workflows/combined_input/subworkflows/combined_input.nf'
include { IRODS_EXTRACTOR } from './assorted-sub-workflows/irods_extractor/subworkflows/irods.nf'
include { KRAKEN2BRACKEN } from './assorted-sub-workflows/kraken2bracken/subworkflows/kraken2bracken.nf'

def logo = NextflowTool.logo(workflow, params.monochrome_logs)

log.info logo

NextflowTool.commandLineParams(workflow.commandLine, log, params.monochrome_logs)


def printHelp() {
    NextflowTool.help_message("${workflow.ProjectDir}/schema.json", 
                               ["${workflow.ProjectDir}/assorted-sub-workflows/combined_input/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/irods_extractor/schema.json",
                                "${workflow.ProjectDir}/assorted-sub-workflows/kraken2bracken/schema.json"],
    params.monochrome_logs, log)
}


workflow {
    if (params.help) {
        printHelp()
        exit 0
    }

    COMBINE_IRODS
    | IRODS_EXTRACTOR
    | COMBINE_READS

    COMBINE_READS.out.all_reads_ready_to_map_ch
    | map { meta, read1, read2 -> tuple(meta, [read1, read2])} //made the input for FASTQC the same as kraken2bracken but can be whatever really if we want to change kraken2bracken
    | (FASTQC & KRAKEN2BRACKEN)

    MULTIQC(
        FASTQC.out.zip.collect{it[1,2]},
        KRAKEN2BRACKEN.out.ch_kraken2_style_bracken_reports.collect{it[1]}
    )

    if (!params.skip_cleanup) {
        FASTQC.out.zip.join(MULTIQC.out.data, remainder=true)
           .flatten()
           .filter(Path)
           .map { it.delete() }
    }
}