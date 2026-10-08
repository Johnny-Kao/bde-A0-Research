#!/usr/bin/env python3
"""Research-only full route accounting; separate from performance binaries."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.cpp")
h=Path("upstream/groups/bal/ball/ball_loggermanager.h")
s=p.read_text(); t=h.read_text()
assert 'ROUTE_COUNTS negative=' in s
anchor="std::atomic<unsigned long long> s_routeSlow(0), s_routeNegative(0),"
assert s.count(anchor)==1
s=s.replace(anchor,"std::atomic<unsigned long long> s_routeGlobal(0);\n"+anchor,1)
# Add declaration in same BDE namespace before LoggerManager inline definition.
header_anchor="inline\nLogger& LoggerManager::getLogger()"
assert t.count(header_anchor)==1
t=t.replace(header_anchor,"void researchCountGlobalDefaultLogger();\n\n"+header_anchor,1)
target='    return *d_logger_p;\n}\n\n// ACCESSORS'
assert t.count(target)==1
t=t.replace(target,'    researchCountGlobalDefaultLogger();\n    return *d_logger_p;\n}\n\n// ACCESSORS',1)
# Defined outside unnamed namespace in Bloomberg BDE namespace, before getLoggerSlow.
fn="Logger& LoggerManager::getLoggerSlow()"
assert s.count(fn)==1
s=s.replace(fn,'''void researchCountGlobalDefaultLogger()
{
    s_routeGlobal.fetch_add(1, std::memory_order_relaxed);
}

'''+fn,1)
needle='std::fprintf(stderr, "ROUTE_COUNTS negative=%llu slow=%llu custom=%llu default=%llu\\n",'
assert s.count(needle)==1
s=s.replace(needle,'std::fprintf(stderr, "ROUTE_COUNTS global=%llu negative=%llu slow=%llu custom=%llu default=%llu\\n",',1)
needle='            (unsigned long long)s_routeNegative.load(),'
assert s.count(needle)==1
s=s.replace(needle,'            (unsigned long long)s_routeGlobal.load(),\n'+needle,1)
h.write_text(t);p.write_text(s)
print("FULL_ROUTE_ACCOUNTING_INSTALLED")
