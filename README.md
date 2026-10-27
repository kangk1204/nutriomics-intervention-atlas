**English** | [한국어](README.ko.md)

# NutriOmics Dietary Intervention Atlas

This repository reanalyzes gene expression and urinary metabolomics data from human dietary intervention studies. It maps participants, treatments, periods and sampling times, then estimates effects and multiple-testing corrections while accounting for repeated measurements from the same person.

[Cohort results and input hashes](docs/validated_snapshot.json) | [Dataset inventory](docs/prior_cohort_inventory.json) | [Analysis script sources](docs/script_origins.json) | [Project report, restricted access](https://github.com/kangk1204/nutriomics-final-report)

## Studies analyzed

Analyses of these four studies were completed on October 1, 2026. Participant counts and measurement counts are reported separately.

| Study | Research focus | Participants | Measurements | Analysis |
|---|---|---:|---|---|
| GSE127530 | Postprandial gene expression over time | 5 | 45 | TMM and voom, accounting for repeated measurements within participants |
| GSE56960 | Gene expression by meal energy and time | 14 | 168 | RMA normalization of raw CEL files; energy and time contrasts |
| GSE27385 | Expression responses to fish oil, placebo and fenofibrate | 11 | 33 | RMA normalization of raw CEL files; participant and period effects |
| ST001257 | Urinary responses to chicken and pork conditions within a DASH diet | 19 | 76 urine samples and 14 food preparations | Within-participant differences before and after intake |

Each study is analyzed independently. Consistent result formats support comparisons of shared genes and pathways across studies.

## What the results contain

Gene expression and metabolomics results include the study ID, measured feature, contrast, effect size, standard error or confidence interval, p-value and FDR-adjusted value. Units and input file hashes connect each result to its source data.

For ST001257, **11,693 analytical features** defined by mass and retention time were compared under two conditions. Of 23,386 result rows, **722 tests** had at least 16 matched before-and-after pairs and could be estimated. After Benjamini-Hochberg correction across all tests, **0 results had q < 0.05**.

Feature names identify mass-spectrometry signals, with compound identification treated separately. The reported estimates describe before-and-after changes within each condition. Sequence and period information were unavailable for the crossover design, so a causal contrast between the two food conditions was not estimated.

## Analysis workflow

1. Retrieve data and sample metadata from the official repositories.
2. Map participants, treatments, periods and sampling times.
3. Apply platform-specific preprocessing and quality control.
4. Estimate contrasts with statistical models that reflect the study design.
5. Save result tables, sample tables and validation records with input and output hashes.

For GSE56960, the analysis compares 1,000 and 1,500 kcal meals with 500 kcal meals at each time point. GSE27385 includes fish oil versus placebo and fenofibrate versus placebo contrasts. ST001257 uses the supplied log2 values; its analysis settings specify missing-value handling and the minimum number of matched pairs.

## Installation and use

Use Python 3.11 or later.

```sh
python -m pip install -e ".[dev]"
nutriomics-atlas --help
python -m pytest -q
```

Retrieve, check and analyze ST001257 as follows:

```sh
nutriomics-atlas fetch-metabolomics --output-dir artifacts/raw/ST001257
nutriomics-atlas audit-metabolomics --input-dir artifacts/raw/ST001257 --output-dir artifacts/st001257-audit
nutriomics-atlas analyze-metabolomics --input-dir artifacts/raw/ST001257 --output-dir artifacts/st001257-paired --min-pairs 16
nutriomics-atlas validate --input-dir artifacts/st001257-paired
```

Expression analyses use R and Bioconductor packages. Run `nutriomics-atlas run-geo --help` for data directories, output directories and R executable options. The [script source record](docs/script_origins.json) documents the analysis scripts and original project paths.

## Accessing and using the results

The [validation results](docs/validated_snapshot.json) record participant and sample counts, analysis settings, result row counts and file hashes for each study. Large source files and complete result tables are held in research data storage.

The [NutriOmics DB web platform](https://github.com/kangk1204/nutriomics-db) provides food composition and intervention-result queries. Within-person analyses use verified participant links. Omics results from different cohorts are connected as study-specific evidence.

Source datasets are available from the corresponding NCBI GEO and Metabolomics Workbench study records. The repository files and [source inventory](docs/script_origins.json) document code reuse. Each source dataset retains its provider's terms.

The code is available under the [MIT License](LICENSE). [Software and data licenses](DATA_LICENSES.md) lists the sources and terms for external data and software.
