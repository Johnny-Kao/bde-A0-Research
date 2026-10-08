#!/usr/bin/env python3
"""Install BDE research-only single-thread LoggerManager lifecycle smoke."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.t.cpp")
s=p.read_text()
anchor="switch (test) { case 0:"
assert s.count(anchor)==1
fragment=r'''switch (test) {
      case 998: {
        for (int generation=0; generation<3; ++generation) {
          ball::LoggerManagerConfiguration config;
          ball::LoggerManagerScopedGuard guard(config);
          Obj& m=Obj::singleton();
          ball::Logger *def=&m.getLogger();
          ASSERT(&m.getLogger()==def);
          ball::FixedSizeRecordBuffer b(32768);
          ball::Logger *custom=m.allocateLogger(&b);
          m.setLogger(custom);
          ASSERT(&m.getLogger()==custom);
          for (int i=0; i<50000; ++i) ASSERT(&m.getLogger()==custom);
          m.setLogger(0);
          ASSERT(&m.getLogger()==def);
          for (int i=0; i<50000; ++i) ASSERT(&m.getLogger()==def);
          m.deallocateLogger(custom);
          ASSERT(&m.getLogger()==def);
          std::cout<<"SINGLE_THREAD_PASS generation="<<generation<<std::endl;
        }
      } break;
      case 0:'''
p.write_text(s.replace(anchor,fragment,1))
print("Installed single-thread-only case 998")
