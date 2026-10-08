#!/usr/bin/env python3
"""Research-only benchmark case 999 for actual ball_loggermanager.t.cpp."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.t.cpp")
s=p.read_text()
s="#include <atomic>\n#include <chrono>\n#include <thread>\n#include <vector>\n"+s
key="switch (test) { case 0:"
assert s.count(key)==1
case=r'''switch (test) {
      case 999: {
        // Model-free benchmark: exercise real LoggerManager::getLogger().
        ball::LoggerManagerConfiguration config;
        ball::LoggerManagerScopedGuard guard(config);
        Obj& manager=Obj::singleton();
        ball::FixedSizeRecordBuffer customBuffer(32768);
        ball::Logger *custom=manager.allocateLogger(&customBuffer);
        std::atomic<bool> ready(false), done(false);
        std::thread owner([&](){
          manager.setLogger(custom);
          ready.store(true);
          while (!done.load()) std::this_thread::yield();
          manager.setLogger(0);
        });
        while (!ready.load()) std::this_thread::yield();
        for (int workers : {1,2,4,8}) {
          for (int repeat=0; repeat<5; ++repeat) {
            std::vector<std::thread> threads;
            std::atomic<int> failures(0);
            auto t0=std::chrono::steady_clock::now();
            for (int k=0; k<workers; ++k)
              threads.emplace_back([&](){
                const ball::Logger *expected=&manager.getLogger();
                for (int i=0; i<200000; ++i)
                  if (&manager.getLogger()!=expected) failures.fetch_add(1);
              });
            for(auto& t:threads)t.join();
            auto t1=std::chrono::steady_clock::now();
            ASSERT(0 == failures.load());
            std::cout<<"ACTUAL_BDE workers="<<workers
                     <<" repeat="<<repeat<<" ms="
                     <<std::chrono::duration<double,std::milli>(t1-t0).count()
                     <<std::endl;
          }
        }
        done.store(true);
        owner.join();
        manager.deallocateLogger(custom);
      } break;
      case 0:'''
s=s.replace(key,case)
p.write_text(s)
print("PASS benchmark case installed into actual BDE test driver")
