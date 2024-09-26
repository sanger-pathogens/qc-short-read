# QC-short-read

[![Singularity](https://img.shields.io/badge/Singularity-blue.svg)](https://singularity.lbl.gov/) 
[![Nextflow](https://img.shields.io/badge/Nextflow-brightgreen.svg)](https://www.nextflow.io/) 
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Conda](https://img.shields.io/badge/Conda-green.svg)](https://docs.conda.io/en/latest/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)

---

Welcome to the **QC-short-read** repository.

## Documentation

Comprehensive documentation for this project is hosted on confluence. You can access it via the sidebar, or by clicking the link below:

🔗 [External Wiki](https://ssg-confluence.internal.sanger.ac.uk/display/PaMI/QC+short+read)

> **Note**: Please refer to the external wiki for setup instructions, usage details, and troubleshooting information.

##If you plan to clone the repository
#The wiki information is written from the perspective of using the tool on the sanger systems.

To instead use this tool from a cloned repository the executable changes from

```
qc-short-read
```

to instead

```
nextflow run .
```

In additon to that you should tailor your profile to match the container method you wish to use options are:

-profile
* singularity
* docker
* conda
