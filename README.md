# QC-short-read

[![Singularity](https://img.shields.io/badge/Singularity-blue.svg)](https://singularity.lbl.gov/) 
[![Nextflow](https://img.shields.io/badge/Nextflow-brightgreen.svg)](https://www.nextflow.io/) 
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Conda](https://img.shields.io/badge/Conda-green.svg)](https://docs.conda.io/en/latest/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)

---

Welcome to the **QC-short-read** repository.

## Documentation

Comprehensive documentation for this project is hosted on the wiki. You can access it via the sidebar, or by clicking the link below:

🔗 [Wiki](../../wikis/home)

> **Note**: Please refer to the Usage details, and troubleshooting information.

## The wiki information is written from the perspective of using the tool outside the sanger systems.

# If you plan to clone this repository

You should tailor your profile to match the container method you wish to use:

This is changed with the flag:
```
-profile
```

Supported options are:

* singularity
* docker
* conda

excluding any profiles defaults to use LSF intergration as well as singularity for containers