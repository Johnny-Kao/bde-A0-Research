#!/usr/bin/env python3
"""Add real BDE zero-custom regression to component driver (case 996)."""
from pathlib import Path
p=Path("upstream/groups/bal/ball/ball_loggermanager.t.cpp")
s=p.read_text()
assert s.count("switch (test) { case 0:")==1
s="#include <atomic>\n#include <chrono>\n#include <thread>\n#include <vector>\n"+s
case=r'''switch (test) {
      case 996: {
        ball::LoggerManagerConfiguration config;
        ball::LoggerManagerScopedGuard guard(config);
        Obj& m=Obj::singleton();
        ball::Logger *expected=&m.getLogger();
        for(int workers:{1,2,4,8,16}) {
          for(int rep=0;rep<5;++rep) {
            std::atomic<int> failures(0), arrived(0);
            std::atomic<bool> go(false);
            std::vector<std::thread> threads;
            for(int k=0;k<workers;++k) threads.emplace_back([&](){
              if(&m.getLogger()!=expected) failures.fetch_add(1);
              arrived.fetch_add(1);
              while(!go.load()) std::this_thread::yield();
              for(int j=0;j<120000;++j)
                if(&m.getLogger()!=expected) failures.fetch_add(1);
            });
            while(arrived.load()!=workers) std::this_thread::yield();
            auto start=std::chrono::steady_clock::now();
            go.store(true);
            for(auto& t:threads)t.join();
            auto end=std::chrono::steady_clock::now();
            ASSERT(failures.load()==0);
            std::cout<<"ZERO_CUSTOM workers="<<workers<<" repeat="<<rep
                     <<" mismatches="<<failures.load()<<" ms="
                     <<std::chrono::duration<double,std::milli>(end-start).count()
                     <<std::endl;
          }
        }
      } break;
      case 0:'''
p.write_text(s.replace("switch (test) { case 0:",case,1))
print("Installed actual BDE zero-custom control case 996")
