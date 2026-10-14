"""Freeze generator-specific mismatch selections after normative encoding review."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
decisions=json.loads((ROOT/'evidence/reviews/encoding_adjudication.json').read_text())['decisions']
for generator in ('openapi-generator','orval','hey-api'):
    scores=json.loads((ROOT/'experiments/bundle'/generator/'full'/'scored.json').read_text())['cases']
    selected=[]
    for row in scores:
        status=row['status']
        if status=='ENCODING_REVIEW':
            status=decisions[generator][row['case_id']]
        if status=='FAIL':
            selected.append(row['case_id'])
    out=ROOT/'evidence'/'reviews'/f'{generator}_mismatch_selection.json'
    out.write_text(json.dumps({'selection_policy':'all full-study wire mismatches after frozen encoding adjudication',
                               'case_ids':selected},indent=2)+'\n')
    print(generator,len(selected),out)
