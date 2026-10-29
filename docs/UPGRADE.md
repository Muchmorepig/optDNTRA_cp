# Compatible unified environment — 2026-10-29

The recommended profile prioritizes compatibility and reproducibility, not the
newest release of every tool or Python. Install `environment.yml` to create
`optDNTRA-stable`. It contains the core workflow, Trinity/RSEM, BUSCO and OMArk.
Only optional eggNOG annotation requires `envs/eggnog.yml`.

| Component | Recommended version |
|---|---:|
| Python | 3.11 |
| Trinity / RSEM | 2.15.2 / 1.3.3 |
| Salmon | 1.10.3 |
| SAMtools | 1.21 |
| edgeR | 4.4.0 |
| BUSCO | 6.1.0 |
| OMArk | 0.3.0 |
| Snakemake | 9.27.1 |
| pandas | 2.3.3 |
| eggNOG-mapper (optional separate environment) | 2.1.15 |

Other direct dependencies are pinned in `environment.yml`; complete tested
Linux x86-64-v4 builds (including CPU-specific dependencies) are recorded in `envs/locks/linux-64/core.txt`.

## Compatibility decisions

- Python 3.11 is sufficient for the workflow and Snakemake. pandas 2.3.3 has
  compatible builds; pandas 3.1 is unnecessary for this workflow.
- Salmon 1.10.3 supports Trinity's existing internal interface. The Salmon 2
  adapter remains available for custom installations, but is not required by
  the recommended environment.
- SAMtools 1.21 avoids the HTSlib 1.25 requirement that conflicts with Trinity
  and RSEM builds. edgeR 4.4.0 allows the R, Augustus and Qt dependencies to
  coexist; Mamba solved and installed the complete combination.
- OMArk 0.3.0 avoids the restrictive SQLite cap in newer recipes. Its database
  must match the installed OMAmer version; an arbitrary newest database is not
  guaranteed compatible.
- Snakemake interface-common remains pinned to 1.22.0 because newer metadata
  conflicts with Snakemake's `packaging<26` constraint.
- eggNOG-mapper stays isolated: its DIAMOND `<2.1` requirement and exact Python
  metadata dependencies (Biopython 1.76, psutil 5.7.0, XlsxWriter 1.4.3) conflict
  with the main environment. The optional lock uses Python 3.8.

No pip overrides or ignored dependency checks are used. Existing installed
five-environment profiles are not deleted or modified. Set `trinity_env`,
`busco_env`, and `omark_env` to empty strings in older configuration files to
use the current environment; explicit external environment settings still work.

## Retained workflow fixes

The workflow retains dotted FASTA/FASTQ filename handling, TransDecoder 6 utility
resolution, argument-safe Snakemake launch, single-end timer initialization,
R startup isolation, output-local DIAMOND indexes, BUSCO 6 JSON-based plotting,
and complete eggNOG database validation. Use a new assembly output directory
when changing Salmon versions; old indexes must not be silently reused.

## Validation

Current measurements are in `test-results.json` and dependency/CLI checks in
`environment-validation.json`. Synthetic tests exercise real executables with
small generated inputs, including preprocessing, paired/single-end optimization
and a three-transcript Trinity assembly. They do not establish biological
accuracy. BUSCO, OMArk and eggNOG database-backed assessments are not claimed
as fully tested by these small checks.

The previous five-environment audit and results are preserved under
`history/five-environments/` as historical records; their versions and timings
do not describe the recommended unified environment.
