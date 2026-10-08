#!/usr/bin/env python3
"""A1: guarded fast-path variant on top of applied A0 (research only).

This is a deliberate branch-shape experiment, not a new caching algorithm.
Do not enable the hit unless (manager identity AND known negative) both hold.
"""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.cpp")
s=p.read_text()
old='''    if (s_negativeLoggerCache.d_managerId == d_cacheId
        && s_negativeLoggerCache.d_isNegative) {
        return *d_logger_p;  // negative hit; no shared map lookup
    }
'''
new='''    // A1 guarded path: treat nonmatching manager identity as an explicit
    // invalid cache state, and use the unchanged lock/map fallback.
    const bool sameManager = s_negativeLoggerCache.d_managerId == d_cacheId;
    if (sameManager) {
        if (s_negativeLoggerCache.d_isNegative) {
            return *d_logger_p;
        }
    }
'''
assert s.count(old)==1, "A0 anchor missing or upstream changed"
p.write_text(s.replace(old,new))
print("PASS A1 guarded path applied to real BDE")
