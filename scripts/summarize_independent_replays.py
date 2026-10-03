"""Aggregate only validated finished cohort reruns, retaining failed-run context."""
import argparse
import json
from pathlib import Path
import sys
import csv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nutriomics_atlas.provenance import file_record,write_json,now

def summarize(inputs,output):
    required={'ST001257','GSE127530','GSE56960','GSE27385'};rows=[];seen=set();table_rows=[]
    for directory in inputs:
        path=directory/'independent_replay.json';row=json.loads(path.read_text());acc=row['accession']
        if acc in seen:raise ValueError('Duplicate cohort rerun cannot count twice')
        if row['validation']['errors']:raise ValueError('Unvalidated rerun cannot be summarized as completed')
        row['receipt']=file_record(path);rows.append(row);seen.add(acc)
        metadata=json.loads((directory/'analysis_metadata.json').read_text())
        for name,stats in row['validation']['tables'].items():
            compared=row['comparisons'].get(name)
            if compared is None: continue
            table_rows.append({'accession':acc,'independent_people':row['validation']['independent_people'],
                'assays':metadata.get('sample_count',metadata.get('urine_samples')),'table':name,**stats,
                'all_numeric_fields_reproduced':compared['all_numeric_fields_reproduced'],
                'max_absolute_numeric_difference':max(v['max_absolute_difference'] for v in compared['fields'].values()),
                'normalization':metadata.get('normalization',metadata.get('units')),
                'receipt_sha256':row['receipt']['sha256']})
    missing=sorted(required-seen)
    result={'generated_at':now(),'completed_cohorts':sorted(seen),'missing_cohorts':missing,'all_four_cohorts_reexecuted':not missing,
      'all_numeric_comparisons_reproduced':not missing and all(all(v.get('all_numeric_fields_reproduced',False) for v in r['comparisons'].values()) for r in rows),
      'source_processed_ST001257_recomputed_not_instrument_raw':True,'original_count_GSE127530_recomputed_not_FASTQ_alignment':True,
      'original_CEL_GSE56960_GSE27385_RMA_recomputed':True,'patient_multiomics_fusion_claim':False,'cohorts':rows}
    write_json(output,result)
    columns=list(dict.fromkeys(k for r in table_rows for k in r))
    with output.with_suffix('.tsv').open('w',newline='',encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=columns,delimiter='\t');writer.writeheader();writer.writerows(table_rows)
    print(json.dumps({'completed':sorted(seen),'missing':missing,'all_numeric_reproduced':result['all_numeric_comparisons_reproduced']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--inputs',type=Path,nargs='+',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();summarize(a.inputs,a.output)
