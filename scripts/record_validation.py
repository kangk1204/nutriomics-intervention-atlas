from __future__ import annotations
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from nutriomics_atlas.validation import validate_output
from nutriomics_atlas.provenance import write_json,now,sha256

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input-dir',nargs='+',type=Path,required=True);parser.add_argument('--junit',type=Path);parser.add_argument('--output',type=Path,default=Path('docs/validated_snapshot.json'));args=parser.parse_args()
    result={'recorded_at':now(),'schema_version':1,'cohorts':[],'patient_multiomics_fusion_confirmed':False}
    for directory in args.input_dir:
        metadata=json.loads((directory/'analysis_metadata.json').read_text(encoding='utf-8'))
        result['cohorts'].append({'validation':validate_output(directory),'metadata':metadata})
    if args.junit:
        suites=list(ET.parse(args.junit).getroot().iter('testsuite'))
        result['tests']={key:sum(int(s.attrib.get(key,0)) for s in suites) for key in ('tests','failures','errors','skipped')}
        result['tests']['junit_sha256']=sha256(args.junit)
    result['unexecuted_primary_cohorts']=[accession for accession in ['GSE127530','GSE56960','GSE27385','ST001257'] if accession not in [cohort['validation']['accession'] for cohort in result['cohorts']]]
    write_json(args.output,result);print(json.dumps({'output':str(args.output),'cohorts':len(result['cohorts']),'unexecuted':result['unexecuted_primary_cohorts'],'tests':result.get('tests')},indent=2))

if __name__=='__main__':main()
