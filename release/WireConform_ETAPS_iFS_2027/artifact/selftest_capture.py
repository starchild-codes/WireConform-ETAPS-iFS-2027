"""End-to-end harness smoke test WITHOUT running any generated client.
Positive and negative requests are deliberately synthesized using urllib,
so this output may not be reported as evidence of generator conformance.
"""
import json,subprocess,sys,time,urllib.request,socket
from pathlib import Path
from spec_oracle import Case,serialize
from score import main as score_main

root=Path(__file__).resolve().parent.parent
manifest=root/'outputs/corpus/manifest.json'
assert manifest.exists(), 'Run build_corpus.py first'
allcases=json.loads(manifest.read_text())
by_id={c['id']:c for c in allcases}
c1=by_id['c001']
c2=by_id['c002']
out=root/'outputs/selftest_observations.jsonl'
if out.exists():out.unlink()
p=subprocess.Popen([sys.executable,str(root/'artifact/capture_server.py'),str(out)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
try:
 for attempt in range(30):
  try:
   with socket.create_connection(('127.0.0.1',8765),timeout=.2): pass
   break
  except OSError: time.sleep(.12)
 else: raise RuntimeError('Capture service did not become ready')
 url=c1['expected_url']; headers=c1['expected_headers']
 urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765'+url,headers=headers)).close()
 # Deliberate wrong value; must be classified FAIL by scorer.
 bad=c2['expected_url'].replace('azure','wrong')
 assert bad!=c2['expected_url']
 urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765'+bad,headers=c2['expected_headers'])).close()
 dest=root/'outputs/selftest_score.json'
 score_main(manifest,out,dest)
 counts=json.loads(dest.read_text())['summary']['status_counts']
 assert counts=={'PASS':1,'FAIL':1,'NOT_RUN':len(allcases)-2},counts
 print('HARNESS_SMOKE_TEST_PASSED: 1 correct and 1 intentionally incorrect observation classified accurately')
finally:
 p.terminate()
 try:p.wait(timeout=2)
 except subprocess.TimeoutExpired:p.kill()
