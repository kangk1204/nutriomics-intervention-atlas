# Software and data licenses

## Project software

The original code and documentation in this repository are distributed under the [MIT License](LICENSE). Dependencies installed through Python, R or Bioconductor retain their own licenses.

## Research data

The software license applies to this project's implementation. External datasets, annotations, publications and pretrained model weights retain the terms set by their providers. Cite the original study and accession when using a research dataset. Input hashes, analysis settings and source identifiers accompany the results in `docs/`.

| Resource | Use in this project | Source and terms |
|---|---|---|
| NCBI GEO: GSE127530, GSE56960 and GSE27385 | Expression studies, sample metadata and processed analysis inputs | [GEO disclaimer](https://www.ncbi.nlm.nih.gov/geo/info/disclaimer.html) and [GEO FAQ](https://www.ncbi.nlm.nih.gov/geo/info/faq.html). NCBI places no restrictions on use or distribution of GEO data; rights held by submitters still apply. Cite the accession and original publication. |
| Metabolomics Workbench: ST001257 | Metabolomics feature identifiers, sample metadata and paired-response analysis | [Study record](https://www.metabolomicsworkbench.org/data/DRCCMetadata.php?Mode=Study&StudyID=ST001257). The [data sharing policy](https://www.metabolomicsworkbench.org/data/datasharing.php) states that released data are in the public domain and requests citation of the accession and associated publication. Its [website terms](https://www.metabolomicsworkbench.org/about/termsofuse.php) apply separately to articles and web pages. |
| Reactome | Gene-to-pathway membership tables | [Reactome license](https://reactome.org/license): data and derived data are CC0. The tables identify their Reactome source; Reactome illustrations are not bundled. |

## Reused project code

The R analysis scripts were adapted from the author's NutriGenomics project, which is MIT-licensed. The [script origins](docs/script_origins.json) record the original and adapted checksums. R and Bioconductor packages are installed separately under their respective licenses.

The processed GSE27385 RDS file, feature crosswalks and sample tables support reproduction of the published analyses. They retain the source-study identifiers. The MIT software license does not change the rights in external study data or platform annotations.
