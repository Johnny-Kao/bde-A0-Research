#!/usr/bin/env python3
"""Research-only ABI-neutral variant: global construction epoch + TLS owner pointer.

Lifetime invariant: no concurrent destruction/use of the manager.
Any manager construction invalidates ALL negative TLS entries via epoch bump.
Never store a positive logger pointer. No header/layout changes.
"""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.cpp")
h=Path("upstream/groups/bal/ball/ball_loggermanager.h")
s=p.read_text(); t=h.read_text()
def once(a,b,label):
    global s
    assert s.count(a)==1,(label,s.count(a))
    s=s.replace(a,b,1)
once("std::atomic<unsigned long long> s_nextLoggerManagerCacheId(1);",
     "std::atomic<unsigned long long> s_loggerManagerConstructionEpoch(1);",
     "epoch global")
once("    unsigned long long d_managerId;\n    bool d_isNegative;",
     "    const void *d_manager;\n    unsigned long long d_epoch;\n    bool d_isNegative;",
     "TLS state")
once("thread_local NegativeLoggerCache s_negativeLoggerCache = {0, false};",
     "thread_local NegativeLoggerCache s_negativeLoggerCache = {0, 0, false};",
     "TLS init")
init=", d_cacheId(s_nextLoggerManagerCacheId.fetch_add(1, std::memory_order_relaxed))\n"
assert s.count(init)==2
s=s.replace(init,"")
body="\n{\n    BSLS_ASSERT(d_observer);"
assert s.count(body)==2
s=s.replace(body,
"""\n{\n    // Invalidate all existing per-thread negative entries across address reuse.
    // Manager lifetime must not overlap another thread's use/destruction.
    s_loggerManagerConstructionEpoch.fetch_add(1, std::memory_order_acq_rel);
    BSLS_ASSERT(d_observer);""")
once("""    const bool canReturnDefault =
        s_negativeLoggerCache.d_managerId == d_cacheId &&
        s_negativeLoggerCache.d_isNegative;""",
"""    const unsigned long long epoch =
        s_loggerManagerConstructionEpoch.load(std::memory_order_acquire);
    const bool canReturnDefault =
        s_negativeLoggerCache.d_manager == this &&
        s_negativeLoggerCache.d_epoch == epoch &&
        s_negativeLoggerCache.d_isNegative;""","guard")
once("""    s_negativeLoggerCache.d_managerId = d_cacheId;
    s_negativeLoggerCache.d_isNegative = isNegative;""",
"""    s_negativeLoggerCache.d_manager = this;
    s_negativeLoggerCache.d_epoch = epoch;
    s_negativeLoggerCache.d_isNegative = isNegative;""","cache update")
once("    s_negativeLoggerCache.d_managerId = 0;",
     "    s_negativeLoggerCache.d_manager = 0;\n    s_negativeLoggerCache.d_epoch = 0;",
     "invalidation")
field="""    unsigned long long     d_cacheId;            // A0 research: unique
                                                 // instance identity"""
assert t.count(field)==1
t=t.replace("\n\n"+field,"")
h.write_text(t);p.write_text(s)
assert "d_cacheId" not in s and "d_cacheId" not in t
print("ABI-neutral variant installed: no LoggerManager header field")
