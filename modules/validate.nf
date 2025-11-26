// validation helper functions

def validate_parameters() {
    int errors = 0
    println "start parameter validation"

    /*
     * Validate consistency between preprocessing and skip_preprocessing
     */
    if (params.preprocessing == params.skip_preprocessing) {
        log.error("Contradiction: --preprocessing is ${params.preprocessing} but --skip_preprocessing is also ${params.skip_preprocessing}. These cannot both be ${params.preprocessing}.")
        log.error("If preprocessing is enabled, skip_preprocessing must be false and preprocessing true. If preprocessing is disabled, skip_preprocessing must be true and preprocessing false.")
        errors++
    }

    /*
     * Final error check
     */
    if (errors > 0) {
        log.error(String.format("%d errors detected", errors))
        exit 1
    }

    println "end parameter validation"
}
