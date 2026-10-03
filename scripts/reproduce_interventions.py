"""Fresh original-input reruns and numerical comparison with previous outputs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from nutriomics_atlas.metabolomics import analyze
from nutriomics_atlas.runner import run_geo
from nutriomics_atlas.validation import validate_output
from nutriomics_atlas.provenance import write_json,file_record,now

def compare_tables(prior,current):
    old=pd.read_csv(prior,sep='\t');new=pd.read_csv(current,sep='\t');keys=['feature_id','contrast']
    if old.duplicated(keys).any() or new.duplicated(keys).any():raise ValueError('Nonunique feature/contrast identities')
    old=old.set_index(keys).sort_index();new=new.set_index(keys).sort_index()
    if not old.index.equals(new.index):raise ValueError('Independent rerun changed feature/contrast universe')
    measures={}
    for field in ('effect_estimate','standard_error','confidence_low','confidence_high','p_value','q_value','n_people'):
        if field not in old and field not in new:continue
        if (field in old)!=(field in new):raise ValueError('Independent rerun changed numeric field availability: '+field)
        a,b=old[field].to_numpy(float),new[field].to_numpy(float)
        both=np.isfinite(a)&np.isfinite(b);delta=float(np.max(np.abs(a[both]-b[both]))) if both.any() else 0.
        same_missing=bool(np.array_equal(np.isnan(a),np.isnan(b)));close=bool(np.allclose(a,b,atol=1e-10,rtol=1e-8,equal_nan=True))
        measures[field]={'max_absolute_difference':delta,'missingness_identical':same_missing,'within_absolute_1e_10_relative_1e_8':close}
    if not {'effect_estimate','p_value','q_value','n_people'}.issubset(measures):raise ValueError('Required effect/p/q/person fields absent')
    return {'rows':len(new),'features':new.index.get_level_values(0).nunique(),'contrasts':new.index.get_level_values(1).nunique(),
      'all_numeric_fields_reproduced':all(v['within_absolute_1e_10_relative_1e_8'] for v in measures.values()),'fields':measures,
      'original_table':file_record(prior),'new_table':file_record(current)}

def run(root,out,accessions,data_dir=None,expansion_root=None,rscript=None,libraries=None,prior_root=None):
    if out.exists():raise FileExistsError('Fresh independent output directory required')
    out.mkdir(parents=True);prior_root=prior_root or root/'artifacts';results=[]
    previous={'ST001257':'st001257-paired-v1','GSE127530':'gse127530-final-v1','GSE56960':'gse56960-final-v1','GSE27385':'gse27385-final-v2'}
    write_json(out/'protocol.json',{'frozen_at':now(),'accessions':accessions,'unit':'Participant; repeated-measures designs retained',
      'old_result_values_used_as_input':False,'numeric_reproduction_atol':1e-10,'numeric_reproduction_rtol':1e-8,
      'raw_CEL_reprocessing_for_GSE56960_GSE27385':True,'original_counts_for_GSE127530':True,'ST001257_source_processed_log2_no_second_log':True})
    for accession in accessions:
        dest=out/accession
        if accession=='ST001257':analyze(root/'artifacts/raw/ST001257',dest,16)
        else:
            if data_dir is None or rscript is None or not libraries:raise ValueError('Explicit raw data and verified R runtime required')
            run_geo(accession,data_dir,expansion_root,dest,rscript,libraries)
        validation=validate_output(dest)
        if validation['errors']:raise ValueError(validation['errors'])
        names=['metabolite_effects.tsv.gz'] if accession=='ST001257' else ['gene_effects.tsv.gz','pathway_effects.tsv.gz']
        comparisons={}
        for name in names:
            prior=prior_root/previous[accession]/name
            comparisons[name]=compare_tables(prior,dest/name) if prior.exists() else {'prior_table_not_available_on_this_machine':True}
        result={'accession':accession,'validation':validation,'comparisons':comparisons,'raw_IDAT_or_instrument_metabolomics_reprocessing':False}
        write_json(dest/'independent_replay.json',result);results.append(result);print(json.dumps(result),flush=True)
    write_json(out/'summary.json',{'completed_at':now(),'results':results,'pipeline_source':file_record(Path(__file__))})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--accessions',nargs='+',choices=['ST001257','GSE127530','GSE56960','GSE27385'],required=True)
    p.add_argument('--data-dir',type=Path);p.add_argument('--expansion-root',type=Path);p.add_argument('--rscript',type=Path);p.add_argument('--r-library',type=Path,nargs='+');p.add_argument('--prior-root',type=Path)
    a=p.parse_args();run(a.root,a.output,a.accessions,a.data_dir,a.expansion_root,a.rscript,a.r_library,a.prior_root)
