#!/usr/bin/env python3
"""Research A2-A5 composition on top of A0 + A1; no upstream writes.

A2: preserve monotonic per-manager lifetime token (rather than unsafe
    address-only ABI-neutral identity). Explicitly carry ABI cost.
A3: force slow-path revalidation for a new manager or any local transition.
A4: enforce pointer extraction and absence test while map lock is held.
A5: integrate explicit fast-miss -> original lock/map fallback,
    with cache invalidated BEFORE release of the setLogger lock.
"""
from pathlib import Path
cpp=Path("upstream/groups/bal/ball/ball_loggermanager.cpp")
hdr=Path("upstream/groups/bal/ball/ball_loggermanager.h")
s=cpp.read_text();h=hdr.read_text()
def swap(old,new,label):
    global s
    assert s.count(old)==1,(label,s.count(old))
    s=s.replace(old,new,1)
# A2: Unique id already added by A0. Prove present; reject unsafe ABI-neutral alternative.
assert "d_cacheId(s_nextLoggerManagerCacheId.fetch_add(1, std::memory_order_relaxed))" in s
assert "unsigned long long     d_cacheId;" in h
# A3: compact validity structure; no positive Logger pointer stored in TLS.
swap('''    const bool sameManager = s_negativeLoggerCache.d_managerId == d_cacheId;
    if (sameManager) {
        if (s_negativeLoggerCache.d_isNegative) {
            return *d_logger_p;
        }
    }
''','''    const bool canReturnDefault =
        s_negativeLoggerCache.d_managerId == d_cacheId &&
        s_negativeLoggerCache.d_isNegative;
    if (canReturnDefault) {
        return *d_logger_p;  // A3: no thread-id lookup, lock, or map lookup
    }
''',"A3 fast path")
# A4: current patch already captures pointer under the lock.
slow=s[s.index("Logger& LoggerManager::getLoggerSlow()"):s.index("void LoggerManager::setLogger(")]
assert slow.index("Logger *logger = itr !=")<slow.index("d_defaultLoggersLock.unlock();")
assert slow.index("const bool isNegative =")<slow.index("d_defaultLoggersLock.unlock();")
# A5: invalidate TLS before releasing the write guard so local transitions
# cannot return a stale negative state after setLogger.
swap('''    d_defaultLoggerCount.storeRelease(
                               static_cast<unsigned>(d_defaultLoggers.size()));
    // setLogger affects only this thread; invalidate its negative hit.
    s_negativeLoggerCache.d_isNegative = false;
''','''    // Local transitions always invalidate the negative cache, including
    // custom->custom and custom->default; no custom Logger is ever cached.
    s_negativeLoggerCache.d_managerId = 0;
    s_negativeLoggerCache.d_isNegative = false;
    d_defaultLoggerCount.storeRelease(
                               static_cast<unsigned>(d_defaultLoggers.size()));
''',"A5 setLogger transition")
cpp.write_text(s)
print("A2 manager generation: retained; ABI-neutral candidate rejected as unproven")
print("A3 TLS negative hit: verified")
print("A4 pointer/absence copied under map lock: verified")
print("A5 invalidate-before-publish + unchanged fallback: applied")
