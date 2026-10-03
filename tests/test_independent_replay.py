import importlib.util
from pathlib import Path
import pandas as pd
import pytest

spec=importlib.util.spec_from_file_location('reproduce',Path(__file__).resolve().parents[1]/'scripts/reproduce_interventions.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def table():
    return pd.DataFrame({'feature_id':['g1','g2'],'contrast':['A','A'],'effect_estimate':[.2,.1],'p_value':[.1,.2],'q_value':[.2,.2],'n_people':[14,14]})

def test_pathway_comparison_does_not_require_unavailable_CI(tmp_path):
    a,b=tmp_path/'old.tsv',tmp_path/'new.tsv';table().to_csv(a,sep='\t',index=False);table().to_csv(b,sep='\t',index=False)
    report=module.compare_tables(a,b);assert report['all_numeric_fields_reproduced'];assert 'confidence_low' not in report['fields']

def test_rerun_cannot_silently_drop_uncertainty_field(tmp_path):
    old=table();old['confidence_low']=.0;a,b=tmp_path/'old.tsv',tmp_path/'new.tsv';old.to_csv(a,sep='\t',index=False);table().to_csv(b,sep='\t',index=False)
    with pytest.raises(ValueError,match='availability'):module.compare_tables(a,b)

def test_distinct_feature_universe_fails(tmp_path):
    old=table();new=table();new.loc[0,'feature_id']='replacement';a,b=tmp_path/'old.tsv',tmp_path/'new.tsv';old.to_csv(a,sep='\t',index=False);new.to_csv(b,sep='\t',index=False)
    with pytest.raises(ValueError,match='universe'):module.compare_tables(a,b)
