#!/usr/bin/env python3
"""T0: inspect the *real* upstream BDE implementation; no patch or perf claim."""
import pathlib
import re

p = pathlib.Path("upstream/groups/bal/ball/ball_loggermanager.cpp")
h = pathlib.Path("upstream/groups/bal/ball/ball_loggermanager.h")
assert p.exists() and h.exists(), "BDE sources were not checked out"
source = p.read_text()
header = h.read_text()
def body(name, next_name):
    m = re.search(r"\bLoggerManager::"+name+r"\s*\([^)]*\)\s*\{", source)
    assert m, name + " not found"
    n = source.find(next_name, m.end())
    return source[m.end():n if n >= 0 else m.end()+1500]
slow = body("getLoggerSlow", "void LoggerManager::setLogger")
setter = body("setLogger", "// Category Management")
deleter = body("deallocateLogger", "Logger& LoggerManager::getLoggerSlow")
checks = {
 "slow_path_read_lock": "d_defaultLoggersLock.lockRead()" in slow,
 "slow_path_map_lookup": "d_defaultLoggers.find(" in slow,
 "slow_path_unlock_before_iterator_usage": slow.find("unlock()") < slow.find("itr != d_defaultLoggers.end()"),
 "setter_map_mutation": "d_defaultLoggers.erase(id)" in setter and "d_defaultLoggers[id] = logger" in setter,
 "deallocator_removes_map_entries": "d_defaultLoggers.erase(itr++)" in deleter,
 "manager_reinitialization_documented": "reinitialized" in header,
}
for name, passed in checks.items():
    print(("PASS" if passed else "FAIL") + " " + name)
assert all(checks.values()), "Upstream changed; re-evaluate A0 before proceeding"
print("T0 SOURCE CONTRACT PASS; NOT a benchmark, correctness proof, or A0 implementation test")
