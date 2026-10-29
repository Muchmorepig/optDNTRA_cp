> Historical five-environment profile, superseded by ../../UPGRADE.md.
> Referenced environment files and locks belong to commit a349e79b86a7664388f9b4b6a740718f30bd3593.

# Tool refresh — 2026-10-29

The workflow uses the latest stable tool versions available from the configured
Bioconda/conda-forge channels at the audit date. Pre-release eggNOG-mapper 3 builds
are not used. Python and transitive dependencies are **compatible runtimes**, not
necessarily the newest releases. The top-level YAML files pin tools; the Linux
explicit locks under `envs/locks/linux-64/` record the complete tested builds.

| Tool | Previous | Current | Environment |
|---|---:|---:|---|
| fastp | 0.23.4 | 1.4.0 | core |
| FastQC | 0.12.1 | 0.13.0 | core |
| CD-HIT | 4.8.1 | 4.8.1 | core |
| TransDecoder | 5.7.1 | 6.0.0 | core |
| BLAST | 2.16.0 | 2.17.0 | core |
| HMMER | 3.4 | 3.4 | core |
| seqtk | 1.4 | 1.5 | core |
| DIAMOND | 2.1.10 | 2.2.8 | core |
| Snakemake | 7.32.4 | 9.27.1 (minimal) | core |
| SAMtools | 1.21 | 1.25 | core |
| Bowtie2 | 2.5.4 | 2.5.5 | core / Trinity |
| Salmon | unpinned | 2.8.0 | core / Trinity |
| Trinity | 2.15.2 | 2.15.2 | Trinity |
| RSEM | 1.3.3 | 1.3.3 | Trinity |
| edgeR | 4.0.16 | 4.10.7 | Trinity |
| BUSCO | 5.7.1 | 6.1.0 | BUSCO |
| OMArk | 0.3.0 | 0.5.0 | OMArk |
| eggNOG-mapper | 2.1.12 | 2.1.15 | eggNOG |

The full package-source audit is in `version-audit.json`. Queries used
`https://api.anaconda.org/package/{channel}/{package}` and Mamba's actual solver;
the API's `latest_version` field can lag the highest stable version in its file
list (as observed for Snakemake). Upstream references:
[Trinity releases](https://github.com/trinityrnaseq/trinityrnaseq/releases),
[Snakemake releases](https://github.com/snakemake/snakemake/releases),
[Salmon migration guide](https://github.com/COMBINE-lab/salmon/blob/master/MIGRATION.md),
[eggNOG-mapper releases](https://github.com/eggnogdb/eggnog-mapper/releases).

## Why separate environments are required

- **Trinity/RSEM vs SAMtools:** current Trinity/RSEM builds require HTSlib below
  1.25; SAMtools 1.25 requires HTSlib 1.25. The core has the latest SAMtools,
  while Trinity/RSEM use their compatible HTSlib/SAMtools dependencies in
  `optDNTRA-trinity`. Quantification is still RSEM/Bowtie2, as in the old workflow.
- **eggNOG vs DIAMOND:** eggNOG-mapper 2.1.15 requires DIAMOND `<2.1`.
  Its conda recipe relaxes Python dependencies, but its installed Python metadata
  still pins Biopython 1.76, psutil 5.7.0 and XlsxWriter 1.4.3. These exact
  dependencies and Python 3.8 are confined to `optDNTRA-eggnog`; they are not
  installed over the modern core. This legacy runtime is required to satisfy the
  published stable package's metadata without modifying or suppressing it.
- **OMArk:** 0.5.0 constrains SQLite to `<=3.40.0`, incompatible with Python
  3.12 builds. Its environment uses Python 3.10.
- **Snakemake:** 9.27.1 constrains `packaging<26`; interface-common 1.23.1's Python
  metadata requires `packaging>=26.1`. Pin interface-common 1.22.0, retaining
  Snakemake 9.27.1. Do not upgrade that dependency independently.
- No pip overlay is used. All five environments must pass `python -m pip check`.

## Runtime compatibility fixes

- Resolve TransDecoder 6's phase executables under `util/`, with a fallback for
  TransDecoder 5 installations. Keep the existing staged DIAMOND/Pfam evidence.
- Accept names such as `trinity.Trinity.fasta` and `sample.clean_R1.fastq.gz`;
  preserve `.fastq.gz` when creating workflow outputs and processing sample sheets.
- Initialize the missing timer in the single-end, no-trimming branch (previously
  raised `NameError: startTime` after linking the input reads).
- Launch Snakemake through an argument list, explicitly target `all`, propagate
  the workflow module path, and avoid old version-specific quiet syntax.
- Ignore user R startup files for workflow subprocesses so external R libraries
  do not shadow the environment's edgeR.
- Build DIAMOND indexes inside the output tree, not beside shared reference data.
- BUSCO 6 plots use JSON summaries and `busco --plot`. An actual nonempty PNG is
  required; no empty placeholder is created.
- eggNOG annotation requires the complete local database (`eggnog.db`,
  `eggnog.taxa.db`, `eggnog_proteins.dmnd`). Download it separately using the
  official downloader in the matching environment; the workflow no longer fetches
  only one SQLite file and pretends the database is ready.

## Trinity with Salmon 2

Run Trinity through `scripts/run_trinity.py` in the Trinity environment. The
wrapper changes PATH only for that subprocess and does not patch installed
Trinity or Salmon files. For Trinity's internal Salmon call it:

1. Detects the real Salmon major version; Salmon 1 arguments are unchanged.
2. Removes `--minAssignedFrags 1` for Salmon 2 and verifies the resulting
   `quant.sf` has at least one assigned fragment. Other thresholds are rejected.
3. Streams Trinity's internal FASTA reads into a temporary FASTQ, preserving
   names and sequences and assigning placeholder `I` qualities (the original
   internal FASTA has no quality scores). Temporary disk usage is proportional
   to the internal reads; the conversion is removed on exit.

Use a **new output directory** when changing Salmon major versions. Salmon 1 and
2 indexes are incompatible. The adapter does not silently reuse or delete indexes.
Salmon 2 is a new implementation and numerical results need not equal Salmon 1;
the regression tests establish executability, not biological equivalence.

## Validation scope

`environment-validation.json` records dependency metadata checks. Automated
tests cover suffix handling, command arguments, TransDecoder layout, Salmon
threshold handling, FASTA conversion, and isolated commands. The full core smoke
test uses synthetic coding transcripts and matched reads, a clearly synthetic
protein reference and HMM, and real installed executables. It asserts final
transcript/protein correspondence and verifies reference indexes stay in outputs.

Optional BUSCO/OMArk/eggNOG environments are checked for installation, dependency
consistency and CLI compatibility. This is **not** a validation of annotation
accuracy or a full database-backed run of those modules. No research reads or
reference databases are published in this repository.

Measured local checks are recorded in `test-results.json`: core synthetic test
56.50 s; core with fastp/FastQC 62.96 s; single-end 55.50 s; tiny Trinity/Salmon 2
15.76 s. A separate real *Ceratopteris richardii* subset (600 assembled transcripts,
existing filtered reads, real local Swiss-Prot/Pfam) completed in 408.60 s with
549 final transcript/protein pairs. Optional-module dry-run and BUSCO 6 plotting
with a synthetic summary also passed. Installation time is not included.
