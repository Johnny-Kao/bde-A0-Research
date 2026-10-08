#!/usr/bin/env python3
"""Install actual BDE controlled-concurrency correctness case 994 (Research only)."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.t.cpp")
s=p.read_text()
key="switch (test) { case 0:"
assert s.count(key)==1
s="#include <atomic>\n#include <thread>\n#include <vector>\n"+s
case=r'''switch (test) {
      case 994: {
        for (int generation=0; generation<3; ++generation) {
          ball::LoggerManagerConfiguration config;
          ball::LoggerManagerScopedGuard guard(config);
          Obj& manager=Obj::singleton();
          ball::Logger *globalDefault=&manager.getLogger();
          // Persistent custom mapping forces the shared slow branch for
          // workers without a custom logger; owner never deallocates it
          // until all workers are joined.
          ball::FixedSizeRecordBuffer ownerBuffer(32768);
          ball::Logger *ownerLogger=manager.allocateLogger(&ownerBuffer);
          std::atomic<bool> ownerReady(false), ownerStop(false);
          std::thread owner([&]{
            manager.setLogger(ownerLogger);
            ownerReady.store(true);
            while(!ownerStop.load()) std::this_thread::yield();
            manager.setLogger(0);
          });
          while(!ownerReady.load()) std::this_thread::yield();

          for (int workers : {2,8,32,64}) {
            for (int scenario : {0,1,2}) {
              // 0: workers all default with a persistent foreign custom;
              // 1: half custom; 2: frequent local custom/default transitions.
              std::atomic<int> errors(0), ready(0);
              std::atomic<bool> go(false);
              std::vector<std::thread> threads;
              for(int k=0;k<workers;++k) threads.emplace_back([&, k]{
                ball::FixedSizeRecordBuffer ownBuffer(32768);
                ball::Logger *own=0;
                const bool useCustom=(scenario!=0 && k%2==0);
                if(useCustom) own=manager.allocateLogger(&ownBuffer);
                ball::Logger *expected=globalDefault;
                ready.fetch_add(1);
                while(!go.load()) std::this_thread::yield();
                for(int i=0;i<4000;++i) {
                  if(useCustom && (i%16==0)) {
                    if ((i/16)%2==0) {
                      manager.setLogger(own);
                      expected=own;
                    } else {
                      manager.setLogger(0);
                      expected=globalDefault;
                    }
                  }
                  if (&manager.getLogger()!=expected) errors.fetch_add(1);
                }
                manager.setLogger(0);
                if(&manager.getLogger()!=globalDefault) errors.fetch_add(1);
                if(own) manager.deallocateLogger(own);
              });
              while(ready.load()!=workers) std::this_thread::yield();
              go.store(true);
              for(auto& t:threads) t.join();
              ASSERT(errors.load()==0);
              std::cout<<"CONCURRENT_CORRECT generation="<<generation
                       <<" workers="<<workers<<" scenario="<<scenario
                       <<" errors="<<errors.load()<<std::endl;
            }
          }
          ownerStop.store(true);
          owner.join();
          manager.deallocateLogger(ownerLogger);
          ASSERT(&manager.getLogger()==globalDefault);
        }
      } break;
      case 0:'''
p.write_text(s.replace(key,case,1))
print("Installed real BDE controlled concurrency case 994")
