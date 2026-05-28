# QC-short-read

[[_TOC_]]

## Pipeline overview

QC-short-read is a Nextflow DSL2 pipeline for quality control and taxonomic profiling of short-read Illumina sequencing data. It accepts data from multiple input sources and produces per-sample FastQC reports, Kraken2/Bracken taxonomic profiles, and an aggregated MultiQC summary.

The pipeline performs the following steps:

1. **Input** — reads are loaded (see [Input](#input)).
2. **Preprocessing** — optional adapter trimming and read length filtering (default: enabled).
3. **QC** — FastQC is run on each sample; Kraken2 performs taxonomic classification and Bracken re-estimates species-level abundances.
4. **Reporting** — MultiQC aggregates FastQC and Kraken2 results into a single HTML report.

[![Singularity](https://img.shields.io/badge/Singularity-blue.svg)](https://singularity.lbl.gov/)
[![Nextflow](https://img.shields.io/badge/Nextflow-brightgreen.svg)](https://www.nextflow.io/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)

## Usage

### Quickstart

#### From source code

1. Clone this repository with its submodules:

   ```bash
   git clone --recurse-submodules https://gitlab.internal.sanger.ac.uk/sanger-pathogens/pipelines/qc-short-read.git
   cd qc-short-read
   ```

2. To run with `docker`, use the `-profile docker` option:

   ```bash
   nextflow run main.nf \
       -profile docker \
       --manifest path/to/manifest.csv \
       --outdir my_output
   ```

   Other profiles are also supported (`singularity`, `conda`).
   :warning: If no profile is specified the pipeline will run with the Sanger HPC-specific configuration.

3. Once the run has finished, clean up intermediate files:

   ```bash
   rm -rf work .nextflow*
   ```

#### Using on the Sanger farm

First load the latest pipeline module:

```bash
module load qc-short-read
```

Then run on the command line with `qc-short-read <options>`. For instance, to see a help message:

```bash
qc-short-read --help
```

Submit to LSF:

```bash
bsub -o output.o -e error.e -q oversubscribed -R "select[mem>4000] rusage[mem=4000]" -M4000 \
    qc-short-read \
        --manifest path/to/manifest.csv \
        --outdir my_output
```

### Input

#### Manifest (`--manifest`)

A CSV file with the required header `ID,R1,R2`, containing per-sample paths to paired `.fastq.gz` files:

```
ID,R1,R2
sampleA,/path/to/sampleA_1.fastq.gz,/path/to/sampleA_2.fastq.gz
sampleB,/path/to/sampleB_1.fastq.gz,/path/to/sampleB_2.fastq.gz
```

#### Generating a manifest

**Sanger users:** the [manifest_generator](https://gitlab.internal.sanger.ac.uk/sanger-pathogens/pipelines/manifest_generator/) tool can generate a compatible `ID,R1,R2` manifest from a directory of FASTQ files or from iRODS.

#### Other input modes

This pipeline supports additional input modes via the `mixed_input` sub-workflow — these can be combined in a single run:

- **iRODS** (Sanger internal) — specify `--studyid`, `--runid`, `--laneid`, and/or `--plexid` on the command line; at least `--studyid` or `--runid` is required. A batch CSV of multiple iRODS searches can be supplied via `--manifest_of_lanes`. Requires an active iRODS session (`iinit`).
- **ENA download** — supply a file of ENA accession IDs via `--manifest_ena`. Set `--accession_type` to `run` (default), `sample`, or `study`.
- **Directory scan** — provide a path to a directory of FASTQ files via `--manifest_from_dir`. Use `--fastq_validation` (`strict`/`relaxed`, default: `strict`) and `--max_depth` (default: `0`) to control discovery.

Run `--help` for the full parameter list.

### Output

Results are written to `--outdir` (default: `./results`):

```
results/
  fastqc/
    <sample_ID>_fastqc.html        # Per-sample FastQC HTML report
    <sample_ID>_fastqc.zip
  kraken2/
    <sample_ID>.kraken2.report     # Kraken2 classification report
  bracken/
    <sample_ID>.bracken            # Bracken species-level abundance estimates
  multiqc/
    multiqc_report.html            # Aggregated MultiQC report
    multiqc_data/
```

### Parameters

**MultiQC options**

| Option             | Type   | Default | Description                                             |
| ------------------ | ------ | ------- | ------------------------------------------------------- |
| `--multiqc_config` | `path` | `""`    | Supply a custom MultiQC config to override the default. |

---

**Logging options**

| Option              | Type      | Default | Description                                            |
| ------------------- | --------- | ------- | ------------------------------------------------------ |
| `--monochrome_logs` | `boolean` | `false` | Output logs in plain ASCII (disable coloured logging). |

---

**Other options**

| Option            | Type      | Default | Description                                              |
| ----------------- | --------- | ------- | -------------------------------------------------------- |
| `--skip_cleanup`  | `boolean` | `false` | Skip cleanup of intermediate MultiQC files.              |
| `--preprocessing` | `boolean` | `true`  | Run the preprocessing (adapter trimming) step before QC. |

---

**Kraken2/Bracken options**

| Option                           | Type      | Default                                                    | Description                                                                              |
| -------------------------------- | --------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `--kraken2_db`                   | `path`    | `/data/pam/software/kraken2/standard/k2_standard_20250402` | Path to the Kraken2 database.                                                            |
| `--bracken_classification_level` | `string`  | `S`                                                        | Taxonomic rank for Bracken re-estimation. Options: `D`, `P`, `C`, `O`, `F`, `G`, `S`.    |
| `--read_len`                     | `integer` | `150`                                                      | Expected read length for Bracken (used to select the k-mer length during re-estimation). |

### Advanced usage

#### Running outside of Sanger

The Kraken2 database defaults to a Sanger-internal path. To run outside of Sanger, download a Kraken2 database (e.g. the [standard database](https://benlangmead.github.io/aws-indexes/k2)) and supply its path via `--kraken2_db`.

#### iRODS input

When using iRODS input, authenticate first with `iinit` and use the `--studyid` / `--runid` parameters. See `qc-short-read --help` for all available iRODS filtering options.

### Dependencies

All dependencies are containerised. The Kraken2 database must be available locally (see above for external users).

## Software versions

Key software used by the pipeline sub-workflows:

| Software | Version | Image                             |
| -------- | ------- | --------------------------------- |
| FastQC   | —       | `quay.io/biocontainers/fastqc:*`  |
| Kraken2  | —       | `quay.io/biocontainers/kraken2:*` |
| Bracken  | —       | `quay.io/biocontainers/bracken:*` |
| MultiQC  | —       | `quay.io/biocontainers/multiqc:*` |

See the `assorted-sub-workflows/qc/modules/` and `assorted-sub-workflows/kraken2bracken/modules/` directories for pinned container versions.

## Troubleshooting

- **Kraken2 database not found**: check that `--kraken2_db` points to a directory containing a valid Kraken2 database. On the Sanger HPC the default path should be available.
- **iRODS authentication**: if using iRODS input, run `iinit` before launching the pipeline.
- **Resuming a failed run**: add `-resume` to your command to restart from cached intermediate results.
- For further help, check `.nextflow.log` and the per-process logs in the `work/` directory.

## Issues and Contributions

If you find an issue with this pipeline, or would like to suggest an improvement, please log an issue or open a pull request on this repository.

If you are at Sanger and need internal support, you can raise an issue on the PAM Freshservice portal: https://sanger.freshservice.com/support/catalog/items/426
