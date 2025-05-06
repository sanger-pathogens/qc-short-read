process MULTIQC {
    label 'cpu_1'
    label 'mem_10'
    label 'time_30m'

    container 'quay.io/biocontainers/multiqc:1.19--pyhdfd78af_0'

    publishDir "${params.outdir}/multiqc/", mode: 'copy', overwrite: true

    input:
    path('*')
    path('*')

    output:
    path("${date}-report.html"), emit: report
    path("*_data.tar.gz"), emit: data
    path("*_plots.tar.gz"), optional:true, emit: plots

    script:
    def custom_config = params.multiqc_config ? "--config ${params.multiqc_config}" : "--config ${projectDir}/multiqc_config/multiqc_config.yml"
    //workflow start is ugly 2024-02-29T12:01:26.233465Z split on T for time and take just the date
    date = "${workflow.start}".split('T')[0]
    """
    multiqc \
        -n ${date}-report.html \
        -f \
        ${custom_config} \
        .

    tar -czf ${date}_data.tar.gz -C *report_data --exclude 'multiqc_data.json' --transform='s,^./,data/,' .
    if [[ -d ${date}-report_plots ]]; then
        tar -czf ${date}_plots.tar.gz -C *report_plots/svg  --transform='s,^./,plots/,' .
    fi
    """
}