# qc_short_read

[[_TOC_]]

## Pipeline overview

**qc_short_read** performs basic preprocessing and quality control (QC) for short-read paired FASTQ datasets.

The pipeline is designed to:

- Clean reads for downstream analysis.
- Run basic QC on short-read file pairs quickly and efficiently.
- Use a shared manifest format compatible with other pipelines.
- Generate an HTML report for sharing results and comparing datasets.
- Generate a pass/fail summary for FastQC, Kraken2/Bracken, and Sylph profiling.

This pipeline allows rapid QC execution before further analysis, helping to filter out low-quality read sets before they undergo resource-intensive downstream processing.

## Usage

### Quickstart

#### From source code

To run the pipeline from source:

1. Clone the repository.
2. Prepare a manifest containing paired FASTQ inputs. See [Manifest of reads](#manifest-of-reads).
3. Run the pipeline:

   ```bash
   qc-short-read --manifest_of_reads manifest.csv
   ```

By default, preprocessing and Sylph profiling are enabled.

See [Parameters](#parameters) for available pipeline options.

#### Using on the Sanger farm

When submitting to the farm, submit the pipeline as a `bsub` job.

For example, to run Kraken2/Bracken profiling with 150 bp reads and species-level classification using the standard Kraken2 database:

```bash
bsub.py 4 <identifier> qc-short-read \
    --manifest_of_reads manifest.csv \
    --bracken_profile true \
    --kraken2_db /data/pam/software/kraken2/standard/ \
    --read_len 150 \
    --classification_level S \
    -ansi-log false
```

We recommend adding `-ansi-log false` to `nextflow run` or `qc-short-read` commands to make logs easier to read when running with LSF.

You can also add `-N <your email>` to be notified when the job has finished.

### Input

#### Manifest of reads

Prepare a minimal input manifest in CSV format with the following headers:

| ID                            | R1         | R2         |
| ----------------------------- | ---------- | ---------- |
| An identifier for your sample | Path to R1 | Path to R2 |

Save the table to a file, for example `manifest.csv`.

#### iRODS input

The pipeline can also retrieve data from iRODS using sequencing identifiers. Provide `--studyid`, `--runid`, `--laneid`, and `--plexid`, or provide a batch of search terms with `--manifest_of_lanes`.

#### Preprocessing

Preprocessing is turned on by default. It can be skipped by specifying `--skip_preprocessing true`.

Preprocessing steps can include trimming, tandem repeat filtering (TRF), and host read removal, depending on the parameters you specify. By default, trimming is on, while TRF and host read removal are off.

- **Trimming** is turned on by default and conducted using Trimmomatic for adapter removal and quality trimming.
- **TRF** can be enabled with `--run_trf true`. Tandem Repeat Finder identifies and removes reads with excessive tandem repeats.
- **Host read removal** can be enabled with `--run_bmtagger true`. BMTagger filters reads that match the specified host genome. The default host genome is T2T-CHM13v2.0.

#### Profiling

The pipeline can generate a Kraken2/Bracken report, a Sylph profile, or both. By default, the pipeline runs Sylph profiling only.

- **Kraken2/Bracken** can be enabled with `--braken_profile true`. Running Kraken2/Bracken requires access to a Kraken2 database, the read length, and the classification level to include in the report.
- **Sylph profiling** requires access to a Sylph database and Sylph taxonomy metadata.

#### Kraken2/Bracken database selection

Centralised Kraken2 databases can be found here:

```text
/data/pam/software/kraken2/
```

Currently installed databases include:

- `bacteria_fungi_protozoa_virus_db`
- `pluspf_20250402`
- `standard/k2_standard_20250402`
- `standard_08gb_20250402`
- `viral_20250402`

Some of these databases are derived from https://benlangmead.github.io/aws-indexes/k2, with names and timestamps derived from those provided on that site.

We recommend using `standard/k2_standard_20250402` for most QC, as Kraken can be very resource intensive when using larger databases.

#### Read length

Ensure the read length matches the sequencing data used. Common read lengths include 75 bp and 150 bp.

#### Classification level

Before running Kraken2/Bracken, choose the taxonomic rank for classification. Available options are:

- `D`: Domain
- `P`: Phylum
- `C`: Class
- `O`: Order
- `F`: Family
- `G`: Genus
- `S`: Species

You will only get a Kraken2/Bracken pass/fail output when using `S` (species rank) classification.

#### Sylph database selection

Centralised Sylph databases can be found here:

```text
/data/pam/software/sylph/
```

Currently installed databases include:

| Database                  | Size   |
| ------------------------- | ------ |
| `tara-eukmags-c200-v0.3`  | 927 MB |
| `gtdb-r226-c1000-dbv1`    | 3.5 GB |
| `uhgg_all_c200_v0.3.0`    | 27 GB  |
| `globdb_r226_sylph_c1000` | 6.5 GB |
| `SMAG-c200-v0.3`          | 2.6 GB |
| `globdb_r226_sylph_c200`  | 33 GB  |
| `gtdb-r220-c200-dbv1`     | 14 GB  |
| `gtdb-r220-c1000-dbv1`    | 2.7 GB |
| `gtdb-r226-c200-dbv1`     | 18 GB  |

The pipeline uses `globdb_r226_sylph_c200/globdb_r226_sylph_c200.syldb` by default. When using larger databases, increase memory for the `SYLPH_PROFILE` process as needed. See the [Configuring our Pipelines with Custom Resources documentation](https://github.com/sanger-pathogens/nextflow-commons/tree/master/configs) for details on adjusting resource allocations for particular processes.

#### K-mer length

The default k-mer length for Sylph is 31, as it is specific enough to be unique in most genomes without being too computationally expensive or resulting in too few common k-mers across samples.

Sylph supports `k = 21` and `k = 31`. Using 21 is less computationally expensive but may reduce specificity.

#### Estimating unclassified reads

By default, Sylph profiling is run with the `-u` flag and `--read-seq-ID 99.5`. To turn off this estimation of unclassified reads, use `--sylph_estimate_unknown false`.

- `-u` enables Sylph to estimate the proportion of classified sequences, where the sum of the `Sequence_abundance` column is the percentage of classified reads.
- `--read-seq-ID` specifies the percentage identity of your sequences, calculated as `100 - error percent`. By default, the pipeline sets this to 99.5, as recommended by Sylph for Illumina reads.
- To specify your own sequence identity, use `--sylph_read_seq_id`.
- To allow Sylph to estimate percentage identity, use `--sylph_read_seq_id false`.

See the [Sylph documentation](https://sylph-docs.github.io/sylph-cookbook/) for additional information.

### Output

Once the pipeline completes, the directory structure will look similar to this:

```text
results/
├── 39214_1#122
│   ├── bracken
│   │   ├── 39214_1#122.bracken
│   │   ├── 39214_1#122_kraken_sample_report_bracken_genuses.tsv
│   │   └── 39214_1#122_report_bracken_species.mpa.txt
│   ├── fastqc
│   │   ├── 39214_1#122_1_fastqc.zip
│   │   └── 39214_1#122_2_fastqc.zip
│   └── kraken2
│       ├── 39214_1#122_kraken_report.tsv
│       └── 39214_1#122_kraken_sample_report.tsv
├── 39214_1#212
│   ├── bracken
│   │   ├── 39214_1#212.bracken
│   │   ├── 39214_1#212_kraken_sample_report_bracken_genuses.tsv
│   │   └── 39214_1#212_report_bracken_species.mpa.txt
│   ├── fastqc
│   │   ├── 39214_1#212_1_fastqc.zip
│   │   └── 39214_1#212_2_fastqc.zip
│   └── kraken2
│       ├── 39214_1#212_kraken_report.tsv
│       └── 39214_1#212_kraken_sample_report.tsv
├── abundance_summary
│   └── bracken_summary_report.tsv
├── metadata_irods_queried_2024-09-12T13:09:24.972011+01:00.csv
└── multiqc
    └── 2024-09-12-report.html
```

Each sample identifier will have its own directory containing the results:

- **Bracken directory**: Contains the `.bracken` file and the Bracken-generated genus-level report.
- **FastQC directory**: Contains the QC reports for Read 1 and Read 2.
- **Kraken2 directory**: Contains the Kraken report and sample report.
- **Sylph directory**: Contains the Sylph profile, `sylph_profile.tsv`.

Additional files include:

- **Bracken species report**: `*_report_bracken_species.mpa.txt`, a MetaPhlAn-style species report for each sample.
- **Abundance summary**: A summary of all samples in a single TSV file, located in `abundance_summary/bracken_summary_report.tsv`.
- **MultiQC report**: An interactive HTML file summarising all preceding reports, located in `multiqc/`.
- **QC pass/fail summary directory**: Contains `sample_pass_fail_qc_summary.tsv`.

If you used iRODS integration, a metadata CSV will also be generated, detailing the metadata retrieved from iRODS.

Download and open the MultiQC HTML report to view the aggregated results interactively.

### Parameters

**Input methods**

| Flag                | Type   | Default | Description                                                          |
| ------------------- | ------ | ------- | -------------------------------------------------------------------- |
| `manifest_of_reads` | `path` | `false` | Manifest containing per-sample paths to `.fastq.gz` files.           |
| `studyid`           | `str`  | `-1`    | Sequencing study ID.                                                 |
| `runid`             | `str`  | `-1`    | Sequencing run ID.                                                   |
| `laneid`            | `str`  | `-1`    | Sequencing lane ID.                                                  |
| `plexid`            | `str`  | `-1`    | Sequencing plex ID.                                                  |
| `target`            | `str`  | `1`     | Marker of key data product likely to be of interest to the customer. |
| `type`              | `str`  | `cram`  | File type.                                                           |
| `manifest_of_lanes` | `path` | `false` | Path to a manifest of search terms for iRODS data retrieval.         |

---

**iRODS extractor processing options**

| Flag                                         | Type   | Default     | Description                                                                  |
| -------------------------------------------- | ------ | ----------- | ---------------------------------------------------------------------------- |
| `cleanup_intermediate_files_irods_extractor` | `bool` | `false`     | Delete intermediate CRAM files downloaded from iRODS in the `work/` folder.  |
| `preexisting_fastq_tag`                      | `str`  | `raw_fastq` | Skip download and processing if expected output FASTQ files exist.           |
| `split_sep_for_ID_from_fastq`                | `str`  | `_1.fastq`  | Separator to recognise sample ID from a pre-existing file.                   |
| `lane_plex_sep`                              | `str`  | `#`         | Separator to build sample ID from `runid`, `laneid`, and `plexid`.           |
| `save_method`                                | `str`  | `nested`    | Save output files in per-sample folders (`nested`) or one folder (`flat`).   |
| `irods_subset_to_skip`                       | `str`  | `phix`      | Skip data items for which the metadata field `subset` is set to this value.  |
| `combine_same_id_crams`                      | `bool` | `false`     | Combine files representing subsets of the same source into a `total` subset. |

---

**Preprocessing options**

| Flag                        | Type   | Default                                                                                                                                             | Description                                                       |
| --------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `publish_clean_reads`       | `bool` | `true`                                                                                                                                              | Save preprocessed reads in the preprocessing output folder.       |
| `publish_trimmomatic_reads` | `bool` | `false`                                                                                                                                             | Publish intermediate reads from Trimmomatic.                      |
| `publish_trf_reads`         | `bool` | `false`                                                                                                                                             | Publish intermediate reads from TRF.                              |
| `run_trimmomatic`           | `bool` | `true`                                                                                                                                              | Run Trimmomatic for adapter removal and quality trimming.         |
| `adapter_fasta`             | `path` | `/data/pam/software/trimmomatic/adapter_fastas/solexa-with-nextseqPR-adapters.fasta`                                                                | Path to FASTA file containing adapter sequences.                  |
| `trim_window_size`          | `int`  | `4`                                                                                                                                                 | Sliding window size for read trimming.                            |
| `trim_baseq`                | `int`  | `20`                                                                                                                                                | Average base quality cutoff for the Trimmomatic sliding window.   |
| `trim_min_length`           | `int`  | `70`                                                                                                                                                | Minimum read length retained after trimming.                      |
| `trimmomatic_options`       | `str`  | `ILLUMINACLIP:{params.adapter_fasta}:2:10:7:1 CROP:151 SLIDINGWINDOW:{params.trim_window_size}:{params.trim_baseq} MINLEN:{params.trim_min_length}` | Trimmomatic command-line options.                                 |
| `run_trf`                   | `bool` | `false`                                                                                                                                             | Run TRF for finding and removing tandem repeats from short reads. |
| `trf_cli_options`           | `str`  | `2 7 7 80 10 50 500 -h -ngs`                                                                                                                        | TRF command-line options.                                         |
| `run_bmtagger`              | `bool` | `false`                                                                                                                                             | Run BMTagger for host read removal.                               |
| `publish_host_data`         | `bool` | `false`                                                                                                                                             | Publish reads determined to originate from the host organism.     |
| `bmtagger_db`               | `path` | `/data/pam/software/bmtagger`                                                                                                                       | Path to directory containing the BMTagger database.               |
| `bmtagger_host`             | `str`  | `T2T-CHM13v2.0`                                                                                                                                     | Reference genome version used for host read filtering.            |

---

**FastQC options**

| Flag          | Type   | Default | Description                |
| ------------- | ------ | ------- | -------------------------- |
| `save_fastqc` | `bool` | `false` | Publish the FastQC output. |

---

**Taxonomy profiling options**

| Flag                          | Type    | Default                                                                  | Description                                                                        |
| ----------------------------- | ------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| `sylph_profile`               | `bool`  | `true`                                                                   | Run Sylph taxonomic classification.                                                |
| `sylph_db`                    | `path`  | `/data/pam/software/sylph/gtdb-r226-c200-dbv1/gtdb-r226-c200-dbv1.syldb` | Path to Sylph database.                                                            |
| `save_sylph_sketches`         | `bool`  | `false`                                                                  | Keep Sylph sketches.                                                               |
| `sketch_size`                 | `int`   | `31`                                                                     | Value of `k` for Sylph. Only `21` and `31` are currently supported.                |
| `sylphtax_db_tag`             | `path`  | `/data/pam/software/sylph-tax/v1/gtdb_r226_metadata.tsv`                 | Path to taxonomy metadata for Sylph.                                               |
| `sylph_estimate_unknown`      | `bool`  | `true`                                                                   | Estimate the proportion of classified sequences.                                   |
| `sylph_read_seq_id`           | `float` | `99.5`                                                                   | Estimated percentage identity of sequences.                                        |
| `bracken_profile`             | `bool`  | `false`                                                                  | Run Kraken2/Bracken taxonomic classification.                                      |
| `kraken2_db`                  | `path`  | `null`                                                                   | Path to the Kraken2 database.                                                      |
| `kraken2_threads`             | `int`   | `4`                                                                      | Number of threads for Kraken2.                                                     |
| `bracken_threads`             | `int`   | `10`                                                                     | Number of threads for Bracken.                                                     |
| `kmer_len`                    | `int`   | `35`                                                                     | K-mer length for Bracken.                                                          |
| `read_len`                    | `int`   | `150`                                                                    | Ideal length of reads in the sample.                                               |
| `braken_classification_level` | `str`   | `S`                                                                      | Taxonomic rank to analyse for Bracken. Options: `D`, `P`, `C`, `O`, `F`, `G`, `S`. |
| `threshold`                   | `int`   | `10`                                                                     | Minimum number of reads required for classification at the specified rank.         |
| `get_classified_reads`        | `bool`  | `false`                                                                  | Retrieve classified reads.                                                         |
| `enable_building`             | `bool`  | `false`                                                                  | Enable automatic building of a Kraken2 database if not found on disk.              |

---

**FastQC QC options**

| Flag                      | Type   | Default                                                         | Description                                                                                |
| ------------------------- | ------ | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| `fastqc_pass_criteria`    | `path` | `assorted-sub-workflows/qc/assets/fastqc_pass_criteria.json`    | JSON array defining FastQC summary items that must have `PASS` for the sample to pass.     |
| `fastqc_no_fail_criteria` | `path` | `assorted-sub-workflows/qc/assets/fastqc_no_fail_criteria.json` | JSON array defining FastQC summary items that must not have `FAIL` for the sample to pass. |

---

**Taxonomy profiling QC options**

| Flag                          | Type  | Default | Description                                            |
| ----------------------------- | ----- | ------- | ------------------------------------------------------ |
| `genus_abundance_threshold`   | `int` | `90`    | Fail the sample if the top genus abundance is lower.   |
| `species_abundance_threshold` | `int` | `85`    | Fail the sample if the top species abundance is lower. |

---

**MultiQC options**

| Flag             | Type   | Default | Description                                          |
| ---------------- | ------ | ------- | ---------------------------------------------------- |
| `multiqc_config` | `path` | `null`  | Supply a config to override the MultiQC base config. |

---

**Logging options**

| Flag              | Type   | Default | Description                 |
| ----------------- | ------ | ------- | --------------------------- |
| `monochrome_logs` | `bool` | `false` | Output logs in plain ASCII. |

### QC pass/fail

A report summary is generated listing all samples and their pass/fail status for FastQC, Kraken2/Bracken profiling, and/or Sylph profiling.

**FastQC pass/fail**

If either of the FASTQs do not meet the required standard for the specified criteria in the FastQC `summary.txt` file, based on the files provided to `--fastqc_pass_criteria` and `--fastqc_no_fail_criteria`, the sample is considered poor quality and a `fail` will be output. Otherwise, a `pass` will be output.

Example FastQC `summary.txt`:

```text
PASS    Basic Statistics    SAMN11586388_1.fastq.gz
PASS    Per base sequence quality   SAMN11586388_1.fastq.gz
PASS    Per sequence quality scores SAMN11586388_1.fastq.gz
WARN    Per base sequence content   SAMN11586388_1.fastq.gz
WARN    Per sequence GC content SAMN11586388_1.fastq.gz
PASS    Per base N content  SAMN11586388_1.fastq.gz
PASS    Sequence Length Distribution    SAMN11586388_1.fastq.gz
PASS    Sequence Duplication Levels SAMN11586388_1.fastq.gz
PASS    Overrepresented sequences   SAMN11586388_1.fastq.gz
FAIL    Adapter Content SAMN11586388_1.fastq.gz
```

Example criteria file:

```json
[
  "Per base sequence quality",
  "Per sequence quality scores",
  "Per base N content"
]
```

If provided to `--fastqc_pass_criteria`, these criteria need a `PASS` for the sample to pass. If provided to `--fastqc_no_fail_criteria`, the criteria need a `PASS` or `WARN` for the sample to pass. Other criteria are allowed to have `FAIL` or `WARN`.

**Taxonomy profiling pass/fail**

If the most abundant genus or species in the Kraken or Sylph report is below a set threshold, the sample is marked as `fail`, meaning it may be contaminated or low quality. If the abundance meets or exceeds the thresholds, the sample is marked as `pass`.

The default thresholds are:

- Genus abundance: `>= 90%`
- Species abundance: `>= 85%`

You can adjust these thresholds using `genus_abundance_threshold` and `species_abundance_threshold`.

### Advanced Usage

#### Running the pipeline with Kraken profiling

For a read length of 150 and classification at species level using the standard Kraken2 database, run:

```bash
qc-short-read \
    --manifest_of_reads manifest.csv \
    --bracken_profile true \
    --kraken2_db /data/pam/software/kraken2/standard/ \
    --read_len 150 \
    --braken_classification_level S
```

#### Running the pipeline with Sylph

For Sylph profiling only, with the default k-mer length of 31 and the default GTDB R226 database, run:

```bash
qc-short-read --manifest_of_reads manifest.csv
```

#### Helper scripts

Helper scripts are available to produce basic descriptive statistics and plots. They can also merge and summarise data from multiple pipeline runs.

Merge and plot multiple Trimmomatic summaries:

```bash
helper_scripts/summarise_trim_stats.py -t *_trimmomatic_statistics.csv -o ./ -p merged_trims
```

Merge and plot multiple Sylph MPA files:

```bash
helper_scripts/summarise_sylph_reports.py --taxon-level s -s *.sylphmpa -o ./ -p merged_sylph
```

Merge MultiQC reports and plot FastQC results:

```bash
helper_scripts/summarise_multiqc_reports.py -m *_general_stats.txt -o ./ -p merged_multiqc_general
```

Each helper script has a help menu that can be accessed with the `-h` flag.

### Dependencies

Pipeline dependencies are containerised. The pipeline can be run with Docker or Singularity.

## Software versions

These Docker images are used as the source to generate Singularity containers that support execution of the Nextflow pipeline:

| Software    | Version | Image URL                                                                                      |
| ----------- | ------- | ---------------------------------------------------------------------------------------------- |
| FastQC      | 0.12.1  | `quay.io/biocontainers/fastqc:0.12.1--hdfd78af_0`                                              |
| Kraken2     | 2.1.3   | `quay.io/biocontainers/kraken2:2.1.3--pl5321hdcf5f25_0`                                        |
| Bracken     | 2.8     | `quay.io/biocontainers/bracken:2.8--py310h0dbaff4_1`                                           |
| Sylph       | 0.8.1   | `gitlab-registry.internal.sanger.ac.uk/sanger-pathogens/docker-images/sylph:0.8.1--ha6fb395_0` |
| Trimmomatic | 0.39    | `quay.io/biocontainers/trimmomatic:0.39--1`                                                    |
| TRF         | 4.09.1  | `quay.io/biocontainers/trf:4.09.1--h031d066_6`                                                 |
| BMTagger    | 3.101   | `quay.io/biocontainers/bmtagger:3.101--h470a237_4`                                             |
| MultiQC     | 1.19    | `quay.io/biocontainers/multiqc:1.19--pyhdfd78af_0`                                             |

## Troubleshooting

If the pipeline fails, check the Nextflow log, process-specific logs, and the contents of the supplied output directory.

Common things to check include:

- The manifest has the required `ID`, `R1`, and `R2` columns.
- Input FASTQ paths are readable from the system where the pipeline is running.
- Kraken2 and Sylph database paths exist and are readable.
- Larger Kraken2 or Sylph databases have enough memory allocated.
- `-ansi-log false` is used when running on the Sanger farm if LSF log output is hard to read.
- The MultiQC report exists under `multiqc/` after the run completes.

## Issues and Contributions

If you find an issue with this pipeline, or would like to suggest an improvement, please log an issue or open a pull request in GitHub.

If you are at Sanger and need internal support, you can also contact the IDS Service Desk. For more information about IDS and to raise a support ticket, read the guidance here: https://fred.sanger.ac.uk/page/6946

For further pipeline-specific information or help, contact [path-help@sanger.ac.uk](mailto:path-help@sanger.ac.uk).
