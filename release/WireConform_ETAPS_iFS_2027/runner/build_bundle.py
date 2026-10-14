"""Combine independent OpenAPI probes into a single reproducible SDK workload.

This is an execution optimization; the 117 original per-case documents remain
frozen. Every operation is copied byte-equivalently except its unique operationId.
The proof-of-equivalence check reconstructs each original operation.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def digest(x):
    return hashlib.sha256(x).hexdigest()


def build(manifest_path):
    manifest_path=Path(manifest_path)
    rows=json.loads(manifest_path.read_text(encoding='utf8'))
    operations={}
    ledger=[]
    for row in rows:
        src=manifest_path.parent/row['spec_file']
        data=json.loads(src.read_text(encoding='utf8'))
        assert data['openapi']=='3.1.1'
        assert data['servers']==[{'url':'http://127.0.0.1:8765'}]
        assert len(data['paths'])==1
        path, methods=next(iter(data['paths'].items()))
        assert list(methods)==['get']
        assert path not in operations
        operation=copy.deepcopy(methods['get'])
        assert operation.pop('operationId')=='probe'
        cid=row['id']
        assert path.startswith(f'/cases/{cid}')
        operation['operationId']='probe'+cid.upper()
        operations[path]={'get':operation}
        ledger.append({'case_id':cid,'path':path,'operation_id':operation['operationId'],
                       'source_sha256':digest(src.read_bytes())})
    assert len(operations)==len(rows)==117
    bundled={'openapi':'3.1.1',
             'info':{'title':'WireConform merged benchmark', 'version':'0.4.0'},
             'servers':[{'url':'http://127.0.0.1:8765'}],
             'paths':operations}
    # Every individual operation can be reconstructed exactly, including its
    # parameter specification and response definition.
    for row in rows:
        original=json.loads((manifest_path.parent/row['spec_file']).read_text())
        p=ledger[[x['case_id'] for x in ledger].index(row['id'])]['path']
        original_op=original['paths'][p]['get']
        reconstructed=copy.deepcopy(bundled['paths'][p]['get'])
        reconstructed['operationId']='probe'
        assert reconstructed==original_op, f'operation drift: {row["id"]}'
    return bundled,ledger


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',default='outputs/corpus/manifest.json')
    ap.add_argument('--output',default='outputs/bundle/all_117.json')
    ap.add_argument('--ledger',default='outputs/bundle/sources.json')
    args=ap.parse_args()
    root=Path(__file__).resolve().parents[1]
    spec,ledger=build(root/args.manifest)
    out=root/args.output;out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(spec,indent=2)+'\n')
    meta={'source_case_count':len(ledger),'bundle_sha256':digest(out.read_bytes()),'cases':ledger}
    provenance=root/args.ledger;provenance.parent.mkdir(parents=True,exist_ok=True)
    provenance.write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps({'operations':len(ledger),'bundle_sha256':meta['bundle_sha256'],'out':str(out)},indent=2))

if __name__=='__main__':main()
