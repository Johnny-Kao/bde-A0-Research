#!/usr/bin/env python3
"""Install a deterministic real-BDE single-thread state-machine case 997."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.t.cpp")
s=p.read_text()
anchor="switch (test) { case 0:"
assert s.count(anchor)==1
case=r'''switch (test) {
      case 997: {
        for (int generation=0;generation<8;++generation) {
          ball::LoggerManagerConfiguration config;
          ball::LoggerManagerScopedGuard scoped(config);
          Obj& m=Obj::singleton();
          ball::Logger *defaultLogger=&m.getLogger();
          ball::FixedSizeRecordBuffer b1(32768),b2(32768);
          ball::Logger *one=m.allocateLogger(&b1);
          ball::Logger *two=m.allocateLogger(&b2);
          unsigned state=123456789u;
          for (int i=0;i<100000;++i) {
            state=state*1664525u+1013904223u;
            unsigned action=(state>>16)%7;
            ball::Logger *expected=defaultLogger;
            if(action==0 || action==3) {m.setLogger(one);expected=one;}
            else if(action==1 || action==4) {m.setLogger(two);expected=two;}
            else m.setLogger(0);
            ASSERT(&m.getLogger()==expected);
            ASSERT(&m.getLogger()==expected);
            ASSERT(&m.getLogger()==expected);
          }
          m.setLogger(0);
          ASSERT(&m.getLogger()==defaultLogger);
          m.deallocateLogger(one);
          m.deallocateLogger(two);
          ASSERT(&m.getLogger()==defaultLogger);
          std::cout<<"SINGLE_THREAD_STATE_MACHINE_PASS generation="
                   <<generation<<std::endl;
        }
      } break;
      case 0:'''
p.write_text(s.replace(anchor,case,1))
print("Installed single-thread state-machine case 997")
