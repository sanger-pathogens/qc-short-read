include { FASTQC } from './modules/fastqc.nf'
include { MULTIQC } from './modules/multiqc.nf'

include { INPUT_CHECK    } from './assorted-sub-workflows/combined_input/subworkflows/input_check.nf'
include { KRAKEN2BRACKEN } from './assorted-sub-workflows/kraken2bracken/subworkflows/kraken2bracken.nf'

workflow {

    INPUT_CHECK(params.manifest)
    | map { meta, read1, read2 -> tuple(meta, [read1, read2])} //made the input for FASTQC the same as kraken2bracken but can be whatever really if we want to change kraken2bracken
    | (FASTQC & KRAKEN2BRACKEN)

    MULTIQC(
        FASTQC.out.zip.collect{it[1]},
        KRAKEN2BRACKEN.out.ch_kraken2_style_bracken_reports
    )

    if (!params.skip_cleanup) {
        FASTQC.out.zip.join(MULTIQC.out.data, remainder=true)
           .flatten()
           .filter(Path)
           .map { it.delete() }
    }
}