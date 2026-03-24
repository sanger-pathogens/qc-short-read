// validation helper functions

def validate_parameters() {
    int errors = 0
    println "start parameter validation"

    /*
     * Final error check
     */
    if (errors > 0) {
        log.error(String.format("%d errors detected", errors))
        exit 1
    }

    println "end parameter validation"
}
