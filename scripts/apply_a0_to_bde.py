#!/usr/bin/env python3
"""Apply A0 experimental source patch to a clean checkout of bloomberg/bde.
Research only. Generated diff is not upstream-ready, porting review required.
"""
from pathlib import Path
root=Path("upstream/groups/bal/ball")
cpp=root/"ball_loggermanager.cpp"
hdr=root/"ball_loggermanager.h"
s=cpp.read_text(); h=hdr.read_text()
def replace_once(t,a,b):
    if t.count(a)!=1: raise RuntimeError(f"expected one anchor, found {t.count(a)}: {a[:95]}")
    return t.replace(a,b,1)
s=replace_once(s,"#include <bsl_cstddef.h>", "#include <atomic>\n#include <bsl_cstddef.h>")
anchor='namespace {\n\n                    // =========================='
s=replace_once(s,anchor,'''namespace {

// A0 research-only cache: never cache a custom Logger pointer.
// Monotonically unique per-manager identity prevents same-address ABA.
std::atomic<unsigned long long> s_nextLoggerManagerCacheId(1);
struct NegativeLoggerCache {
    unsigned long long d_managerId;
    bool d_isNegative;
};
thread_local NegativeLoggerCache s_negativeLoggerCache = {0, false};

                    // ==========================''')
# Both constructor variants use the same initialization item.
anchor=', d_defaultLoggerCount(0)\n'
assert s.count(anchor)==2, f"unexpected constructor count {s.count(anchor)}"
s=s.replace(anchor,anchor+', d_cacheId(s_nextLoggerManagerCacheId.fetch_add(1, std::memory_order_relaxed))\n')
original='''    // TBD: optimize it using thread local storage

    d_defaultLoggersLock.lockRead();
    bsl::map<void *, Logger *>::iterator itr =
            d_defaultLoggers.find((void *)bslmt::ThreadUtil::selfIdAsUint64());
    d_defaultLoggersLock.unlock();
    return itr != d_defaultLoggers.end() ? *(itr->second) : *d_logger_p;'''
patched='''    if (s_negativeLoggerCache.d_managerId == d_cacheId
        && s_negativeLoggerCache.d_isNegative) {
        return *d_logger_p;  // negative hit; no shared map lookup
    }

    d_defaultLoggersLock.lockRead();
    bsl::map<void *, Logger *>::iterator itr =
            d_defaultLoggers.find((void *)bslmt::ThreadUtil::selfIdAsUint64());
    Logger *logger = itr != d_defaultLoggers.end() ? itr->second : d_logger_p;
    const bool isNegative = itr == d_defaultLoggers.end();
    d_defaultLoggersLock.unlock();
    // Do not retain iterator or custom Logger pointer beyond unlock.
    s_negativeLoggerCache.d_managerId = d_cacheId;
    s_negativeLoggerCache.d_isNegative = isNegative;
    return *logger;'''
s=replace_once(s,original,patched)
needle='''    d_defaultLoggerCount.storeRelease(
                               static_cast<unsigned>(d_defaultLoggers.size()));
}

                             // Category Management'''
replacement='''    d_defaultLoggerCount.storeRelease(
                               static_cast<unsigned>(d_defaultLoggers.size()));
    // setLogger affects only this thread; invalidate its negative hit.
    s_negativeLoggerCache.d_isNegative = false;
}

                             // Category Management'''
s=replace_once(s,needle,replacement)
# a unique 64-bit identity field; no ABI claims, this is research.
needle='''    bsls::AtomicUint       d_defaultLoggerCount; // number of thread-specific
                                                 // default loggers'''
h=replace_once(h,needle,needle+'''

    unsigned long long     d_cacheId;            // A0 research: unique
                                                 // instance identity''')
cpp.write_text(s);hdr.write_text(h)
print("PASS actual BDE A0 experimental patch applied")
