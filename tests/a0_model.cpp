// Research-only C++ model, NOT compiled against Bloomberg BDE.
// Tests whether a TLS negative-cache design can preserve local setLogger semantics
// and produce sufficient perf signal to justify a real BDE integration.
#include <atomic>
#include <cassert>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <map>
#include <mutex>
#include <shared_mutex>
#include <thread>
#include <vector>
#include <algorithm>
struct Model {
  static std::atomic<uint64_t> sequence;
  uint64_t id = sequence.fetch_add(1, std::memory_order_relaxed);
  mutable std::shared_mutex lock;
  std::map<std::thread::id,int> custom;
  std::atomic<unsigned> count{0};
  int fallback=1;
  struct Cache { uint64_t id=0; bool negative=false; };
  static thread_local Cache cache;
  void set(int n) {
    { std::unique_lock<std::shared_mutex> g(lock);
      if(n==0) custom.erase(std::this_thread::get_id());
      else custom[std::this_thread::get_id()]=n;
      count.store(unsigned(custom.size()),std::memory_order_release);
    }
    cache={}; // invalidate when this thread changes association
  }
  int baseline() const {
    if(!count.load(std::memory_order_acquire)) return fallback;
    std::shared_lock<std::shared_mutex> g(lock);
    auto it=custom.find(std::this_thread::get_id());
    return it==custom.end()?fallback:it->second;
  }
  int candidate() const {
    if(!count.load(std::memory_order_acquire)) return fallback;
    if(cache.id==id && cache.negative) return fallback;
    std::shared_lock<std::shared_mutex> g(lock);
    auto it=custom.find(std::this_thread::get_id());
    bool absent=it==custom.end();
    int result=absent?fallback:it->second;
    cache={id,absent};
    return result;
  }
};
std::atomic<uint64_t> Model::sequence{1};
thread_local Model::Cache Model::cache{};
static void correctness() {
  Model a;
  assert(a.baseline()==a.candidate());
  a.set(7);
  assert(a.candidate()==7 && a.baseline()==7);
  a.set(0);
  assert(a.candidate()==1);
  Model b; b.set(8);
  assert(b.candidate()==8);
  assert(a.candidate()==1);
  a.set(9);
  assert(a.candidate()==9);
  a.set(0);
  assert(a.candidate()==1);
  // Allocation at the same storage address: manager identity still differs.
  alignas(Model) unsigned char storage[sizeof(Model)];
  auto* p=new(storage) Model();
  const auto old=p->id;
  p->set(0); assert(p->candidate()==1);
  p->~Model();
  auto* q=new(storage) Model();
  assert(q->id!=old && q->candidate()==1);
  q->~Model();
  // One custom-associated thread, many default threads.
  Model c; std::atomic<bool> ready{false}, done{false};
  std::thread custom([&]{c.set(7);ready.store(true);while(!done.load()) std::this_thread::yield();assert(c.candidate()==7);c.set(0);});
  while(!ready.load()) std::this_thread::yield();
  std::vector<std::thread> threads;
  for(int i=0;i<8;i++) threads.emplace_back([&]{for(int j=0;j<10000;j++)assert(c.baseline()==c.candidate());});
  for(auto& t:threads)t.join();
  done.store(true);custom.join();
  std::cout<<"PASS correctness: set/reset, manager isolation, same-address reuse, 8-thread default lookup\n";
}
static double bench(bool opt,int threads,int iterations){
  Model m;std::atomic<bool> ready{false},done{false};
  std::thread owner([&]{m.set(7);ready=true;while(!done)std::this_thread::yield();m.set(0);});
  while(!ready)std::this_thread::yield();
  std::atomic<uint64_t> checksum{0};
  std::vector<std::thread> v;
  auto begin=std::chrono::steady_clock::now();
  for(int i=0;i<threads;i++)v.emplace_back([&]{
    uint64_t s=0;
    for(int j=0;j<iterations;j++)s+=(opt?m.candidate():m.baseline());
    checksum.fetch_add(s,std::memory_order_relaxed);
  });
  for(auto& t:v)t.join();
  auto end=std::chrono::steady_clock::now();
  done=true;owner.join();
  assert(checksum==uint64_t(threads)*iterations);
  return std::chrono::duration<double,std::milli>(end-begin).count();
}
int main() {
 correctness();
 for(int t:{1,2,4,8}){
   std::vector<double> base,fast;
   for(int i=0;i<5;i++){
     if(i%2){fast.push_back(bench(true,t,120000));base.push_back(bench(false,t,120000));}
     else{base.push_back(bench(false,t,120000));fast.push_back(bench(true,t,120000));}
   }
   std::sort(base.begin(),base.end());std::sort(fast.begin(),fast.end());
   std::cout<<"MODEL_ONLY threads="<<t<<" baseline_ms="<<base[2]
            <<" candidate_ms="<<fast[2]<<" speedup="<<base[2]/fast[2]<<"x\n";
 }
 std::cout<<"Model-only data MUST NOT be represented as actual BDE improvement.\n";
}
