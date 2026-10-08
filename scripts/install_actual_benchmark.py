#!/usr/bin/env python3
"""Install research-only case 999 into the ACTUAL BDE component driver."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.t.cpp")
s=p.read_text()
s="#include <atomic>\n#include <chrono>\n#include <thread>\n#include <vector>\n"+s
key="switch (test) { case 0:"
assert s.count(key)==1
case=r'''switch (test) {
      case 999: {
        ball::LoggerManagerConfiguration config;
        ball::LoggerManagerScopedGuard guard(config);
        Obj& manager=Obj::singleton();
        // All expected identities are known from allocation and registration.
        ball::Logger *globalDefault=&manager.getLogger();
        ball::FixedSizeRecordBuffer persistentBuffer(32768);
        ball::Logger *persistent=manager.allocateLogger(&persistentBuffer);
        std::atomic<bool> active(false), terminate(false);
        std::thread owner([&](){
            manager.setLogger(persistent);
            active.store(true);
            while(!terminate.load()) std::this_thread::yield();
            manager.setLogger(0);
        });
        while(!active.load()) std::this_thread::yield();

        for (int workers : {1,2,4,8,16}) {
          for (int scenario : {0,1,2,3,4}) {
            // 0 = no custom associations (owner temporarily cleared);
            // 1 = one persistent custom association, workers all default;
            // 2 = half workers custom; 3 = all workers custom;
            // 4 = frequent custom/default toggling in half workers.
            // scenario 0 has a separate manager, because owner is active.
            if (scenario==0) continue;
            for (int repeat=0; repeat<5; ++repeat) {
              std::atomic<int> failures(0), arrived(0);
              std::atomic<bool> go(false);
              std::vector<std::thread> threads;
              for (int k=0; k<workers; ++k) threads.emplace_back([&, k](){
                ball::FixedSizeRecordBuffer ownBuffer(32768);
                ball::Logger *own = 0;
                bool customThread = scenario==3 ||
                    ((scenario==2 || scenario==4) && k%2==0);
                if(customThread) {
                   own=manager.allocateLogger(&ownBuffer);
                   manager.setLogger(own);
                }
                ball::Logger *expected=customThread ? own : globalDefault;
                if(&manager.getLogger()!=expected) failures.fetch_add(1);
                arrived.fetch_add(1);
                while(!go.load()) std::this_thread::yield();
                for (int i=0;i<120000;++i) {
                   if (scenario==4 && customThread && (i%256)==0) {
                      if ((i/256)%2==0) {manager.setLogger(0); expected=globalDefault;}
                      else {manager.setLogger(own);expected=own;}
                   }
                   if (&manager.getLogger()!=expected) failures.fetch_add(1);
                }
                if(own) {
                    manager.setLogger(0);
                    manager.deallocateLogger(own);
                }
              });
              while(arrived.load()!=workers) std::this_thread::yield();
              auto start=std::chrono::steady_clock::now();
              go.store(true);
              for (auto& t:threads) t.join();
              auto end=std::chrono::steady_clock::now();
              ASSERT(0==failures.load());
              std::cout<<"ACTUAL_BDE workers="<<workers
                       <<" scenario="<<scenario<<" repeat="<<repeat
                       <<" mismatches="<<failures.load()
                       <<" ms="<<std::chrono::duration<double,std::milli>(end-start).count()
                       <<std::endl;
            }
          }
        }
        terminate.store(true); owner.join();
        manager.deallocateLogger(persistent);
      } break;
      case 0:'''
s=s.replace(key,case)
p.write_text(s)
print("PASS research benchmark installed; expected identities explicit")
