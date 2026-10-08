#!/usr/bin/env python3
"""Compare paired real-BDE measurements; fail on identity mismatch/missing strata."""
from pathlib import Path
import re,statistics,sys,json
root=Path(sys.argv[1])
pat=re.compile(r"(ZERO_CUSTOM|ACTUAL_BDE) workers=(\d+)(?: scenario=(\d+))? repeat=(\d+) mismatches=(\d+) ms=([0-9.]+)")
data={}
for label in ("baseline","candidate"):
  for kind in ("zero","mixed"):
    p=root/f"{label}-{kind}.txt"
    matches=pat.findall(p.read_text())
    assert matches,(str(p),"no measurements")
    for tag,workers,scenario,rep,mismatches,ms in matches:
      assert int(mismatches)==0,(label,workers,scenario,rep,mismatches)
      key=(tag,int(workers),int(scenario) if scenario else 0)
      data.setdefault((label,key),[]).append(float(ms))
summary={}
for label,key in data:
  assert len(data[(label,key)])==5,(label,key,"requires five samples")
for key in {k for label,k in data}:
  assert ("baseline",key) in data and ("candidate",key) in data,key
  a=statistics.median(data["baseline",key])
  b=statistics.median(data["candidate",key])
  summary[str(key)]={"baseline_ms":a,"candidate_ms":b,"speedup":a/b}
  print(f"PAIR {key} baseline_ms={a:.6g} candidate_ms={b:.6g} speedup={a/b:.3f}")
(root/"paired-summary.json").write_text(json.dumps(summary,indent=2))
print("PAIRED_MATRIX_PASS rows=",len(summary))
