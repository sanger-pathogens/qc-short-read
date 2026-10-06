# QC-short-read

[![Singularity](https://img.shields.io/badge/Singularity-blue.svg)](https://singularity.lbl.gov/)
[![Nextflow](https://img.shields.io/badge/Nextflow-brightgreen.svg)](https://www.nextflow.io/)
[![Docker](https://img.shields.io/badge/Docker-blue.svg)](https://www.docker.com/)

[[_TOC_]]

## Pipeline overview

QC-short-read is a Nextflow DSL2 pipeline for quality control and taxonomic profiling of short-read Illumina sequencing data. It accepts data from multiple input sources and produces per-sample FastQC reports, Kraken2/Bracken taxonomic profiles, and an aggregated MultiQC summary.

The pipeline performs the following steps:

1. **Input** — reads are loaded (see [Input](#input)).
2. **Preprocessing** — Preprocessing steps can include trimming (default: enabled), and host read removal (default: disabled), depending on the parameters you specify .
3. **QC** — FastQC is run on each sample; Kraken2 performs taxonomic classification and Bracken re-estimates species-level abundances; Sylph performed community profiling and abundance estimation which requires access to a Sylph database and Sylph taxonomy metadata.
4. **Reporting** — MultiQC aggregates FastQC and Kraken2 results into a single HTML report.

## Usage

### Quickstart

#### From source code

1. Clone this repository with its submodules:

   ```bash
   git clone --recurse-submodules <repo-url>
   cd qc-short-read
   ```

2. To run the pipeline using Docker container to support module dependencies, use the `-profile docker` option:

   ```bash
   nextflow run main.nf -profile docker [options]
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
    qc-short-read [options]
```

#### From code archive downloaded from the Github Release section or from Zenodo

Please be aware that the code archive asset attached to a release will have empty folders for the dependcy submodules `assorted-sub-workflows` ([repository](https://github.com/sanger-pathogens/assorted-sub-workflows)) and `lib` (points to `nextflowtool` [repository](https://github.com/sanger-pathogens/nextflowtool)). The code executed from these archives will therefore **NOT** be functional. Unfortunately, the `.git` folder will be missing too, meaning that it is not a working `git` repository and submodule folders _cannot_ be populated with `git submodule init`.

It is thus recommended to use the `git clone` approach described above, adding the commands below to get the code version referred to in the release:

```bash
git checkout <revision_tag> # e.g. revision_tag can be "v2.0.0"
git pull --recurse-submodules
```

### Input

#### Manifest (`--manifest`)

A CSV file with the required header `ID,R1,R2`, containing per-sample paths to paired `.fastq.gz` files:

```
ID,R1,R2
sampleA,/path/to/sampleA_1.fastq.gz,/path/to/sampleA_2.fastq.gz
sampleB,/path/to/sampleB_1.fastq.gz,/path/to/sampleB_2.fastq.gz
```

#### Other input modes

This pipeline supports additional input modes via the `mixed_input` sub-workflow — these can be combined in a single run:

- **iRODS** (Sanger users only) — specify `--studyid`, `--runid`, `--laneid`, and/or `--plexid` on the command line; at least `--studyid` or `--runid` is required. A batch CSV of multiple iRODS searches can be supplied via `--manifest_of_lanes`. Requires an active iRODS session (`iinit`).
- **ENA download** — supply a file of ENA accession IDs via `--manifest_ena`. Set `--accession_type` to `run` (default), `sample`, or `study`.

Run `--help` for the full parameter list.

#### Kraken2bracken options

**Sanger users only** databases that can be found here:
`/data/pam/software/kraken2/`

Currently installed databases are:

```
bacteria_fungi_protozoa_virus_db
bacteria_fungi_protozoa_virus_db_08062026
16S_Greengenes13.5_20200326
16S_RDP11.5_20200326
16S_Silva138_20200326
pluspf_20250402
standard/k2_standard_20250402
standard_08gb_20250402
viral_20250402
```

To select the read length passed to bracken, supply the argument `--read_len` (default: `150`). Classification can be specified by the taxonomic rank using `bracken_classification_level` (default:`S`).

#### Sylph options

**Sanger users only** Sylph databases that can be found here:
`/data/pam/software/sylph/`

Currently installed databases are:

```
bacteria_fungi_protozoa_virus_db_07042026.syldb
bacteria_fungi_protozoa_virus_db.syldb
fungi_refseq_db.syldb
globdb_r226_sylph_c1000
globdb_r226_sylph_c200
gtdb_full_r226.syldb
gtdb-r220-c1000-dbv1
gtdb-r220-c200-dbv1
gtdb-r226-c1000-dbv1
gtdb-r226-c200-dbv1
gtdb-r232-c1000-dbv1
gtdb-r232-c200-dbv1
SMAG-c200-v0.3
tara-eukmags-c200-v0.3
uhgg_all_c200_v0.3.0
```

Please not that the `.syldb` file must be supplied and some are contained with subdirectories along with README.md files. Additionally, the kmer size selected must match the kmer sizes used to sketch the databases.

The default k-mer length for sylph is `31`. Sylph supports `k = 21` or `k = 31`.

#### Pre-processing and QC

Detailed pre-processing options can be found [here](#parameters) or by accessing the help menu in the pipeline by running `nextflow run qc-short-read/main.nf -h` or `qc-short-read -h` as a Sanger user after [loading the module](#using-on-the-sanger-farm-hpc). To turn the pre-processing subworkflow on/off use the `--preprocessing` options (default: `true`).

#### BMTagger database

The indexes for the complete human genome assemblies `hg38` and `T2T-CHM13v2.0` are available at `/data/pam/software/bmtagger` on the Sanger HPC.

For external users, download from [NCBI](https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_009914755.1/) and build the BMTagger index. For information on how to build the database, please refer to [the workflow documentation](./assorted-sub-workflows/mags_maker/metawrap_qc/README.md).

To decontaminate against another human reference genome or a host other than human, provide a different BMTagger database prefix to `--bmtagger_db` and set `--bmtagger_host` to the corresponding reference name.

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

**Input options**

Multiple input options are available, and can be combined. Providing at least one is mandatory.

| Option                                          | Type   | Default | Description                                                                                                                                                                                                                   |
| ----------------------------------------------- | ------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--manifest_of_reads`                           | `path` | `null`  | Input manifest CSV with required header `ID,R1,R2`.                                                                                                                                                                           |
| `--manifest`                                    | `path` | `null`  | Same as `--manifest_of_reads` (alias).                                                                                                                                                                                        |
| `--manifest_of_lanes`                           | `path` | `null`  | **Sanger users only:** Input manifest CSV for submission of multiple iRODS (meta)data queries; various header fields can be used that refer to iRODS metadata fields, including `sudyid`,`runid`,`laneid`,`plexid` or `type`. |
| `--manifest_ena`                                | `path` | `null`  | Input manifest for submission of multiple ENA (meta)data queries; no header required, the only required content should be ENA accessions, one per line. This option should be accopanied by the `--accession_type` option.    |
| `--accession_type`                              | `str`  | `"run"` | One of the following types: `run`, `study`, `sample`.                                                                                                                                                                         |
| `sudyid`,`runid`,`laneid`,`plexid`, `type`, ... | `str`  | `null`  | **Sanger users only:** Individual fields to be combined to form a single iRODS query (similar syntax as with `--manifest_of_lanes`, but resulting in a separate, additional query).                                           |

For more information, please read [the MIXED_INPUT workflow documentation](./assorted-sub-workflows/README.md).

---

**Logging options**

| Option              | Type      | Default | Description                                            |
| ------------------- | --------- | ------- | ------------------------------------------------------ |
| `--monochrome_logs` | `boolean` | `false` | Output logs in plain ASCII (disable coloured logging). |

---

**General pre-processing options**

| Option                        | Type      | Default | Description                                                                                                                |
| ----------------------------- | --------- | ------- | -------------------------------------------------------------------------------------------------------------------------- |
| `--skip_cleanup`              | `boolean` | `false` | Skip cleanup of intermediate MultiQC files.                                                                                |
| `--skip_preprocessing`        | `boolean` | `false` | Run the preprocessing (adapter trimming) step before QC.                                                                   |
| `--publish_clean_reads`       | `boolean` | `true`  | Save the pre-processed reads (gzip-compressed) in the `preprocessing/` output folder.                                      |
| `--publish_trimmomatic_reads` | `boolean` | `false` | Publish intermediate reads from the Trimmomatic process during pre-processing. Read sets will be uncompressed FASTQ files. |

---

**FastQC options**

| Option                      | Type      | Default                                                         | Description                                                                                                                                                                |
| --------------------------- | --------- | --------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--save_fastqc`             | `boolean` | `false`                                                         | Publish FastQC output.                                                                                                                                                     |
| `--fastqc_pass_criteria`    | `path`    | `assorted-sub-workflows/qc/assets/fastqc_pass_criteria.json`    | JSON file defining an array of items in the FastQC `summary.txt` that must have the value `PASS` for the sample to be considered a pass.                                   |
| `--fastqc_no_fail_criteria` | `path`    | `assorted-sub-workflows/qc/assets/fastqc_no_fail_criteria.json` | JSON file defining an array of items in the FastQC `summary.txt` that must NOT have the value `FAIL` for the sample to be considered a pass (i.e. they could have `WARN`). |

---

**Trimmomatic options**

| Option                  | Type      | Default                                                                                                                                                 | Description                                                                         |
| ----------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `--run_trimmomatic`     | `boolean` | `true`                                                                                                                                                  | Run Trimmomatic for adapter removal and trimming for quality.                       |
| `--adapter_fasta`       | `path`    | `/data/pam/software/trimmomatic/adapter_fastas/solexa-with-nextseqPR-adapters.fasta`                                                                    | **Default related to Sanger only** Path to fasta file containing adapter sequences. |
| `--trim_window_size`    | `integer` | `4`                                                                                                                                                     | Sliding window size for read trimming.                                              |
| `--trim_baseq`          | `integer` | `20`                                                                                                                                                    | Average base quality cutoff for the sliding window for Trimmomatic.                 |
| `--trim_min_length`     | `integer` | `70`                                                                                                                                                    | Minimum read length retained following trimming.                                    |
| `--trimmomatic_options` | `string`  | `ILLUMINACLIP:${params.adapter_fasta}:2:10:7:1 CROP:151 SLIDINGWINDOW:${params.trim_window_size}:${params.trim_baseq} MINLEN:${params.trim_min_length}` | Trimmomatic command line options.                                                   |

> Note: there is also the possibility to run the tandem repeat finder (TRF) tool with `--run_trf` but this behaviour is deprecated and turned off by default; we don't recommend turning it on as repeat removal is mostly thought to degrade sequencing data.

---

**Bmtagger options**

| Option                | Type      | Default                       | Description                                                                        |
| --------------------- | --------- | ----------------------------- | ---------------------------------------------------------------------------------- |
| `--run_bmtagger`      | `boolean` | `false`                       | Run bmtagger for host read removal.                                                |
| `--publish_host_data` | `boolean` | `false`                       | Publish the reads determined to originate from the host organism.                  |
| `--bmtagger_db`       | `path`    | `/data/pam/software/bmtagger` | **Default related to Sanger only** Path to directory containing BMTagger database. |
| `--bmtagger_host`     | `string`  | `T2T-CHM13v2.0`               | Reference genome version used for host read filtering.                             |

**MultiQC options**

| Option             | Type   | Default | Description                                             |
| ------------------ | ------ | ------- | ------------------------------------------------------- |
| `--multiqc_config` | `path` | `""`    | Supply a custom MultiQC config to override the default. |

---

**Kraken2/Bracken options**

| Option                           | Type      | Default                                                    | Description                                                                                                                                                                           |
| -------------------------------- | --------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--kraken2_db`                   | `path`    | `/data/pam/software/kraken2/standard/k2_standard_20250402` | Path to the Kraken2 database. Users external to Sanger will have to download an appropriate [Kraken2 database](#running-outside-of-sanger).                                           |
| `--kraken2_threads`              | `integer` | `4`                                                        | Number of threads for Kraken2.                                                                                                                                                        |
| `--bracken_threads`              | `integer` | `10`                                                       | Number of threads for Bracken.                                                                                                                                                        |
| `--kmer_len`                     | `integer` | `35`                                                       | K-mer length for Bracken.                                                                                                                                                             |
| `--read_len`                     | `integer` | `150`                                                      | Expected read length for Bracken (used to select the k-mer length during re-estimation).                                                                                              |
| `--bracken_classification_level` | `string`  | `S`                                                        | Taxonomic rank for Bracken re-estimation. Options: `D`, `P`, `C`, `O`, `F`, `G`, `S`. Classification accuracy cannot be checked at species level unless this is set to `S` (species). |
| `--threshold`                    | `integer` | `10`                                                       | Minimum number of reads required for a classification at the specified rank.                                                                                                          |
| `--get_classified_reads`         | `boolean` | `false`                                                    | Retrieve classified reads.                                                                                                                                                            |
| `--enable_building`              | `boolean` | `false`                                                    | Enable automatic building of the Kraken2 database if it is not found on disk.                                                                                                         |

---

**Sylph options**
| Option | Type | Default | Description |
| -------------------------------- | --------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
taxo profile Subworkflow Options
| `--sylph_profile` | `boolean` | `true` | Run sylph taxonomic classification.
| `--sylph_db` | `path` | `/data/pam/software/sylph/gtdb-r226-c200-dbv1/gtdb-r226-c200-dbv1.syldb` | **Default related to Sanger only** Path to sylph database. |
| `--save_sylph_sketches` | `boolean` | `false` | Keep sylph sketches. |
| `--sketch_size` | `integer` | `31` | Value of k. Only k = 21, 31 are currently supported. |
| `--sylphtax_db_tag` | `path` | `/data/pam/software/sylph-tax/v1/gtdb_r226_metadata.tsv` | **Default related to Sanger only** Path to the sylph-tax metadata TSV to use for taxprof. |
| `--bracken_profile` | `boolean` | `false` | Run Kraken2Bracken taxonomic classification.

### Running outside of Sanger

#### Kraken2 databases

The Kraken2 database defaults to a Sanger-internal path. To run outside of Sanger, download a Kraken2 database (e.g. the [standard database](https://benlangmead.github.io/aws-indexes/k2)) and supply its path via `--kraken2_db`.

#### Sylph databases

Pre-sketched sylph databases are available on the sylph [website](https://sylph-docs.github.io/pre%E2%80%90built-databases/). Should you require a custom database you can follow their documentartion [here](https://sylph-docs.github.io/sylph-cookbook/#database-sketching-options).

#### Trimmomatic

Users of the pipeline who want to be able to preprocess their reads (including adapter removal) will need to supply a fasta file of their adapters uisng the `--adapter_fasta` option.

### Dependencies

All dependencies are containerised.

Key software used by the pipeline sub-workflows:

| Software    | Version | Image                                                   |
| ----------- | ------- | ------------------------------------------------------- |
| FastQC      | 0.12.1  | `quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0`       |
| Kraken2     | 2.1.3   | `quay.io/biocontainers/kraken2:2.1.3--pl5321hdcf5f25_0` |
| Bracken     | 2.8     | `quay.io/biocontainers/bracken:2.8--py310h0dbaff4_1`    |
| MultiQC     | 1.19    | `quay.io/biocontainers/multiqc:1.19--pyhdfd78af_0`      |
| Sylph       | 0.8.1   | `quay.io/biocontainers/sylph:0.8.1--ha6fb395_0`         |
| Sylphtax.   | 1.2.0.  | `quay.io/biocontainers/sylph-tax:1.2.0--pyhdfd78af_0`   |
| Trimmomatic | 0.39    | `quay.io/biocontainers/trimmomatic:0.39--1`             |
| TRF         | 4.09.1  | `quay.io/biocontainers/trf:4.09.1--h031d066_6`          |
| Bmtagger    | 3.101.  | `quay.io/biocontainers/bmtagger:3.101--h470a237_4`      |

See the `assorted-sub-workflows/qc/modules/` and `assorted-sub-workflows/kraken2bracken/modules/` directories for pinned container versions.

## Troubleshooting

- **Kraken2 database not found**: check that `--kraken2_db` points to a directory containing a valid Kraken2 database. On the Sanger HPC the default path should be available.
- **BMTagger database not found**: ensure `--bmtagger_db` points to a directory containing a valid BMTagger index for the selected host reference. On the Sanger HPC the default path `/data/pam/software/bmtagger` should be available.
- **Out of memory for BMTagger**: BMTagger loads the full database into memory. The default resource allocation uses 16 GB RAM; request more via a custom config if needed.
- **iRODS authentication**: if using iRODS input, run `iinit` before launching the pipeline.
- **Resuming a failed run**: add `-resume` to your command to restart from cached intermediate results.
- For further help, check `.nextflow.log` and the per-process `.command.log` logs in the `work/` directory.

Sanger users may find [this page](https://ssg-confluence.internal.sanger.ac.uk/spaces/PaMI/pages/181078206/General+pipeline+info#Generalpipelineinfo-Troubleshootingafailedpipelinerunandsendingabugreport) useful for troubleshooting Nextflow pipeline runs.

## Issues and Contributions

**GitHub users:** if you find an issue with this pipeline, or would like to suggest an improvement, please log an issue or open a pull request on this repository.

**Sanger users:** if you need internal support, you can raise an issue on the PAM Freshservice portal: https://sanger.freshservice.com/support/catalog/items/426
