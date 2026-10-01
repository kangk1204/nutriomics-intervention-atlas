# Nutriomics intervention atlas

Private source-backed reanalysis of human dietary intervention omics. The independent unit is the participant. This repository uses actual raw/processed data with verified sample identities and new statistical execution; old analysis outputs are not adopted.

## Install and verify

```sh
python -m pip install -e '.[dev]'
mkdir -p artifacts
python -m pytest -q --basetemp artifacts/pytest_tmp --junitxml artifacts/test-results.xml
```

Dependencies: NumPy, pandas, SciPy, requests. GEO expression reanalysis additionally requires the explicitly supplied R executable and package libraries. The verified server runtime is R 4.5.3; the runner records actual package versions and rejects a different R version unless `--expected-r-version` is explicitly changed. No R packages are silently installed. If editable installation is unavailable, use `PYTHONPATH=src python -m nutriomics_atlas ...` (PowerShell: `$env:PYTHONPATH = (Join-Path $PWD src)`).

## DASH diet metabolomics: ST001257

```sh
nutriomics-atlas fetch-metabolomics --output-dir artifacts/raw/ST001257
nutriomics-atlas audit-metabolomics --input-dir artifacts/raw/ST001257 \
  --output-dir artifacts/st001257-audit
nutriomics-atlas analyze-metabolomics --input-dir artifacts/raw/ST001257 \
  --output-dir artifacts/st001257-paired-v1 --min-pairs 16
nutriomics-atlas validate --input-dir artifacts/st001257-paired-v1
```

The official [ST001257 study](https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST001257), project PR000843 ([DOI](https://doi.org/10.21228/M8QH5G)), contains 19 people, 76 urine samples and 14 food preparations. The urine design is 19 people × chicken/pork protein arm × pre/post a 6-week DASH-style intervention. The deposited AN002086 analysis is positive-mode Agilent 6520 QTOF with source abundance already log2 transformed. The downloader records URL, retrieval time, bytes and SHA-256 for the official abundance TSV, factors, mwTab and metadata. Instrument raw data are not reprocessed.

Matrix samples must exactly and uniquely match official factor identities. The official arm factor overrides two contradictory sample-name suffixes for participant S31-119; participant identity comes from the source sample label. Every participant must have all four urine cells. Food measurements are kept out of human paired inference. Features are neutral mass/retention-time pairs: they are not confirmed named chemical structures and cannot be equated with PubChem molecules by mass alone. Participant-level transcriptome/metabolome linkage is not supplied by this study.

Primary estimands are within-person post-minus-pre changes in each diet arm. Two-sided Student t tests on paired differences report means, standard errors, 95% intervals and actual feature-specific pair counts; at least 16 of 19 complete pairs are required. BH correction covers all estimable feature × two-arm tests, with separate within-contrast q values retained. Non-finite, missing or constant-difference cases remain unestimated. The zero-retention sensitivity is recorded separately; the actual downloaded snapshot contains no finite zero values. No imputation or second log transformation is applied. Sequence/period covariates and blood-pressure endpoints are unavailable here, so these changes are exploratory associations rather than between-arm causal effects.

The actual initial run has 11,693 features and 904,465 missing cells out of 1,052,370 total (including food preparations). It exports 23,386 feature/contrast rows, 722 estimable tests, and zero q<0.05 results. Sparse coverage and limited sample size restrict inference; absence of FDR-significant features is not proof of no dietary effect. Actual metadata and hashes are recorded in `docs/validated_snapshot.json`.

## Independent GEO full-feature reanalysis

Adapted R code comes from the earlier project's source scripts, with original and adapted hashes recorded in `docs/script_origins.json`. It is executed anew on original input. The runner validates package availability, writes a new execution manifest/log, hashes source code and completed output files, and refuses an already-used run directory.

```sh
nutriomics-atlas run-geo --accession GSE127530 \
  --data-dir /home/keunsoo/projects/nutrigenomics-db/data \
  --output-dir artifacts/gse127530-final-v1 \
  --rscript /home/keunsoo/projects/nutrigenomics-db/toolchain/r-nutrigenomics/bin/Rscript \
  --r-library /home/keunsoo/projects/nutrigenomics-db/toolchain/r-library
```

Use the same arguments with `--accession GSE56960` and a new output directory. For `GSE27385`, additionally supply `--expansion-root /home/keunsoo/projects/nutrigenomics-db/expansion/2026-10-01`. `--preflight-only` checks the runtime before analysis. Original raw inputs are read; staged links and extraction outputs are created under the new run directory. A complete GEO count audit or sample sheet is re-derived from source metadata rather than previous result tables.

| Study | People / assays | Input and primary model | Limits |
|---|---:|---|---|
| GSE127530 | 5 / 45 | Audited original/fixed RNA-seq counts; TMM, voom, day/time design and person-blocked duplicateCorrelation; three planned post/fast contrasts | Mixed high-fat challenge, small cohort; no isolated-nutrient causal estimates |
| GSE56960 | 14 / 168 | Raw CEL RMA; one unambiguous Entrez gene per probe; person-blocked limma with 12 dose-by-time change contrasts comparing 1000/1500 to 500 kcal | 7 people per metabolic-status group; whole-meal contrasts |
| GSE27385 | 11 / 33 | Raw CEL RMA; unique GPL570 Entrez mapping; person and period fixed effects; fish oil/placebo and fenofibrate/placebo | Fish-oil mixture cannot identify EPA versus DHA; fenofibrate is a drug comparator |

Effects are exported for all admitted features, not a hand-picked display panel. Ambiguous probe targets are excluded with an explicit feature crosswalk. GSE127530 retains depositor gene symbols and separately freezes strict one-to-one Entrez annotations; aliases mapping to the same gene are excluded from pathway rankings rather than selected by observed t values. Primary q values cover all prespecified gene × contrast tests in a study; pathway tests form a separate family. Gene estimates have confidence intervals. Reactome package annotations are exported with exact membership hashes and are labeled legacy snapshots rather than current Reactome releases. fgsea random seeds are fixed; GSE56960/27385 also export person-level CAMERA sensitivity.

## Record completed execution

```sh
python scripts/record_validation.py \
  --input-dir artifacts/st001257-paired-v1 artifacts/gse127530-final-v1 \
    artifacts/gse56960-final-v1 artifacts/gse27385-final-v1 \
  --junit artifacts/test-results.xml --output docs/validated_snapshot.json
```

`validate` checks feature/contrast uniqueness, p/q bounds, independent-person counts, the primary BH family, required uncertainty and recorded output hashes. The summary includes only directories containing actually completed analysis metadata and explicitly lists unexecuted primary cohorts. These independent cohorts can be joined through reviewed public molecular identifiers for database integration; they are not same-person multiomics fusion, clinical response prediction, or a validated personalized diet prescription.

`audit-inventory --source-roots /path/old-data /path/old-expansion /path/research-metadata --analysis-dirs artifacts/gse127530-final-v1 artifacts/gse56960-final-v1 artifacts/gse27385-final-v2 --output docs/prior_cohort_inventory.json` audits the earlier eight catalog study groups. It separates reported people, observed source sample records, resolved participant candidates and actually completed new analyses. GSE54690 and GSE27387 SuperSeries are containers; child assay subsets and acute/chronic visits do not add independent cohorts. Missing/unresolved subject identities and cohorts without new full-feature execution remain explicit. No unique participant total is fabricated across overlapping or unresolved assay subsets.
