#!/usr/bin/env python3
"""Research-only route accounting: count slow-path entry, negative hits and map outcomes.
Use counts ONLY; never benchmark instrumented binaries for performance claims.
"""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.cpp")
s=p.read_text()
marker="std::atomic<unsigned long long> s_loggerManagerConstructionEpoch(1);"
assert s.count(marker)==1
s=s.replace(marker,marker+'''
std::atomic<unsigned long long> s_routeSlow(0), s_routeNegative(0),
    s_routeCustom(0), s_routeDefault(0);''',1)
key="        return *d_logger_p;  // A3: no thread-id lookup, lock, or map lookup"
assert s.count(key)==1
s=s.replace(key,"        s_routeNegative.fetch_add(1, std::memory_order_relaxed);\n"+key)
key="    d_defaultLoggersLock.lockRead();"
start=s.index("Logger& LoggerManager::getLoggerSlow()")
pos=s.index(key,start)
s=s[:pos]+"    s_routeSlow.fetch_add(1, std::memory_order_relaxed);\n"+s[pos:]
key="    const bool isNegative = itr == d_defaultLoggers.end();"
assert s.count(key)==1
s=s.replace(key,key+'''
    if (isNegative) s_routeDefault.fetch_add(1, std::memory_order_relaxed);
    else s_routeCustom.fetch_add(1, std::memory_order_relaxed);''')
# Print counters after process exit via a local destructor; test-only instrumentation.
anchor="std::atomic<unsigned long long> s_routeSlow(0), s_routeNegative(0),"
assert s.count(anchor)==1
s=s.replace(anchor,'''struct RouteReport {
    ~RouteReport() {
        std::fprintf(stderr, "ROUTE_COUNTS negative=%llu slow=%llu custom=%llu default=%llu\\n",
            (unsigned long long)s_routeNegative.load(),
            (unsigned long long)s_routeSlow.load(),
            (unsigned long long)s_routeCustom.load(),
            (unsigned long long)s_routeDefault.load());
    }
};
'''+anchor) if False else s
# Explicit report method without modifying public headers: append reporting via atexit.
# The test run emits route totals when each case finishes via C++ static destructor.
prefix="#include <cstdio>\n"
s=prefix+s
a="std::atomic<unsigned long long> s_routeSlow(0), s_routeNegative(0),\n    s_routeCustom(0), s_routeDefault(0);"
assert a in s
s=s.replace(a,a+'''
struct RouteReport {
    ~RouteReport() {
        std::fprintf(stderr, "ROUTE_COUNTS negative=%llu slow=%llu custom=%llu default=%llu\\n",
            (unsigned long long)s_routeNegative.load(),
            (unsigned long long)s_routeSlow.load(),
            (unsigned long long)s_routeCustom.load(),
            (unsigned long long)s_routeDefault.load());
    }
} s_routeReport;''',1)
p.write_text(s)
print("ROUTE_INSTRUMENTATION_INSTALLED")
