#!/usr/bin/env python3
"""Install case 995: adversarial single-thread actual BDE LoggerManager checks."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.t.cpp")
s=p.read_text()
anchor="switch (test) { case 0:"
assert s.count(anchor)==1
case=r'''switch (test) {
      case 995: {
        // Strictly single-threaded: no worker threads, no concurrency.
        for (int epoch=0;epoch<24;++epoch) {
          ball::LoggerManagerConfiguration config;
          ball::LoggerManagerScopedGuard guard(config);
          Obj& m=Obj::singleton();
          ball::Logger *def=&m.getLogger();
          ball::FixedSizeRecordBuffer b1(32768), b2(32768), b3(32768);
          ball::Logger *a=m.allocateLogger(&b1);
          ball::Logger *b=m.allocateLogger(&b2);
          ball::Logger *c=m.allocateLogger(&b3);
          // Cover cold lookup, warm negative cache, two custom identities,
          // custom->custom, custom->default, and stale-negative revival.
          for(int round=0; round<128; ++round) {
            m.setLogger(0);
            for(int j=0;j<64;++j) ASSERT(&m.getLogger()==def);
            m.setLogger(a);
            for(int j=0;j<64;++j) ASSERT(&m.getLogger()==a);
            m.setLogger(b);
            for(int j=0;j<64;++j) ASSERT(&m.getLogger()==b);
            m.setLogger(0);
            ASSERT(&m.getLogger()==def);
            m.setLogger(c);
            ASSERT(&m.getLogger()==c);
            m.setLogger(0);
          }
          // A removed logger is not a legal return value.
          m.deallocateLogger(a);
          m.deallocateLogger(b);
          m.deallocateLogger(c);
          for(int j=0;j<4096;++j) ASSERT(&m.getLogger()==def);
          std::cout<<"ADVERSARIAL_SINGLE_PASS epoch="<<epoch<<std::endl;
        }
      } break;
      case 0:'''
p.write_text(s.replace(anchor,case,1))
print("Installed actual BDE adversarial single-thread case 995")
