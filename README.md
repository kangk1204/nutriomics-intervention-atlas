# NutriOmics 식이중재 분석

사람 식이중재 연구의 유전자 발현과 소변 대사체 자료를 재분석하는 코드입니다. 참가자, 처치, 기간과 측정 시점을 정리하고, 같은 사람의 반복측정을 반영해 효과크기와 다중검정 보정값을 산출합니다.

[코호트별 결과와 입력 해시](docs/validated_snapshot.json) · [자료 목록](docs/prior_cohort_inventory.json) · [분석 코드 출처](docs/script_origins.json) · [통합 보고서](https://github.com/kangk1204/nutriomics-final-report)

## 분석한 연구

2026년 10월 1일 완료한 네 연구의 결과를 보관합니다. 사람 수와 측정 수는 각각 집계합니다.

| 연구 | 연구 내용 | 참가자 | 측정 수 | 분석 방법 |
|---|---|---:|---:|---|
| GSE127530 | 식후 시간별 유전자 발현 | 5명 | 45개 | TMM·voom, 참가자 내 반복측정 반영 |
| GSE56960 | 식사 열량·시간별 유전자 발현 | 14명 | 168개 | 원시 CEL의 RMA 정규화, 열량·시간별 대비 |
| GSE27385 | 어유·위약·fenofibrate의 발현 변화 | 11명 | 33개 | 원시 CEL의 RMA 정규화, 참가자·기간 반영 |
| ST001257 | DASH 식이의 닭고기·돼지고기 조건별 소변 변화 | 19명 | 소변 76개, 식품 조제물 14개 | 참가자별 섭취 전후 차이 |

각 연구를 독립적으로 분석하며, 연구 간 공통 유전자·경로를 비교할 수 있도록 결과 형식을 맞췄습니다.

## 결과가 담고 있는 것

유전자·대사체 결과에는 연구 ID, 측정 특징, 비교 조건, 효과크기, 표준오차 또는 신뢰구간, p값과 FDR 보정값을 저장합니다. 자료 단위와 입력 파일 해시를 함께 기록해 결과를 원자료까지 추적할 수 있습니다.

ST001257은 질량·머무름 시간으로 정의한 **11,693개 분석 특징**을 두 조건에서 비교했습니다. 전체 23,386개 결과 행 중 최소 16쌍의 전후 측정을 확보한 **722개 검정**이 추정 가능했고, 전체 검정에 BH 보정을 적용했을 때 **q < 0.05인 결과는 0개**였습니다.

이 자료의 특징명은 질량분석 신호를 가리킵니다. 화합물 동정과는 구분해 제공하며, 조건별 전후 차이를 연구 결과로 보고합니다. 교차설계의 순서·기간 정보가 없어 두 식품 조건 사이의 인과효과는 추정하지 않았습니다.

## 분석 흐름

1. 공식 제공처에서 자료와 시료 정보를 확보합니다.
2. 참가자·처치·기간·시점의 대응표를 만듭니다.
3. 플랫폼별 전처리와 품질관리를 수행합니다.
4. 연구 설계에 맞는 통계모형으로 대비를 계산합니다.
5. 결과표·시료표·검증 기록을 저장하고 입력·출력 해시를 연결합니다.

GSE56960에서는 500 kcal 대비 1,000·1,500 kcal의 시간별 비교를, GSE27385에서는 어유·위약과 fenofibrate·위약의 비교를 산출합니다. ST001257은 제공된 log2 값을 사용하고 결측 처리와 최소 전후 쌍 수를 분석 조건에 명시했습니다.

## 설치와 실행

Python 3.11 이상에서 설치합니다.

```sh
python -m pip install -e ".[dev]"
nutriomics-atlas --help
python -m pytest -q
```

ST001257은 다음 순서로 수집·확인·분석합니다.

```sh
nutriomics-atlas fetch-metabolomics --output-dir artifacts/raw/ST001257
nutriomics-atlas audit-metabolomics --input-dir artifacts/raw/ST001257 --output-dir artifacts/st001257-audit
nutriomics-atlas analyze-metabolomics --input-dir artifacts/raw/ST001257 --output-dir artifacts/st001257-paired --min-pairs 16
nutriomics-atlas validate --input-dir artifacts/st001257-paired
```

발현 분석은 R과 Bioconductor 패키지를 사용합니다. `nutriomics-atlas run-geo --help`에서 자료·출력 폴더와 R 실행 경로를 지정하는 방법을 확인할 수 있습니다. 사용한 스크립트와 원 연구 자료의 위치는 [분석 코드 출처](docs/script_origins.json)에 있습니다.

## 자료 확인과 활용

[검증 결과](docs/validated_snapshot.json)에서 연구별 참가자·시료 수, 분석 조건, 결과 행 수와 파일 해시를 확인할 수 있습니다. 대용량 원자료와 전체 결과표는 연구 데이터 저장소에 보관합니다.

식품 성분량과 중재 결과를 함께 조회하는 웹은 [NutriOmics DB](https://github.com/kangk1204/nutriomics-db)에서 제공합니다. 참가자 연결이 확인된 자료만 개인 내 분석에 사용하며, 서로 다른 코호트의 오믹스 결과는 연구별 근거로 연결합니다.

원자료는 NCBI GEO와 Metabolomics Workbench의 해당 연구에서 확보합니다. 코드와 재사용 내역은 이 저장소의 파일 및 [출처 목록](docs/script_origins.json)에, 원자료의 이용조건은 각 제공기관에 따릅니다.
