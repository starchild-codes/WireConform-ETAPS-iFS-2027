// INSTRUMENTATION FIXTURE ONLY. NOT A GENERATED CLIENT; NEVER SCORE AS SDK EVIDENCE.
const payload=JSON.parse(process.argv[2]);
const base=payload.base_url;
if (payload.case_id==='c004' || payload.case_id==='c005') {
  const params=new URLSearchParams();
  for (const v of payload.value) params.append('item',String(v));
  await fetch(`${base}/cases/${payload.case_id}?${params.toString()}`);
} else if (payload.case_id==='c003') {
  // An intentionally incorrect join for a form/explode=false array. Controlled negative fixture.
  await fetch(`${base}/cases/${payload.case_id}?item=${payload.value.join('|')}`);
} else if (payload.case_id==='c001') {
  // Valid scalar positive-control fixture.
  await fetch(`${base}/cases/${payload.case_id}?item=${payload.value}`);
} else {
  process.stderr.write('No instrumentation fixture implemented for '+payload.case_id+'\n');
  process.exit(2);
}
