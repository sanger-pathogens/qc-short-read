# QC-short-read

[![Singularity](https://img.shields.io/badge/Singularity-blue.svg)](https://singularity.lbl.gov/)
[![Nextflow](https://img.shields.io/badge/Nextflow-brightgreen.svg)](https://www.nextflow.io/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)

[[_TOC_]]

## Pipeline overview

QC-short-read is a Nextflow DSL2 pipeline for quality control and taxonomic profiling of short-read Illumina sequencing data. It accepts data from multiple input sources and produces per-sample FastQC reports, Kraken2/Bracken taxonomic profiles, and an aggregated MultiQC summary.

The pipeline performs the following steps:

1. **Input** — reads are loaded (see [Input](#input)).
2. **Preprocessing** — optional adapter trimming and read length filtering (default: enabled).
3. **QC** — FastQC is run on each sample; Kraken2 performs taxonomic classification and Bracken re-estimates species-level abundances.
4. **Reporting** — MultiQC aggregates FastQC and Kraken2 results into a single HTML report.

## Usage

### Quickstart

#### From source code

1. Clone this repository with its submodules:

   ```bash
   git clone --recurse-submodules <repo-url>
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

3. Once the run has finished successfully and you have inspected the output, clean up intermediate files. The `work/` directory and `.nextflow.log` are useful for troubleshooting — do not delete them until you are satisfied the outputs are correct:

   ```bash
   rm -rf work .nextflow*
   ```

   Alternatively, use `nextflow clean` for more fine-grained control over which runs and intermediate files are removed.

#### Using on the Sanger "farm" HPC

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
jobname="my_qc_short_read_run" # you can edit this!
bsub -o ${jobname}.%J.o -e ${jobname}.%J.e -J ${jobname} -q oversubscribed -R "select[mem>4000] rusage[mem=4000]" -M4000 \
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

**Sanger users only:** the [manifest_generator](https://gitlab.internal.sanger.ac.uk/sanger-pathogens/pipelines/manifest_generator/) tool can generate a compatible `ID,R1,R2` manifest from a directory of FASTQ files or from iRODS.

#### Other input modes

This pipeline supports additional input modes via the `mixed_input` sub-workflow — these can be combined in a single run:

- **iRODS** (Sanger users only) — specify `--studyid`, `--runid`, `--laneid`, and/or `--plexid` on the command line; at least `--studyid` or `--runid` is required. A batch CSV of multiple iRODS searches can be supplied via `--manifest_of_lanes`. Requires an active iRODS session (`iinit`).
- **ENA download** — supply a file of ENA accession IDs via `--manifest_ena`. Set `--accession_type` to `run` (default), `sample`, or `study`.
- **Directory scan** — provide a path to a directory of FASTQ files via `--manifest_from_dir`. Use `--fastq_validation` (`strict`/`relaxed`, default: `strict`) and `--max_depth` (default: `0`) to control discovery.

Run `--help` for the full parameter list.

### Output

Results are written to `--outdir` (default: `./results`):

```
results/
  <sample_ID>/
    kraken2/
      <sample_ID>_kraken_sample_report.tsv      # Kraken2 per-sample classification report
      <sample_ID>_kraken_report.tsv.gz          # Full Kraken2 output (if --publish_full_kraken_report)
    bracken/
      <sample_ID>.bracken                       # Bracken species-level abundance estimates
      <sample_ID>_kraken_sample_report_bracken_*.tsv  # Kraken-style Bracken report
      <sample_ID>_report_bracken_species.mpa.txt      # MPA-format Bracken abundance report
    sylph/
      <sample_ID>_sylph_profile.tsv             # Sylph taxonomic profile (if --sylph_profile)
      <sample_ID>.sylphmpa                      # Sylph MPA-format report (if --sylph_profile)
      <sample_ID>.paired.sylsp                  # Sylph sketch file (if --save_sylph_sketches)
    fastqc/
      <sample_ID>_1_fastqc.zip                  # FastQC zip archives (if --save_fastqc)
      <sample_ID>_2_fastqc.zip
    preprocessing/                              # Preprocessed FASTQ files (if --publish_clean_reads)
      <sample_ID>_preprocessed_1.fastq.gz
      <sample_ID>_preprocessed_2.fastq.gz
  abundance_summary/
    bracken_summary_report.tsv                  # Combined Bracken abundance across all samples
  qc_pass_fail_summary/
    sample_pass_fail_qc_summary.tsv             # Per-sample QC pass/fail status
  preprocessing_summary_stats/
    *_statistics.csv                            # Preprocessing read count statistics
  multiqc/
    multiqc_report.html                         # Aggregated MultiQC HTML report
  host_reads/                                   # Host reads extracted during preprocessing (if --publish_host_reads)
    *_host*.fastq.gz
  manifest/
    manifest.csv                                # Auto-generated manifest (only when using --manifest_from_dir)
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
| `--kraken2_db`                   | `path`    | `/data/pam/software/kraken2/standard/k2_standard_20250402` | Path to the Kraken2 database. Users external to Sanger will have to download an approrriate [Kraken2 database](#running-outside-of-sanger)      |
| `--bracken_classification_level` | `string`  | `S`                                                        | Taxonomic rank for Bracken re-estimation. Options: `D`, `P`, `C`, `O`, `F`, `G`, `S`.    |
| `--read_len`                     | `integer` | `150`                                                      | Expected read length for Bracken (used to select the k-mer length during re-estimation). |

### Advanced usage

#### Running outside of Sanger

The Kraken2 database defaults to a Sanger-internal path. To run outside of Sanger, download a Kraken2 database (e.g. the [standard database](https://benlangmead.github.io/aws-indexes/k2)) and supply its path via `--kraken2_db`.


### Dependencies

All dependencies are containerised. The Kraken2 database must be available locally (see above for external users).

## Software versions

Key software used by the pipeline sub-workflows:

| Software | Version | Image                                                   |
| -------- | ------- | ------------------------------------------------------- |
| FastQC   | 0.12.1  | `quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0`       |
| Kraken2  | 2.1.3   | `quay.io/biocontainers/kraken2:2.1.3--pl5321hdcf5f25_0` |
| Bracken  | 2.8     | `quay.io/biocontainers/bracken:2.8--py310h0dbaff4_1`    |
| MultiQC  | 1.19    | `quay.io/biocontainers/multiqc:1.19--pyhdfd78af_0`      |

See the `assorted-sub-workflows/qc/modules/` and `assorted-sub-workflows/kraken2bracken/modules/` directories for pinned container versions.

## Troubleshooting

- **Kraken2 database not found**: check that `--kraken2_db` points to a directory containing a valid Kraken2 database. On the Sanger HPC the default path should be available.
- **iRODS authentication**: if using iRODS input, run `iinit` before launching the pipeline.
- **Resuming a failed run**: add `-resume` to your command to restart from cached intermediate results.
- For further help, check `.nextflow.log` and the per-process `.command.log` logs in the `work/` directory.

Sanger users may find [this page](https://ssg-confluence.internal.sanger.ac.uk/spaces/PaMI/pages/181078206/General+pipeline+info#Generalpipelineinfo-Troubleshootingafailedpipelinerunandsendingabugreport) useful for troubleshooting Nextflow pipeline runs.

## Issues and Contributions

**GitHub users:** if you find an issue with this pipeline, or would like to suggest an improvement, please log an issue or open a pull request on this repository.

**Sanger users:** if you need internal support, you can raise an issue on the PAM Freshservice portal: https://sanger.freshservice.com/support/catalog/items/426
