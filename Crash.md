-------------------------------------
Translated Report (Full Report Below)
-------------------------------------
Process:             Electron [28699]
Path:                /Applications/Visual Studio Code.app/Contents/MacOS/Electron
Identifier:          com.microsoft.VSCode
Version:             1.103.1 (1.103.1)
Code Type:           ARM-64 (Native)
Role:                Foreground
Parent Process:      launchd [1]
Coalition:           com.microsoft.VSCode [13141]
User ID:             501

Date/Time:           2025-08-16 10:03:47.4153 +0100
Launch Time:         2025-08-16 00:35:23.1608 +0100
Hardware Model:      Mac16,13
OS Version:          macOS 26.0 (25A5338b)
Release Type:        User

Crash Reporter Key:  4E207357-19A3-A70F-DAD5-7940E32325FE
Incident Identifier: 47803C92-8E56-4CD9-8759-1C7074C63E5D

Sleep/Wake UUID:       48BC6E61-0466-445A-8B83-8DC7D53E3F2C

Time Awake Since Boot: 260000 seconds
Time Since Wake:       18519 seconds

System Integrity Protection: enabled

Triggered by Thread: 0  CrBrowserMain

Exception Type:    EXC_BREAKPOINT (SIGTRAP)
Exception Codes:   0x0000000000000001, 0x000000011e3277cc

Termination Reason:  Namespace SIGNAL, Code 5, Trace/BPT trap: 5
Terminating Process: exc handler [28699]


Thread 0 Crashed:: CrBrowserMain
0   Electron Framework            	       0x11e3277cc ares_llist_node_first + 3553388
1   Electron Framework            	       0x11e3277cc ares_llist_node_first + 3553388
2   Electron Framework            	       0x11e3277e4 ares_llist_node_first + 3553412
3   Electron Framework            	       0x11e327800 ares_llist_node_first + 3553440
4   Electron Framework            	       0x11bdda0f4 node::sqlite::UserDefinedFunction::xDestroy(void*) + 27600
5   Electron Framework            	       0x11cbcf2f0 v8::PropertyDescriptor::set() const + 4297956
6   Electron Framework            	       0x11cbcf284 v8::PropertyDescriptor::set() const + 4297848
7   Electron Framework            	       0x1198f3270 v8::internal::compiler::CompilationDependencies::Commit(v8::internal::Handle<v8::internal::Code>) + 12724
8   Electron Framework            	       0x11949db98 node::Blob::GetTransferMode() const + 29476
9   Electron Framework            	       0x1194a36cc node::Blob::GetTransferMode() const + 52824
10  Electron Framework            	       0x11a0eb574 v8::String::NewFromUtf8(v8::Isolate*, char const*, v8::NewStringType, int) + 392
11  Electron Framework            	       0x11a0eb45c v8::String::NewFromUtf8(v8::Isolate*, char const*, v8::NewStringType, int) + 112
12  Electron Framework            	       0x11c09d610 node::StringBytes::Encode(v8::Isolate*, char const*, unsigned long, node::encoding, v8::Local<v8::Value>*) + 252
13  Electron Framework            	       0x11bf2b7c4 node::Buffer::RegisterExternalReferences(node::ExternalReferenceRegistry*) + 28512
14  ???                           	       0x157e103ac ???
15  ???                           	       0x1501753e8 ???
16  ???                           	       0x150389afc ???
17  ???                           	       0x1503a6414 ???
18  ???                           	       0x150250854 ???
19  ???                           	       0x1503a5a98 ???
20  ???                           	       0x157e0b228 ???
21  ???                           	       0x157e0ae74 ???
22  Electron Framework            	       0x11964e308 v8::Function::Call(v8::Isolate*, v8::Local<v8::Context>, v8::Local<v8::Value>, int, v8::Local<v8::Value>*) + 3576
23  Electron Framework            	       0x11964d6a4 v8::Function::Call(v8::Isolate*, v8::Local<v8::Context>, v8::Local<v8::Value>, int, v8::Local<v8::Value>*) + 404
24  Electron Framework            	       0x11be79448 node::InternalMakeCallback(node::Environment*, v8::Local<v8::Object>, v8::Local<v8::Object>, v8::Local<v8::Function>, int, v8::Local<v8::Value>*, node::async_context, v8::Local<v8::Value>) + 512
25  Electron Framework            	       0x11be79820 node::InternalMakeCallback(v8::Isolate*, v8::Local<v8::Object>, v8::Local<v8::Function>, int, v8::Local<v8::Value>*, node::async_context, v8::Local<v8::Value>) + 304
26  Electron Framework            	       0x11bdd4abc node::sqlite::UserDefinedFunction::xDestroy(void*) + 5528
27  Electron Framework            	       0x11bd2ca48 node::AsyncWrap::~AsyncWrap() + 541412
28  Electron Framework            	       0x11bd2c96c node::AsyncWrap::~AsyncWrap() + 541192
29  Electron Framework            	       0x11a04ead8 v8::internal::ThreadIsolation::RegisterJitPage(unsigned long, unsigned long) + 53484
30  Electron Framework            	       0x119581788 temporal_rs_PlainTime_second + 1244
31  Electron Framework            	       0x119580da8 v8::HandleScope::~HandleScope() + 22132
32  Electron Framework            	       0x11bafab64 v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef) + 463296
33  Electron Framework            	       0x1197abd78 v8::ExternalMemoryAccounter::Increase(v8::Isolate*, unsigned long) + 58696
34  Electron Framework            	       0x11bafa8b8 v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef) + 462612
35  CoreFoundation                	       0x187561ad8 __CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__ + 28
36  CoreFoundation                	       0x187561a6c __CFRunLoopDoSource0 + 172
37  CoreFoundation                	       0x1875617d8 __CFRunLoopDoSources0 + 232
38  CoreFoundation                	       0x187560468 __CFRunLoopRun + 820
39  CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
40  HIToolbox                     	       0x193f39730 RunCurrentEventLoopInMode + 316
41  HIToolbox                     	       0x193f3c9b8 ReceiveNextEventCommon + 464
42  HIToolbox                     	       0x1940c61dc _BlockUntilNextEventMatchingListInMode + 48
43  AppKit                        	       0x18be2d2c4 _DPSBlockUntilNextEventMatchingListInMode + 236
44  AppKit                        	       0x18b946f2c _DPSNextEvent + 588
45  AppKit                        	       0x18c392584 -[NSApplication(NSEventRouting) _nextEventMatchingEventMask:untilDate:inMode:dequeue:] + 688
46  AppKit                        	       0x18c392290 -[NSApplication(NSEventRouting) nextEventMatchingMask:untilDate:inMode:dequeue:] + 72
47  AppKit                        	       0x18b93f770 -[NSApplication run] + 368
48  Electron Framework            	       0x11b0a5cdc v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 11208
49  Electron Framework            	       0x11b0a5af4 v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 10720
50  Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
51  Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
52  Electron Framework            	       0x11b297718 node::PrincipalRealm::inspector_enable_async_hooks() const + 85928
53  Electron Framework            	       0x11b297668 node::PrincipalRealm::inspector_enable_async_hooks() const + 85752
54  Electron Framework            	       0x11b2e5e10 v8::Message::GetLineNumber(v8::Local<v8::Context>) const + 22864
55  Electron Framework            	       0x11b2e5d18 v8::Message::GetLineNumber(v8::Local<v8::Context>) const + 22616
56  Electron Framework            	       0x11ae53ce0 v8::internal::ThreadIsolation::JitPageReference::Shrink(v8::internal::ThreadIsolation::JitPage*) + 58156
57  Electron Framework            	       0x11ae50630 v8::internal::ThreadIsolation::JitPageReference::Shrink(v8::internal::ThreadIsolation::JitPage*) + 44156
58  Electron Framework            	       0x11b1a0078 rust_png$cxxbridge1$Reader$get_trns_chunk + 22836
59  Electron Framework            	       0x11b19f99c rust_png$cxxbridge1$Reader$get_trns_chunk + 21080
60  Electron Framework            	       0x11bc5d544 ElectronMain + 124
61  dyld                          	       0x187105924 start + 6400

Thread 1:: com.apple.NSEventThread
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   CoreFoundation                	       0x187561c80 __CFRunLoopServiceMachPort + 160
5   CoreFoundation                	       0x1875605d8 __CFRunLoopRun + 1188
6   CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
7   AppKit                        	       0x18b9d6a48 _NSEventThread + 184
8   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
9   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 2:: ThreadPoolServiceThread
0   libsystem_kernel.dylib        	       0x18748bb84 kevent64 + 8
1   Electron Framework            	       0x11a81fa64 cxxbridge1$box$rust_png$Reader$drop + 191108
2   Electron Framework            	       0x11a81f010 cxxbridge1$box$rust_png$Reader$drop + 188464
3   Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
4   Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
5   Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
6   Electron Framework            	       0x11baf7368 v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef) + 448964
7   Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
8   Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
9   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
10  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 3:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 4:: ThreadPoolBackgroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f59a4 uv_get_osfhandle + 76472
9   Electron Framework            	       0x1196f587c uv_get_osfhandle + 76176
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 5:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 6:: Chrome_IOThread
0   libsystem_kernel.dylib        	       0x18748bb84 kevent64 + 8
1   Electron Framework            	       0x11a81fa64 cxxbridge1$box$rust_png$Reader$drop + 191108
2   Electron Framework            	       0x11a81f010 cxxbridge1$box$rust_png$Reader$drop + 188464
3   Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
4   Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
5   Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
6   Electron Framework            	       0x11b23fb78 v8::Message::Get() const + 20328
7   Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
8   Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
9   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
10  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 7:: MemoryInfra
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x11a0504f8 v8::internal::ThreadIsolation::RegisterJitPage(unsigned long, unsigned long) + 60172
7   Electron Framework            	       0x11baf0cb8 v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef) + 422676
8   Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
9   Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
10  Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
11  Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
12  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
13  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
14  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 8:
0   libsystem_kernel.dylib        	       0x187485f30 kevent + 8
1   Electron Framework            	       0x11bc5cff8 uv__io_poll + 1840
2   Electron Framework            	       0x11bc4b010 uv_run + 376
3   Electron Framework            	       0x11bfd9af0 node::WorkerThreadsTaskRunner::DelayedTaskScheduler::Start()::'lambda'(void*)::__invoke(void*) + 112
4   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
5   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 9:
0   Electron Framework            	       0x1195b6840 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 13760
1   Electron Framework            	       0x1195b683c v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 13756
2   Electron Framework            	       0x1195b63c8 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 12616
3   Electron Framework            	       0x1195b61c8 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 12104
4   Electron Framework            	       0x11ef35c74 temporal_rs_PlainDate_iso_month + 9536808
5   Electron Framework            	       0x11bfd7768 node::WorkerThreadsTaskRunner::WorkerThreadsTaskRunner(int, node::PlatformDebugLogLevel) + 1388
6   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
7   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 10:
0   Electron Framework            	       0x1195b78d4 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 18004
1   Electron Framework            	       0x1195b6878 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 13816
2   Electron Framework            	       0x1195b63c8 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 12616
3   Electron Framework            	       0x1195b6104 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 11908
4   Electron Framework            	       0x11ef35c74 temporal_rs_PlainDate_iso_month + 9536808
5   Electron Framework            	       0x11bfd7768 node::WorkerThreadsTaskRunner::WorkerThreadsTaskRunner(int, node::PlatformDebugLogLevel) + 1388
6   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
7   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 11:
0   Electron Framework            	       0x1195b7908 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 18056
1   Electron Framework            	       0x1195b6878 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 13816
2   Electron Framework            	       0x1195b63c8 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 12616
3   Electron Framework            	       0x1195b6198 v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const + 12056
4   Electron Framework            	       0x11ef35c74 temporal_rs_PlainDate_iso_month + 9536808
5   Electron Framework            	       0x11bfd7768 node::WorkerThreadsTaskRunner::WorkerThreadsTaskRunner(int, node::PlatformDebugLogLevel) + 1388
6   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
7   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 12:
0   libsystem_kernel.dylib        	       0x18747fbb0 semaphore_wait_trap + 8
1   Electron Framework            	       0x11bc57d78 uv_sem_wait + 24
2   Electron Framework            	       0x11c1361d0 node::inspector::Agent::GetWsUrl() const + 52
3   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 13:: libuv-worker
0   libsystem_kernel.dylib        	       0x1874834f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x1874c309c _pthread_cond_wait + 984
2   Electron Framework            	       0x11bc57f10 uv_cond_wait + 40
3   Electron Framework            	       0x11bc4755c uv_cancel + 700
4   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
5   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 14:: libuv-worker
0   libsystem_kernel.dylib        	       0x1874834f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x1874c309c _pthread_cond_wait + 984
2   Electron Framework            	       0x11bc57f10 uv_cond_wait + 40
3   Electron Framework            	       0x11bc4755c uv_cancel + 700
4   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
5   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 15:: libuv-worker
0   libsystem_kernel.dylib        	       0x18747fbb0 semaphore_wait_trap + 8
1   libdispatch.dylib             	       0x187308970 _dispatch_sema4_wait + 28
2   libdispatch.dylib             	       0x187308f20 _dispatch_semaphore_wait_slow + 132
3   vscode-policy-watcher.node    	       0x10579f2bc PolicyWatcher::Execute(Napi::AsyncProgressQueueWorker<Policy const*>::ExecutionProgress const&) + 272
4   vscode-policy-watcher.node    	       0x10579fb44 Napi::AsyncProgressQueueWorker<Policy const*>::Execute() + 32
5   vscode-policy-watcher.node    	       0x10579f114 Napi::AsyncWorker::OnExecute(Napi::Env) + 32
6   Electron Framework            	       0x11bf1884c node::ThreadPoolWork::ScheduleWork()::'lambda'(uv_work_s*)::__invoke(uv_work_s*) + 52
7   Electron Framework            	       0x11bc474c4 uv_cancel + 548
8   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
9   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 16:: libuv-worker
0   libsystem_kernel.dylib        	       0x1874834f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x1874c309c _pthread_cond_wait + 984
2   Electron Framework            	       0x11bc57f10 uv_cond_wait + 40
3   Electron Framework            	       0x11bc4755c uv_cancel + 700
4   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
5   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 17:
0   libsystem_kernel.dylib        	       0x187485f30 kevent + 8
1   Electron Framework            	       0x11bc5cff8 uv__io_poll + 1840
2   Electron Framework            	       0x11bc4b010 uv_run + 376
3   Electron Framework            	       0x11be79e58 node::SpinEventLoopInternal(node::Environment*) + 360
4   Electron Framework            	       0x11c071af0 node::worker::Worker::Run() + 2008
5   Electron Framework            	       0x11c07611c _register_external_reference_worker(node::ExternalReferenceRegistry*) + 4504
6   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
7   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 18:
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x11b2f5cb4 node::PrincipalRealm::wasm_streaming_object_constructor() const + 53728
5   Electron Framework            	       0x11b2f592c node::PrincipalRealm::wasm_streaming_object_constructor() const + 52824
6   Electron Framework            	       0x120e102e0 temporal_rs_PlainTime_microsecond + 7057248
7   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
8   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 19:: NetworkConfigWatcher
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   CoreFoundation                	       0x187561c80 __CFRunLoopServiceMachPort + 160
5   CoreFoundation                	       0x1875605d8 __CFRunLoopRun + 1188
6   CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
7   Foundation                    	       0x189787bd4 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212
8   Electron Framework            	       0x11b0a5c4c v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 11064
9   Electron Framework            	       0x11b0a5af4 v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 10720
10  Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
11  Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
12  Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
13  Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
14  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
15  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
16  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 20:: CrShutdownDetector
0   libsystem_kernel.dylib        	       0x187480908 read + 8
1   Electron Framework            	       0x11be41f00 node::sqlite::UserDefinedFunction::xDestroy(void*) + 453084
2   Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
3   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 21:: NetworkConfigWatcher
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   CoreFoundation                	       0x187561c80 __CFRunLoopServiceMachPort + 160
5   CoreFoundation                	       0x1875605d8 __CFRunLoopRun + 1188
6   CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
7   Foundation                    	       0x189787bd4 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212
8   Electron Framework            	       0x11b0a5c4c v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 11064
9   Electron Framework            	       0x11b0a5af4 v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 10720
10  Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
11  Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
12  Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
13  Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
14  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
15  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
16  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 22:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 23:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 24:: ThreadPoolSingleThreadForegroundBlocking0
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f92dc uv_get_osfhandle + 91120
9   Electron Framework            	       0x1196f58a4 uv_get_osfhandle + 76216
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 25:: CompositorTileWorker1
0   libsystem_kernel.dylib        	       0x1874834f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x1874c309c _pthread_cond_wait + 984
2   Electron Framework            	       0x11a296bb8 v8::internal::OptimizingCompileTaskExecutor::RunCompilationJob(v8::internal::OptimizingCompileTaskState&, v8::internal::Isolate*, v8::internal::LocalIsolate&, v8::internal::TurbofanCompilationJob*) + 69212
3   Electron Framework            	       0x11a4aecd0 v8::RegExp::New(v8::Local<v8::Context>, v8::Local<v8::String>, v8::RegExp::Flags) + 254388
4   Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
5   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
6   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 26:
0   libsystem_kernel.dylib        	       0x18747fbb0 semaphore_wait_trap + 8
1   Electron Framework            	       0x11bc57d78 uv_sem_wait + 24
2   Electron Framework            	       0x11bddaf50 node::sqlite::UserDefinedFunction::xDestroy(void*) + 31276
3   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 27:: NetworkNotificationThreadMac
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   CoreFoundation                	       0x187561c80 __CFRunLoopServiceMachPort + 160
5   CoreFoundation                	       0x1875605d8 __CFRunLoopRun + 1188
6   CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
7   Foundation                    	       0x189787bd4 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212
8   Electron Framework            	       0x11b0a5c4c v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 11064
9   Electron Framework            	       0x11b0a5af4 v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 10720
10  Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
11  Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
12  Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
13  Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
14  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
15  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
16  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 28:: ThreadPoolSingleThreadSharedBackgroundBlocking1
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f92b0 uv_get_osfhandle + 91076
9   Electron Framework            	       0x1196f58b8 uv_get_osfhandle + 76236
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 29:: NetworkConfigWatcher
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   CoreFoundation                	       0x187561c80 __CFRunLoopServiceMachPort + 160
5   CoreFoundation                	       0x1875605d8 __CFRunLoopRun + 1188
6   CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
7   Foundation                    	       0x189787bd4 -[NSRunLoop(NSRunLoop) runMode:beforeDate:] + 212
8   Electron Framework            	       0x11b0a5c4c v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 11064
9   Electron Framework            	       0x11b0a5af4 v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&) + 10720
10  Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
11  Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
12  Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
13  Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
14  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
15  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
16  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 30:: ThreadPoolBackgroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f59a4 uv_get_osfhandle + 76472
9   Electron Framework            	       0x1196f587c uv_get_osfhandle + 76176
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 31:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 32:: ThreadPoolSingleThreadSharedForeground2
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f59d0 uv_get_osfhandle + 76516
9   Electron Framework            	       0x1196f5890 uv_get_osfhandle + 76196
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 33:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 34:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 35:: ThreadPoolForegroundWorker
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   Electron Framework            	       0x1196f65c8 uv_get_osfhandle + 79580
5   Electron Framework            	       0x1196f63b8 uv_get_osfhandle + 79052
6   Electron Framework            	       0x1196f9298 uv_get_osfhandle + 91052
7   Electron Framework            	       0x1196f6034 uv_get_osfhandle + 78152
8   Electron Framework            	       0x1196f5924 uv_get_osfhandle + 76344
9   Electron Framework            	       0x1196f5848 uv_get_osfhandle + 76124
10  Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
11  libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
12  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 36:
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   CoreFoundation                	       0x187561c80 __CFRunLoopServiceMachPort + 160
5   CoreFoundation                	       0x1875605d8 __CFRunLoopRun + 1188
6   CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
7   CoreFoundation                	       0x1875b7a44 CFRunLoopRun + 64
8   Electron Framework            	       0x11bc5c0c4 uv__fsevents_close + 1408
9   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
10  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 37:: CacheThread_BlockFile
0   libsystem_kernel.dylib        	       0x18748bb84 kevent64 + 8
1   Electron Framework            	       0x11a81fa64 cxxbridge1$box$rust_png$Reader$drop + 191108
2   Electron Framework            	       0x11a81f010 cxxbridge1$box$rust_png$Reader$drop + 188464
3   Electron Framework            	       0x11aa899bc node::PrincipalRealm::async_hooks_callback_trampoline() const + 103452
4   Electron Framework            	       0x11abd34f4 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144976
5   Electron Framework            	       0x11abd3268 node::PrincipalRealm::crypto_key_object_private_constructor() const + 144324
6   Electron Framework            	       0x11abd312c node::PrincipalRealm::crypto_key_object_private_constructor() const + 144008
7   Electron Framework            	       0x11a3d2950 node::PrincipalRealm::maybe_cache_generated_source_map() const + 147224
8   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
9   libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 38:: com.apple.NSURLConnectionLoader
0   libsystem_kernel.dylib        	       0x18747fc34 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x187492028 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x18748898c mach_msg_overwrite + 484
3   libsystem_kernel.dylib        	       0x18747ffb4 mach_msg + 24
4   CoreFoundation                	       0x187561c80 __CFRunLoopServiceMachPort + 160
5   CoreFoundation                	       0x1875605d8 __CFRunLoopRun + 1188
6   CoreFoundation                	       0x18761e898 _CFRunLoopRunSpecificWithOptions + 532
7   CFNetwork                     	       0x18d9e4c3c +[__CFN_CoreSchedulingSetRunnable _run:] + 416
8   Foundation                    	       0x188d67750 __NSThread__start__ + 732
9   libsystem_pthread.dylib       	       0x1874c2bc8 _pthread_start + 136
10  libsystem_pthread.dylib       	       0x1874bdb80 thread_start + 8

Thread 39:

Thread 40:


Thread 0 crashed with ARM Thread State (64-bit):
    x0: 0x000000016ba7bd18   x1: 0x0000000000000000   x2: 0x000000011e3351c8   x3: 0x0000012403814fb3
    x4: 0x0000012403815000   x5: 0x0000000122f34588   x6: 0x0000000000000054   x7: 0xffffffff0001f700
    x8: 0x0000000123039000   x9: 0x0000000000000001  x10: 0x0000000122f84c18  x11: 0x0000000000000013
   x12: 0x0000000000000000  x13: 0x0000000000000002  x14: 0x0000000000000000  x15: 0x8f5c28f5c28f5c29
   x16: 0x00000001874bdbf0  x17: 0x00000001f3d285c0  x18: 0x0000000000000000  x19: 0x0000000000000000
   x20: 0x0000000121d2e83d  x21: 0x0000000000000013  x22: 0x000000016ba7bd7b  x23: 0x0000000000000001
   x24: 0x00000000000405b8  x25: 0x0000000000c81b95  x26: 0x0000012400510100  x27: 0x000039e30006332d
   x28: 0x000039e300000000   fp: 0x000000016ba7bd20   lr: 0x000000011e3277cc
    sp: 0x000000016ba7bd10   pc: 0x000000011e3277cc cpsr: 0x80000000
   far: 0x0000000000000000  esr: 0xf2000000 (Breakpoint) brk 0

Binary Images:
       0x104380000 -        0x104383fff com.microsoft.VSCode (1.103.1) <4c4c443e-5555-3144-a1db-8d5c6fed78b5> /Applications/Visual Studio Code.app/Contents/MacOS/Electron
       0x119458000 -        0x1228affff com.github.Electron.framework (*) <4c4c4459-5555-3144-a1ea-b7cc7b73dc85> /Applications/Visual Studio Code.app/Contents/Frameworks/Electron Framework.framework/Versions/A/Electron Framework
       0x1043fc000 -        0x104413fff com.github.Squirrel (1.0) <4c4c44c2-5555-3144-a19d-a4d47264663a> /Applications/Visual Studio Code.app/Contents/Frameworks/Squirrel.framework/Versions/A/Squirrel
       0x1044f4000 -        0x104537fff com.electron.reactive (3.1.0) <4c4c449b-5555-3144-a17d-45c2dd34dd5e> /Applications/Visual Studio Code.app/Contents/Frameworks/ReactiveObjC.framework/Versions/A/ReactiveObjC
       0x104428000 -        0x104433fff org.mantle.Mantle (1.0) <4c4c44b0-5555-3144-a1cf-86e87e5d78b9> /Applications/Visual Studio Code.app/Contents/Frameworks/Mantle.framework/Versions/A/Mantle
       0x104b8c000 -        0x104d27fff libffmpeg.dylib (*) <4c4c4418-5555-3144-a1e8-df882823b6b5> /Applications/Visual Studio Code.app/Contents/Frameworks/Electron Framework.framework/Versions/A/Libraries/libffmpeg.dylib
       0x105038000 -        0x105043fff libobjc-trampolines.dylib (*) <580e4b29-8304-342d-a21c-2a869364dc35> /usr/lib/libobjc-trampolines.dylib
       0x14b370000 -        0x14bb93fff com.apple.AGXMetalG16G-B0 (340.26.1) <3236991d-b08b-3d98-b928-10238b9fcd37> /System/Library/Extensions/AGXMetalG16G_B0.bundle/Contents/MacOS/AGXMetalG16G_B0
       0x105760000 -        0x10577ffff com.apple.security.csparser (3.0) <68d38a93-ae93-39b1-a636-19b0f3369545> /System/Library/Frameworks/Security.framework/Versions/A/PlugIns/csparser.bundle/Contents/MacOS/csparser
       0x10579c000 -        0x1057a7fff vscode-policy-watcher.node (*) <f2bee164-0956-329c-acf2-7dcb7e69965f> /Applications/Visual Studio Code.app/Contents/Resources/app/node_modules/@vscode/policy-watcher/build/Release/vscode-policy-watcher.node
       0x1180c4000 -        0x1180fffff spdlog.node (*) <634649a7-7523-3506-8075-0aa8f8a344ca> /Applications/Visual Studio Code.app/Contents/Resources/app/node_modules/@vscode/spdlog/build/Release/spdlog.node
       0x118a88000 -        0x118c23fff vscode-sqlite3.node (*) <200a8d95-9f94-3463-95bd-64b04cd883b8> /Applications/Visual Studio Code.app/Contents/Resources/app/node_modules/@vscode/sqlite3/build/Release/vscode-sqlite3.node
       0x1186f8000 -        0x1186fbfff keymapping.node (*) <81fbfda6-ae68-342a-b0a7-3288461e02a1> /Applications/Visual Studio Code.app/Contents/Resources/app/node_modules/native-keymap/build/Release/keymapping.node
               0x0 - 0xffffffffffffffff ??? (*) <00000000-0000-0000-0000-000000000000> ???
       0x187502000 -        0x187a4ef7f com.apple.CoreFoundation (6.9) <abc6831d-f275-379e-a645-84102778d2a3> /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation
       0x193e78000 -        0x19417a6df com.apple.HIToolbox (2.1.1) <d25cb3ee-608d-3934-bc87-b97c714e332c> /System/Library/Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework/Versions/A/HIToolbox
       0x18b927000 -        0x18d01f55f com.apple.AppKit (6.9) <80f05729-fb1b-34d0-b4f3-052ee9037b03> /System/Library/Frameworks/AppKit.framework/Versions/C/AppKit
       0x1870fd000 -        0x18719b6e3 dyld (*) <09b89563-df74-3b6c-a915-241c4752e5b4> /usr/lib/dyld
       0x1874bc000 -        0x1874c8a67 libsystem_pthread.dylib (*) <1db1f8c5-d5d8-3485-b5e2-c5f75a9d689e> /usr/lib/system/libsystem_pthread.dylib
       0x18747f000 -        0x1874bb45f libsystem_kernel.dylib (*) <f422da94-53ac-36ae-a166-82e4c905ecd2> /usr/lib/system/libsystem_kernel.dylib
       0x1874c9000 -        0x1874d105f libsystem_platform.dylib (*) <6d8d83b9-f558-376b-b0b5-53fa7d7d5731> /usr/lib/system/libsystem_platform.dylib
       0x187305000 -        0x18734be5f libdispatch.dylib (*) <553d7026-4684-3483-8faf-eee6ffa9a0a6> /usr/lib/system/libdispatch.dylib
       0x188d41000 -        0x189ccc5df com.apple.Foundation (6.9) <b7f5a950-39e3-3616-b895-f260036c9590> /System/Library/Frameworks/Foundation.framework/Versions/C/Foundation
       0x1870cc000 -        0x1870fcab0 libdyld.dylib (*) <be17cf9e-d613-3012-b515-72181b2f008e> /usr/lib/system/libdyld.dylib
       0x18d79a000 -        0x18db53a7f com.apple.CFNetwork (1.0) <10bc915e-16e7-3b21-8e1b-3295a051249f> /System/Library/Frameworks/CFNetwork.framework/Versions/A/CFNetwork

External Modification Summary:
  Calls made by other processes targeting this process:
    task_for_pid: 0
    thread_create: 0
    thread_set_state: 0
  Calls made by this process:
    task_for_pid: 0
    thread_create: 0
    thread_set_state: 0
  Calls made by all processes on this machine:
    task_for_pid: 0
    thread_create: 0
    thread_set_state: 0

-----------
Full Report
-----------

{"app_name":"Electron","timestamp":"2025-08-16 10:03:51.00 +0100","app_version":"1.103.1","slice_uuid":"4c4c443e-5555-3144-a1db-8d5c6fed78b5","build_version":"1.103.1","platform":1,"bundleID":"com.microsoft.VSCode","share_with_app_devs":1,"is_first_party":0,"bug_type":"309","os_version":"macOS 26.0 (25A5338b)","roots_installed":0,"name":"Electron","incident_id":"47803C92-8E56-4CD9-8759-1C7074C63E5D"}
{
  "uptime" : 260000,
  "procRole" : "Foreground",
  "version" : 2,
  "userID" : 501,
  "deployVersion" : 210,
  "modelCode" : "Mac16,13",
  "coalitionID" : 13141,
  "osVersion" : {
    "train" : "macOS 26.0",
    "build" : "25A5338b",
    "releaseType" : "User"
  },
  "captureTime" : "2025-08-16 10:03:47.4153 +0100",
  "codeSigningMonitor" : 2,
  "incident" : "47803C92-8E56-4CD9-8759-1C7074C63E5D",
  "pid" : 28699,
  "translated" : false,
  "cpuType" : "ARM-64",
  "roots_installed" : 0,
  "bug_type" : "309",
  "procLaunch" : "2025-08-16 00:35:23.1608 +0100",
  "procStartAbsTime" : 5463395846556,
  "procExitAbsTime" : 6279284819252,
  "procName" : "Electron",
  "procPath" : "\/Applications\/Visual Studio Code.app\/Contents\/MacOS\/Electron",
  "bundleInfo" : {"CFBundleShortVersionString":"1.103.1","CFBundleVersion":"1.103.1","CFBundleIdentifier":"com.microsoft.VSCode"},
  "storeInfo" : {"deviceIdentifierForVendor":"FD06918A-805D-5E60-9517-132539AD3E2A","thirdParty":true},
  "parentProc" : "launchd",
  "parentPid" : 1,
  "coalitionName" : "com.microsoft.VSCode",
  "crashReporterKey" : "4E207357-19A3-A70F-DAD5-7940E32325FE",
  "lowPowerMode" : 1,
  "developerMode" : 1,
  "codeSigningID" : "com.microsoft.VSCode",
  "codeSigningTeamID" : "UBF8T346G9",
  "codeSigningFlags" : 570503953,
  "codeSigningValidationCategory" : 6,
  "codeSigningTrustLevel" : 4294967295,
  "codeSigningAuxiliaryInfo" : 0,
  "instructionByteStream" : {"beforePC":"gf\/\/VO\/\/\/xf\/gwDR\/XsBqf1DAJGIaALQAMEC+eAHAPngIwCRhz3Flg==","atPC":"AAAg1AAAQNQgACDU\/Xu\/qf0DAJHz\/\/+X9E++qf17Aan9QwCR8wMAqg=="},
  "bootSessionUUID" : "1C280AD3-E81D-456A-A92F-265CF0D7E678",
  "wakeTime" : 18519,
  "sleepWakeUUID" : "48BC6E61-0466-445A-8B83-8DC7D53E3F2C",
  "sip" : "enabled",
  "exception" : {"codes":"0x0000000000000001, 0x000000011e3277cc","rawCodes":[1,4801591244],"type":"EXC_BREAKPOINT","signal":"SIGTRAP"},
  "termination" : {"flags":0,"code":5,"namespace":"SIGNAL","indicator":"Trace\/BPT trap: 5","byProc":"exc handler","byPid":28699},
  "os_fault" : {"process":"Electron"},
  "extMods" : {"caller":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"system":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"targeted":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"warnings":0},
  "faultingThread" : 0,
  "threads" : [{"triggered":true,"id":6283195,"name":"CrBrowserMain","threadState":{"x":[{"value":6101122328},{"value":0},{"value":4801647048,"symbolLocation":3609192,"symbol":"ares_llist_node_first"},{"value":1254189256627},{"value":1254189256704},{"value":4881335688},{"value":84},{"value":18446744069414713088},{"value":4882403328,"symbolLocation":4440,"symbol":"cppgc::internal::CagedHeapBase::g_age_table_size_"},{"value":1},{"value":4881665048},{"value":19},{"value":0},{"value":2},{"value":0},{"value":10330176681277348905},{"value":6564862960,"symbolLocation":0,"symbol":"pthread_getspecific"},{"value":8385627584,"symbolLocation":0,"symbol":"_main_thread"},{"value":0},{"value":0},{"value":4862437437},{"value":19},{"value":6101122427},{"value":1},{"value":263608},{"value":13114261},{"value":1254135759104},{"value":63647120765741},{"value":63647120359424}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4801591244},"cpsr":{"value":2147483648},"fp":{"value":6101122336},"sp":{"value":6101122320},"esr":{"value":4060086272,"description":"(Breakpoint) brk 0"},"pc":{"value":4801591244,"matchesCrashFrame":1},"far":{"value":0}},"frames":[{"imageOffset":82638796,"symbol":"ares_llist_node_first","symbolLocation":3553388,"imageIndex":1},{"imageOffset":82638796,"symbol":"ares_llist_node_first","symbolLocation":3553388,"imageIndex":1},{"imageOffset":82638820,"symbol":"ares_llist_node_first","symbolLocation":3553412,"imageIndex":1},{"imageOffset":82638848,"symbol":"ares_llist_node_first","symbolLocation":3553440,"imageIndex":1},{"imageOffset":43524340,"symbol":"node::sqlite::UserDefinedFunction::xDestroy(void*)","symbolLocation":27600,"imageIndex":1},{"imageOffset":58159856,"symbol":"v8::PropertyDescriptor::set() const","symbolLocation":4297956,"imageIndex":1},{"imageOffset":58159748,"symbol":"v8::PropertyDescriptor::set() const","symbolLocation":4297848,"imageIndex":1},{"imageOffset":4829808,"symbol":"v8::internal::compiler::CompilationDependencies::Commit(v8::internal::Handle<v8::internal::Code>)","symbolLocation":12724,"imageIndex":1},{"imageOffset":285592,"symbol":"node::Blob::GetTransferMode() const","symbolLocation":29476,"imageIndex":1},{"imageOffset":308940,"symbol":"node::Blob::GetTransferMode() const","symbolLocation":52824,"imageIndex":1},{"imageOffset":13186420,"symbol":"v8::String::NewFromUtf8(v8::Isolate*, char const*, v8::NewStringType, int)","symbolLocation":392,"imageIndex":1},{"imageOffset":13186140,"symbol":"v8::String::NewFromUtf8(v8::Isolate*, char const*, v8::NewStringType, int)","symbolLocation":112,"imageIndex":1},{"imageOffset":46421520,"symbol":"node::StringBytes::Encode(v8::Isolate*, char const*, unsigned long, node::encoding, v8::Local<v8::Value>*)","symbolLocation":252,"imageIndex":1},{"imageOffset":44906436,"symbol":"node::Buffer::RegisterExternalReferences(node::ExternalReferenceRegistry*)","symbolLocation":28512,"imageIndex":1},{"imageOffset":5769331628,"imageIndex":13},{"imageOffset":5638673384,"imageIndex":13},{"imageOffset":5640854268,"imageIndex":13},{"imageOffset":5640971284,"imageIndex":13},{"imageOffset":5639571540,"imageIndex":13},{"imageOffset":5640968856,"imageIndex":13},{"imageOffset":5769310760,"imageIndex":13},{"imageOffset":5769309812,"imageIndex":13},{"imageOffset":2056968,"symbol":"v8::Function::Call(v8::Isolate*, v8::Local<v8::Context>, v8::Local<v8::Value>, int, v8::Local<v8::Value>*)","symbolLocation":3576,"imageIndex":1},{"imageOffset":2053796,"symbol":"v8::Function::Call(v8::Isolate*, v8::Local<v8::Context>, v8::Local<v8::Value>, int, v8::Local<v8::Value>*)","symbolLocation":404,"imageIndex":1},{"imageOffset":44176456,"symbol":"node::InternalMakeCallback(node::Environment*, v8::Local<v8::Object>, v8::Local<v8::Object>, v8::Local<v8::Function>, int, v8::Local<v8::Value>*, node::async_context, v8::Local<v8::Value>)","symbolLocation":512,"imageIndex":1},{"imageOffset":44177440,"symbol":"node::InternalMakeCallback(v8::Isolate*, v8::Local<v8::Object>, v8::Local<v8::Function>, int, v8::Local<v8::Value>*, node::async_context, v8::Local<v8::Value>)","symbolLocation":304,"imageIndex":1},{"imageOffset":43502268,"symbol":"node::sqlite::UserDefinedFunction::xDestroy(void*)","symbolLocation":5528,"imageIndex":1},{"imageOffset":42814024,"symbol":"node::AsyncWrap::~AsyncWrap()","symbolLocation":541412,"imageIndex":1},{"imageOffset":42813804,"symbol":"node::AsyncWrap::~AsyncWrap()","symbolLocation":541192,"imageIndex":1},{"imageOffset":12544728,"symbol":"v8::internal::ThreadIsolation::RegisterJitPage(unsigned long, unsigned long)","symbolLocation":53484,"imageIndex":1},{"imageOffset":1218440,"symbol":"temporal_rs_PlainTime_second","symbolLocation":1244,"imageIndex":1},{"imageOffset":1215912,"symbol":"v8::HandleScope::~HandleScope()","symbolLocation":22132,"imageIndex":1},{"imageOffset":40512356,"symbol":"v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef)","symbolLocation":463296,"imageIndex":1},{"imageOffset":3489144,"symbol":"v8::ExternalMemoryAccounter::Increase(v8::Isolate*, unsigned long)","symbolLocation":58696,"imageIndex":1},{"imageOffset":40511672,"symbol":"v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef)","symbolLocation":462612,"imageIndex":1},{"imageOffset":391896,"symbol":"__CFRUNLOOP_IS_CALLING_OUT_TO_A_SOURCE0_PERFORM_FUNCTION__","symbolLocation":28,"imageIndex":14},{"imageOffset":391788,"symbol":"__CFRunLoopDoSource0","symbolLocation":172,"imageIndex":14},{"imageOffset":391128,"symbol":"__CFRunLoopDoSources0","symbolLocation":232,"imageIndex":14},{"imageOffset":386152,"symbol":"__CFRunLoopRun","symbolLocation":820,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":792368,"symbol":"RunCurrentEventLoopInMode","symbolLocation":316,"imageIndex":15},{"imageOffset":805304,"symbol":"ReceiveNextEventCommon","symbolLocation":464,"imageIndex":15},{"imageOffset":2417116,"symbol":"_BlockUntilNextEventMatchingListInMode","symbolLocation":48,"imageIndex":15},{"imageOffset":5268164,"symbol":"_DPSBlockUntilNextEventMatchingListInMode","symbolLocation":236,"imageIndex":16},{"imageOffset":130860,"symbol":"_DPSNextEvent","symbolLocation":588,"imageIndex":16},{"imageOffset":10925444,"symbol":"-[NSApplication(NSEventRouting) _nextEventMatchingEventMask:untilDate:inMode:dequeue:]","symbolLocation":688,"imageIndex":16},{"imageOffset":10924688,"symbol":"-[NSApplication(NSEventRouting) nextEventMatchingMask:untilDate:inMode:dequeue:]","symbolLocation":72,"imageIndex":16},{"imageOffset":100208,"symbol":"-[NSApplication run]","symbolLocation":368,"imageIndex":16},{"imageOffset":29678812,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":11208,"imageIndex":1},{"imageOffset":29678324,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":10720,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":31717144,"symbol":"node::PrincipalRealm::inspector_enable_async_hooks() const","symbolLocation":85928,"imageIndex":1},{"imageOffset":31716968,"symbol":"node::PrincipalRealm::inspector_enable_async_hooks() const","symbolLocation":85752,"imageIndex":1},{"imageOffset":32038416,"symbol":"v8::Message::GetLineNumber(v8::Local<v8::Context>) const","symbolLocation":22864,"imageIndex":1},{"imageOffset":32038168,"symbol":"v8::Message::GetLineNumber(v8::Local<v8::Context>) const","symbolLocation":22616,"imageIndex":1},{"imageOffset":27245792,"symbol":"v8::internal::ThreadIsolation::JitPageReference::Shrink(v8::internal::ThreadIsolation::JitPage*)","symbolLocation":58156,"imageIndex":1},{"imageOffset":27231792,"symbol":"v8::internal::ThreadIsolation::JitPageReference::Shrink(v8::internal::ThreadIsolation::JitPage*)","symbolLocation":44156,"imageIndex":1},{"imageOffset":30703736,"symbol":"rust_png$cxxbridge1$Reader$get_trns_chunk","symbolLocation":22836,"imageIndex":1},{"imageOffset":30701980,"symbol":"rust_png$cxxbridge1$Reader$get_trns_chunk","symbolLocation":21080,"imageIndex":1},{"imageOffset":41964868,"symbol":"ElectronMain","symbolLocation":124,"imageIndex":1},{"imageOffset":35108,"symbol":"start","symbolLocation":6400,"imageIndex":17}]},{"id":6283285,"name":"com.apple.NSEventThread","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":128655745351680},{"value":0},{"value":128655745351680},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":29955},{"value":0},{"value":18446744073709551569},{"value":8408933984},{"value":0},{"value":4294967295},{"value":2},{"value":128655745351680},{"value":0},{"value":128655745351680},{"value":6104555656},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6104555504},"sp":{"value":6104555424},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":392320,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":14},{"imageOffset":386520,"symbol":"__CFRunLoopRun","symbolLocation":1188,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":719432,"symbol":"_NSEventThread","symbolLocation":184,"imageIndex":16},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283287,"name":"ThreadPoolServiceThread","threadState":{"x":[{"value":4},{"value":0},{"value":0},{"value":1254132180992},{"value":4},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":3},{"value":47279000005378},{"value":2800},{"value":6283287},{"value":1254190227184},{"value":1056496},{"value":369},{"value":1236951904512},{"value":0},{"value":1236953168112},{"value":1236951649408},{"value":0},{"value":12297829382473034411},{"value":1},{"value":12297829382473034410},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4739693156},"cpsr":{"value":2684354560},"fp":{"value":6112980368},"sp":{"value":6112980224},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564658052},"far":{"value":0}},"frames":[{"imageOffset":52100,"symbol":"kevent64","symbolLocation":8,"imageIndex":19},{"imageOffset":20740708,"symbol":"cxxbridge1$box$rust_png$Reader$drop","symbolLocation":191108,"imageIndex":1},{"imageOffset":20738064,"symbol":"cxxbridge1$box$rust_png$Reader$drop","symbolLocation":188464,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":40498024,"symbol":"v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef)","symbolLocation":448964,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283288,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":150645977907200},{"value":0},{"value":150645977907200},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":35075},{"value":578048},{"value":18446744073709551569},{"value":1236951906304},{"value":0},{"value":0},{"value":32},{"value":150645977907200},{"value":0},{"value":150645977907200},{"value":6121401616},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6121400976},"sp":{"value":6121400896},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283289,"name":"ThreadPoolBackgroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":171536698834944},{"value":0},{"value":171536698834944},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":39939},{"value":850944},{"value":18446744073709551569},{"value":1236951902720},{"value":0},{"value":0},{"value":32},{"value":171536698834944},{"value":0},{"value":171536698834944},{"value":6129822992},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6129822352},"sp":{"value":6129822272},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742692,"symbol":"uv_get_osfhandle","symbolLocation":76472,"imageIndex":1},{"imageOffset":2742396,"symbol":"uv_get_osfhandle","symbolLocation":76176,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283290,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":169337675579392},{"value":0},{"value":169337675579392},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":39427},{"value":383504},{"value":18446744073709551569},{"value":1236951908096},{"value":0},{"value":0},{"value":32},{"value":169337675579392},{"value":0},{"value":169337675579392},{"value":6138244368},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6138243728},"sp":{"value":6138243648},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283291,"name":"Chrome_IOThread","threadState":{"x":[{"value":1},{"value":0},{"value":0},{"value":1254152388736},{"value":10},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":9223372036854775810},{"value":261636448250},{"value":2688},{"value":6283291},{"value":1},{"value":22},{"value":369},{"value":1254131171328},{"value":0},{"value":1236953160432},{"value":1254131631488},{"value":0},{"value":12297829382473034411},{"value":1},{"value":12297829382473034410},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4739693156},"cpsr":{"value":2147483648},"fp":{"value":6146665856},"sp":{"value":6146665712},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564658052},"far":{"value":0}},"frames":[{"imageOffset":52100,"symbol":"kevent64","symbolLocation":8,"imageIndex":19},{"imageOffset":20740708,"symbol":"cxxbridge1$box$rust_png$Reader$drop","symbolLocation":191108,"imageIndex":1},{"imageOffset":20738064,"symbol":"cxxbridge1$box$rust_png$Reader$drop","symbolLocation":188464,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":31357816,"symbol":"v8::Message::Get() const","symbolLocation":20328,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283292,"name":"MemoryInfra","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":190228396507136},{"value":0},{"value":190228396507136},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":44291},{"value":0},{"value":18446744073709551569},{"value":1254131172992},{"value":0},{"value":0},{"value":32},{"value":190228396507136},{"value":0},{"value":190228396507136},{"value":6155086896},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6155086256},"sp":{"value":6155086176},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":12551416,"symbol":"v8::internal::ThreadIsolation::RegisterJitPage(unsigned long, unsigned long)","symbolLocation":60172,"imageIndex":1},{"imageOffset":40471736,"symbol":"v8::internal::compiler::CompilationDependencies::DependOnInitialMap(v8::internal::compiler::JSFunctionRef)","symbolLocation":422676,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283296,"frames":[{"imageOffset":28464,"symbol":"kevent","symbolLocation":8,"imageIndex":19},{"imageOffset":41963512,"symbol":"uv__io_poll","symbolLocation":1840,"imageIndex":1},{"imageOffset":41889808,"symbol":"uv_run","symbolLocation":376,"imageIndex":1},{"imageOffset":45619952,"symbol":"node::WorkerThreadsTaskRunner::DelayedTaskScheduler::Start()::'lambda'(void*)::__invoke(void*)","symbolLocation":112,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":4},{"value":0},{"value":0},{"value":6163476176},{"value":1024},{"value":0},{"value":0},{"value":0},{"value":6163476128},{"value":4294967295},{"value":0},{"value":65536},{"value":1},{"value":0},{"value":0},{"value":0},{"value":363},{"value":8408940656},{"value":0},{"value":1254135236328},{"value":1},{"value":4294967295},{"value":0},{"value":65531},{"value":1254135236416},{"value":0},{"value":6163476176},{"value":111},{"value":1254135236864}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4760915960},"cpsr":{"value":1610612736},"fp":{"value":6163509040},"sp":{"value":6163476048},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564634416},"far":{"value":0}}},{"id":6283297,"frames":[{"imageOffset":1435712,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":13760,"imageIndex":1},{"imageOffset":1435708,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":13756,"imageIndex":1},{"imageOffset":1434568,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":12616,"imageIndex":1},{"imageOffset":1434056,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":12104,"imageIndex":1},{"imageOffset":95280244,"symbol":"temporal_rs_PlainDate_iso_month","symbolLocation":9536808,"imageIndex":1},{"imageOffset":45610856,"symbol":"node::WorkerThreadsTaskRunner::WorkerThreadsTaskRunner(int, node::PlatformDebugLogLevel)","symbolLocation":1388,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":0},{"value":244332},{"value":244380},{"value":14},{"value":63647135665728},{"value":32},{"value":1254133715968},{"value":0},{"value":954},{"value":63647135563792},{"value":4630281508966400008},{"value":63647135793152},{"value":8},{"value":24},{"value":0},{"value":24},{"value":6564921328,"symbolLocation":0,"symbol":"__bzero"},{"value":0},{"value":0},{"value":1254151973888},{"value":0},{"value":1254151974208},{"value":63647135808156},{"value":4882398376,"symbolLocation":24,"symbol":"v8::internal::ThreadIsolation::trusted_data_"},{"value":954},{"value":4630281508832149504},{"value":48},{"value":0},{"value":63647135808108}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4720388156},"cpsr":{"value":0},"fp":{"value":6171930064},"sp":{"value":6171929808},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":4720388160},"far":{"value":0}}},{"id":6283298,"frames":[{"imageOffset":1439956,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":18004,"imageIndex":1},{"imageOffset":1435768,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":13816,"imageIndex":1},{"imageOffset":1434568,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":12616,"imageIndex":1},{"imageOffset":1433860,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":11908,"imageIndex":1},{"imageOffset":95280244,"symbol":"temporal_rs_PlainDate_iso_month","symbolLocation":9536808,"imageIndex":1},{"imageOffset":45610856,"symbol":"node::WorkerThreadsTaskRunner::WorkerThreadsTaskRunner(int, node::PlatformDebugLogLevel)","symbolLocation":1388,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":6180351312},{"value":63647120359645},{"value":46800},{"value":14},{"value":1},{"value":32},{"value":1254466152448},{"value":0},{"value":63647120359424},{"value":0},{"value":48128},{"value":63648958414848},{"value":272},{"value":24},{"value":0},{"value":24},{"value":6564921328,"symbolLocation":0,"symbol":"__bzero"},{"value":0},{"value":0},{"value":1254270144512},{"value":63647977356457},{"value":1254270144832},{"value":63647977354960},{"value":4882398376,"symbolLocation":24,"symbol":"v8::internal::ThreadIsolation::trusted_data_"},{"value":188},{"value":4398046511104},{"value":1544},{"value":221},{"value":63647977356456}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4720388216},"cpsr":{"value":2147483648},"fp":{"value":6180351440},"sp":{"value":6180351184},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":4720392404},"far":{"value":0}}},{"id":6283299,"frames":[{"imageOffset":1440008,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":18056,"imageIndex":1},{"imageOffset":1435768,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":13816,"imageIndex":1},{"imageOffset":1434568,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":12616,"imageIndex":1},{"imageOffset":1434008,"symbol":"v8::CppHeapExternal::ValueImpl(v8::Isolate*, v8::CppHeapPointerTagRange) const","symbolLocation":12056,"imageIndex":1},{"imageOffset":95280244,"symbol":"temporal_rs_PlainDate_iso_month","symbolLocation":9536808,"imageIndex":1},{"imageOffset":45610856,"symbol":"node::WorkerThreadsTaskRunner::WorkerThreadsTaskRunner(int, node::PlatformDebugLogLevel)","symbolLocation":1388,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":6188772688},{"value":63647120359645},{"value":201428},{"value":14},{"value":1},{"value":32},{"value":1254198943744},{"value":0},{"value":6188772688},{"value":32},{"value":4294967123},{"value":63647572017152},{"value":0},{"value":24},{"value":0},{"value":24},{"value":6564921328,"symbolLocation":0,"symbol":"__bzero"},{"value":0},{"value":0},{"value":1254258675712},{"value":63647805280981},{"value":1254258676032},{"value":63647805280980},{"value":4882398376,"symbolLocation":24,"symbol":"v8::internal::ThreadIsolation::trusted_data_"},{"value":786},{"value":9007199254740992},{"value":1380},{"value":221},{"value":63647805280980}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4720388216},"cpsr":{"value":2147483648},"fp":{"value":6188772816},"sp":{"value":6188772560},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":4720392456},"far":{"value":0}}},{"id":6283300,"frames":[{"imageOffset":2992,"symbol":"semaphore_wait_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":41942392,"symbol":"uv_sem_wait","symbolLocation":24,"imageIndex":1},{"imageOffset":47047120,"symbol":"node::inspector::Agent::GetWsUrl() const","symbolLocation":52,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":14},{"value":0},{"value":4765999540,"symbolLocation":24,"symbol":"node::inspector::Agent::GetWsUrl() const"},{"value":0},{"value":6188855296},{"value":419432703},{"value":0},{"value":0},{"value":4765999540,"symbolLocation":24,"symbol":"node::inspector::Agent::GetWsUrl() const"},{"value":64516},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":18446744073709551580},{"value":8408932328},{"value":0},{"value":4881363604},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4760894840},"cpsr":{"value":536870912},"fp":{"value":6188855184},"sp":{"value":6188855168},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564608944},"far":{"value":0}}},{"id":6283307,"name":"libuv-worker","threadState":{"x":[{"value":4},{"value":0},{"value":8974080},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6197292744},{"value":0},{"value":86272},{"value":370535418646786},{"value":370535418646786},{"value":86272},{"value":0},{"value":370535418646784},{"value":305},{"value":8408932112},{"value":0},{"value":4881331296},{"value":4881331360},{"value":6197293280},{"value":0},{"value":0},{"value":8974080},{"value":8974080},{"value":8974848},{"value":4881330176},{"value":1254154217840}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564884636},"cpsr":{"value":1610612736},"fp":{"value":6197292864},"sp":{"value":6197292720},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564623608},"far":{"value":0}},"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":19},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":18},{"imageOffset":41942800,"symbol":"uv_cond_wait","symbolLocation":40,"imageIndex":1},{"imageOffset":41874780,"symbol":"uv_cancel","symbolLocation":700,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283308,"name":"libuv-worker","threadState":{"x":[{"value":4},{"value":0},{"value":8974592},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6205730504},{"value":0},{"value":86272},{"value":370535418646786},{"value":370535418646786},{"value":86272},{"value":0},{"value":370535418646784},{"value":305},{"value":8408932112},{"value":0},{"value":4881331296},{"value":4881331360},{"value":6205731040},{"value":0},{"value":0},{"value":8974592},{"value":8974592},{"value":8975360},{"value":4881330176},{"value":1254136485648}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564884636},"cpsr":{"value":1610612736},"fp":{"value":6205730624},"sp":{"value":6205730480},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564623608},"far":{"value":0}},"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":19},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":18},{"imageOffset":41942800,"symbol":"uv_cond_wait","symbolLocation":40,"imageIndex":1},{"imageOffset":41874780,"symbol":"uv_cancel","symbolLocation":700,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283309,"name":"libuv-worker","threadState":{"x":[{"value":14},{"value":8589934595},{"value":171798697235},{"value":413429256946179},{"value":14680198217728},{"value":413429256945664},{"value":48},{"value":0},{"value":0},{"value":1},{"value":0},{"value":2},{"value":0},{"value":0},{"value":6568147044,"symbolLocation":0,"symbol":"__CFMacRomanCharToUnicharTable"},{"value":1721063979},{"value":18446744073709551580},{"value":8408936456},{"value":0},{"value":1254155119392},{"value":1254155119328},{"value":18446744073709551615},{"value":4881331440},{"value":4881330176},{"value":4881331424},{"value":9223372036854775800},{"value":1},{"value":1254147914064},{"value":1254147914064}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6563072368},"cpsr":{"value":1610612736},"fp":{"value":6214168064},"sp":{"value":6214168048},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564608944},"far":{"value":0}},"frames":[{"imageOffset":2992,"symbol":"semaphore_wait_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":14704,"symbol":"_dispatch_sema4_wait","symbolLocation":28,"imageIndex":21},{"imageOffset":16160,"symbol":"_dispatch_semaphore_wait_slow","symbolLocation":132,"imageIndex":21},{"imageOffset":12988,"symbol":"PolicyWatcher::Execute(Napi::AsyncProgressQueueWorker<Policy const*>::ExecutionProgress const&)","symbolLocation":272,"imageIndex":9},{"imageOffset":15172,"symbol":"Napi::AsyncProgressQueueWorker<Policy const*>::Execute()","symbolLocation":32,"imageIndex":9},{"imageOffset":12564,"symbol":"Napi::AsyncWorker::OnExecute(Napi::Env)","symbolLocation":32,"imageIndex":9},{"imageOffset":44828748,"symbol":"node::ThreadPoolWork::ScheduleWork()::'lambda'(uv_work_s*)::__invoke(uv_work_s*)","symbolLocation":52,"imageIndex":1},{"imageOffset":41874628,"symbol":"uv_cancel","symbolLocation":548,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283310,"name":"libuv-worker","threadState":{"x":[{"value":260},{"value":0},{"value":8974336},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6222606024},{"value":0},{"value":86272},{"value":370535418646786},{"value":370535418646786},{"value":86272},{"value":0},{"value":370535418646784},{"value":305},{"value":8408932112},{"value":0},{"value":4881331296},{"value":4881331360},{"value":6222606560},{"value":0},{"value":0},{"value":8974336},{"value":8974336},{"value":8975104},{"value":4881330176},{"value":1254152458224}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564884636},"cpsr":{"value":1610612736},"fp":{"value":6222606144},"sp":{"value":6222606000},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564623608},"far":{"value":0}},"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":19},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":18},{"imageOffset":41942800,"symbol":"uv_cond_wait","symbolLocation":40,"imageIndex":1},{"imageOffset":41874780,"symbol":"uv_cancel","symbolLocation":700,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283322,"frames":[{"imageOffset":28464,"symbol":"kevent","symbolLocation":8,"imageIndex":19},{"imageOffset":41963512,"symbol":"uv__io_poll","symbolLocation":1840,"imageIndex":1},{"imageOffset":41889808,"symbol":"uv_run","symbolLocation":376,"imageIndex":1},{"imageOffset":44179032,"symbol":"node::SpinEventLoopInternal(node::Environment*)","symbolLocation":360,"imageIndex":1},{"imageOffset":46242544,"symbol":"node::worker::Worker::Run()","symbolLocation":2008,"imageIndex":1},{"imageOffset":46260508,"symbol":"_register_external_reference_worker(node::ExternalReferenceRegistry*)","symbolLocation":4504,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":4},{"value":0},{"value":0},{"value":6226815072},{"value":1024},{"value":6226815024},{"value":6226846935},{"value":0},{"value":6226815024},{"value":8},{"value":1000000},{"value":2},{"value":0},{"value":0},{"value":6226849152},{"value":839},{"value":363},{"value":1254131189632},{"value":0},{"value":6226848456},{"value":1},{"value":8100},{"value":0},{"value":65531},{"value":6226848544},{"value":0},{"value":6226815072},{"value":6226847952},{"value":6226848992}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4760915960},"cpsr":{"value":536870912},"fp":{"value":6226847936},"sp":{"value":6226814944},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564634416},"far":{"value":0}}},{"id":6283358,"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":32103604,"symbol":"node::PrincipalRealm::wasm_streaming_object_constructor() const","symbolLocation":53728,"imageIndex":1},{"imageOffset":32102700,"symbol":"node::PrincipalRealm::wasm_streaming_object_constructor() const","symbolLocation":52824,"imageIndex":1},{"imageOffset":127632096,"symbol":"temporal_rs_PlainTime_microsecond","symbolLocation":7057248,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":0},{"value":0},{"value":202323024412672},{"value":48},{"value":0},{"value":0},{"value":17179869184},{"value":48},{"value":0},{"value":0},{"value":0},{"value":47107},{"value":0},{"value":18446744073709551569},{"value":8408932328},{"value":0},{"value":0},{"value":48},{"value":202323024412672},{"value":0},{"value":0},{"value":4369416192},{"value":0},{"value":17179870210},{"value":18446744073709550527},{"value":1026}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6227421904},"sp":{"value":6227421824},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}}},{"id":6283361,"name":"NetworkConfigWatcher","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":260597140684800},{"value":0},{"value":260597140684800},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":60675},{"value":0},{"value":18446744073709551569},{"value":8408933984},{"value":0},{"value":4294967295},{"value":2},{"value":260597140684800},{"value":0},{"value":260597140684800},{"value":6395616792},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6395616640},"sp":{"value":6395616560},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":392320,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":14},{"imageOffset":386520,"symbol":"__CFRunLoopRun","symbolLocation":1188,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":10775508,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":22},{"imageOffset":29678668,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":11064,"imageIndex":1},{"imageOffset":29678324,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":10720,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283363,"name":"CrShutdownDetector","threadState":{"x":[{"value":4},{"value":0},{"value":4},{"value":6395703395},{"value":6395702728},{"value":18},{"value":0},{"value":0},{"value":18},{"value":8385675360,"symbolLocation":0,"symbol":"_current_pid"},{"value":8026668483491361347},{"value":1099511628034},{"value":1},{"value":0},{"value":4861309442},{"value":0},{"value":3},{"value":8408940752},{"value":0},{"value":1254148882416},{"value":20},{"value":6395702800},{"value":4},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4762902272},"cpsr":{"value":1610612736},"fp":{"value":6395703168},"sp":{"value":6395702800},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564612360},"far":{"value":0}},"frames":[{"imageOffset":6408,"symbol":"read","symbolLocation":8,"imageIndex":19},{"imageOffset":43949824,"symbol":"node::sqlite::UserDefinedFunction::xDestroy(void*)","symbolLocation":453084,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283364,"name":"NetworkConfigWatcher","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":207820582551552},{"value":0},{"value":207820582551552},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":48387},{"value":0},{"value":18446744073709551569},{"value":8408933984},{"value":0},{"value":4294967295},{"value":2},{"value":207820582551552},{"value":0},{"value":207820582551552},{"value":6404120088},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6404119936},"sp":{"value":6404119856},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":392320,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":14},{"imageOffset":386520,"symbol":"__CFRunLoopRun","symbolLocation":1188,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":10775508,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":22},{"imageOffset":29678668,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":11064,"imageIndex":1},{"imageOffset":29678324,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":10720,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283365,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":251801047662592},{"value":0},{"value":251801047662592},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":58627},{"value":1027920},{"value":18446744073709551569},{"value":4801667060,"symbolLocation":3629204,"symbol":"ares_llist_node_first"},{"value":0},{"value":0},{"value":32},{"value":251801047662592},{"value":0},{"value":251801047662592},{"value":6412545296},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6412544656},"sp":{"value":6412544576},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283366,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":213318140690432},{"value":0},{"value":213318140690432},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":49667},{"value":851002217},{"value":18446744073709551569},{"value":2578920405},{"value":0},{"value":0},{"value":32},{"value":213318140690432},{"value":0},{"value":213318140690432},{"value":6420966672},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6420966032},"sp":{"value":6420965952},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283367,"name":"ThreadPoolSingleThreadForegroundBlocking0","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":214452012056576},{"value":0},{"value":214452012056576},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":49931},{"value":549248},{"value":18446744073709551569},{"value":1254131207936},{"value":0},{"value":0},{"value":32},{"value":214452012056576},{"value":0},{"value":214452012056576},{"value":6429388048},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6429387408},"sp":{"value":6429387328},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2757340,"symbol":"uv_get_osfhandle","symbolLocation":91120,"imageIndex":1},{"imageOffset":2742436,"symbol":"uv_get_osfhandle","symbolLocation":76216,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283368,"name":"CompositorTileWorker1","threadState":{"x":[{"value":260},{"value":0},{"value":42240},{"value":0},{"value":0},{"value":161},{"value":0},{"value":0},{"value":6437809752},{"value":0},{"value":2048},{"value":8796093024258},{"value":8796093024258},{"value":2048},{"value":0},{"value":8796093024256},{"value":305},{"value":8408932112},{"value":0},{"value":1254133357080},{"value":1254133357208},{"value":6437810400},{"value":0},{"value":0},{"value":42240},{"value":42241},{"value":42496},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564884636},"cpsr":{"value":1610612736},"fp":{"value":6437809872},"sp":{"value":6437809728},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564623608},"far":{"value":0}},"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":19},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":18},{"imageOffset":14937016,"symbol":"v8::internal::OptimizingCompileTaskExecutor::RunCompilationJob(v8::internal::OptimizingCompileTaskState&, v8::internal::Isolate*, v8::internal::LocalIsolate&, v8::internal::TurbofanCompilationJob*)","symbolLocation":69212,"imageIndex":1},{"imageOffset":17132752,"symbol":"v8::RegExp::New(v8::Local<v8::Context>, v8::Local<v8::String>, v8::RegExp::Flags)","symbolLocation":254388,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283370,"frames":[{"imageOffset":2992,"symbol":"semaphore_wait_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":41942392,"symbol":"uv_sem_wait","symbolLocation":24,"imageIndex":1},{"imageOffset":43528016,"symbol":"node::sqlite::UserDefinedFunction::xDestroy(void*)","symbolLocation":31276,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":14},{"value":1},{"value":1254194805376},{"value":261636392794},{"value":0},{"value":0},{"value":0},{"value":0},{"value":16114527472},{"value":0},{"value":6560740088,"symbolLocation":0,"symbol":"_tlv_get_addr"},{"value":202310139557890},{"value":202310139557890},{"value":202310139557888},{"value":18563328},{"value":0},{"value":18446744073709551580},{"value":1254131212928},{"value":0},{"value":1254133007464},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4760894840},"cpsr":{"value":1610612736},"fp":{"value":16114528160},"sp":{"value":16114528144},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564608944},"far":{"value":0}}},{"id":6283371,"name":"NetworkNotificationThreadMac","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":230910326734848},{"value":0},{"value":230910326734848},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":53763},{"value":0},{"value":18446744073709551569},{"value":8408933984},{"value":0},{"value":4294967295},{"value":2},{"value":230910326734848},{"value":0},{"value":230910326734848},{"value":16122945048},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16122944896},"sp":{"value":16122944816},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":392320,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":14},{"imageOffset":386520,"symbol":"__CFRunLoopRun","symbolLocation":1188,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":10775508,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":22},{"imageOffset":29678668,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":11064,"imageIndex":1},{"imageOffset":29678324,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":10720,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283390,"name":"ThreadPoolSingleThreadSharedBackgroundBlocking1","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":318888436826112},{"value":0},{"value":318888436826112},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":74247},{"value":238464},{"value":18446744073709551569},{"value":8408940752},{"value":0},{"value":0},{"value":32},{"value":318888436826112},{"value":0},{"value":318888436826112},{"value":16131370256},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16131369616},"sp":{"value":16131369536},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2757296,"symbol":"uv_get_osfhandle","symbolLocation":91076,"imageIndex":1},{"imageOffset":2742456,"symbol":"uv_get_osfhandle","symbolLocation":76236,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283401,"name":"NetworkConfigWatcher","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":398036094156800},{"value":0},{"value":398036094156800},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":92675},{"value":0},{"value":18446744073709551569},{"value":8408933984},{"value":0},{"value":4294967295},{"value":2},{"value":398036094156800},{"value":0},{"value":398036094156800},{"value":16139787800},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16139787648},"sp":{"value":16139787568},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":392320,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":14},{"imageOffset":386520,"symbol":"__CFRunLoopRun","symbolLocation":1188,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":10775508,"symbol":"-[NSRunLoop(NSRunLoop) runMode:beforeDate:]","symbolLocation":212,"imageIndex":22},{"imageOffset":29678668,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":11064,"imageIndex":1},{"imageOffset":29678324,"symbol":"v8::ObjectTemplate::SetHandler(v8::NamedPropertyHandlerConfiguration const&)","symbolLocation":10720,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283402,"name":"ThreadPoolBackgroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":545370652278784},{"value":0},{"value":545370652278784},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":126979},{"value":1581024},{"value":18446744073709551569},{"value":1254131232896},{"value":0},{"value":0},{"value":32},{"value":545370652278784},{"value":0},{"value":545370652278784},{"value":16148213008},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16148212368},"sp":{"value":16148212288},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742692,"symbol":"uv_get_osfhandle","symbolLocation":76472,"imageIndex":1},{"imageOffset":2742396,"symbol":"uv_get_osfhandle","symbolLocation":76176,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283403,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":400235117412352},{"value":0},{"value":400235117412352},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":93187},{"value":1781536},{"value":18446744073709551569},{"value":8408939496},{"value":0},{"value":0},{"value":32},{"value":400235117412352},{"value":0},{"value":400235117412352},{"value":16156634384},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16156633744},"sp":{"value":16156633664},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283404,"name":"ThreadPoolSingleThreadSharedForeground2","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":402434140667904},{"value":0},{"value":402434140667904},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":93699},{"value":601440},{"value":18446744073709551569},{"value":8408932360},{"value":0},{"value":0},{"value":32},{"value":402434140667904},{"value":0},{"value":402434140667904},{"value":16165055760},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16165055120},"sp":{"value":16165055040},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742736,"symbol":"uv_get_osfhandle","symbolLocation":76516,"imageIndex":1},{"imageOffset":2742416,"symbol":"uv_get_osfhandle","symbolLocation":76196,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283405,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":542072117395456},{"value":0},{"value":542072117395456},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":126211},{"value":250752},{"value":18446744073709551569},{"value":2578920405},{"value":0},{"value":0},{"value":32},{"value":542072117395456},{"value":0},{"value":542072117395456},{"value":16173477136},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16173476496},"sp":{"value":16173476416},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283406,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":540972605767680},{"value":0},{"value":540972605767680},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":125955},{"value":252288},{"value":18446744073709551569},{"value":1254131221248},{"value":0},{"value":0},{"value":32},{"value":540972605767680},{"value":0},{"value":540972605767680},{"value":16181898512},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16181897872},"sp":{"value":16181897792},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283407,"name":"ThreadPoolForegroundWorker","threadState":{"x":[{"value":268451845},{"value":17179869186},{"value":0},{"value":538773582512128},{"value":0},{"value":538773582512128},{"value":32},{"value":0},{"value":0},{"value":17179869184},{"value":32},{"value":0},{"value":0},{"value":0},{"value":125443},{"value":253824},{"value":18446744073709551569},{"value":2578920405},{"value":0},{"value":0},{"value":32},{"value":538773582512128},{"value":0},{"value":538773582512128},{"value":16190319888},{"value":0},{"value":17179869186},{"value":18446744073709550527},{"value":2}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16190319248},"sp":{"value":16190319168},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":2745800,"symbol":"uv_get_osfhandle","symbolLocation":79580,"imageIndex":1},{"imageOffset":2745272,"symbol":"uv_get_osfhandle","symbolLocation":79052,"imageIndex":1},{"imageOffset":2757272,"symbol":"uv_get_osfhandle","symbolLocation":91052,"imageIndex":1},{"imageOffset":2744372,"symbol":"uv_get_osfhandle","symbolLocation":78152,"imageIndex":1},{"imageOffset":2742564,"symbol":"uv_get_osfhandle","symbolLocation":76344,"imageIndex":1},{"imageOffset":2742344,"symbol":"uv_get_osfhandle","symbolLocation":76124,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6283420,"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":392320,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":14},{"imageOffset":386520,"symbol":"__CFRunLoopRun","symbolLocation":1188,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":744004,"symbol":"CFRunLoopRun","symbolLocation":64,"imageIndex":14},{"imageOffset":41959620,"symbol":"uv__fsevents_close","symbolLocation":1408,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}],"threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":529977489489920},{"value":0},{"value":529977489489920},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":123395},{"value":0},{"value":18446744073709551569},{"value":8408933984},{"value":0},{"value":4294967295},{"value":2},{"value":529977489489920},{"value":0},{"value":529977489489920},{"value":16198737992},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":16198737840},"sp":{"value":16198737760},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}}},{"id":6283465,"name":"CacheThread_BlockFile","threadState":{"x":[{"value":4},{"value":0},{"value":0},{"value":1254158081968},{"value":2},{"value":0},{"value":0},{"value":1873313359},{"value":0},{"value":0},{"value":1380},{"value":261614608750},{"value":2352},{"value":6283465},{"value":1254131998208},{"value":0},{"value":369},{"value":1254131262848},{"value":0},{"value":1254154994416},{"value":1254159512448},{"value":0},{"value":12297829382473034411},{"value":8000},{"value":12297829382473034410},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":4739693156},"cpsr":{"value":2684354560},"fp":{"value":16207162800},"sp":{"value":16207162656},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564658052},"far":{"value":0}},"frames":[{"imageOffset":52100,"symbol":"kevent64","symbolLocation":8,"imageIndex":19},{"imageOffset":20740708,"symbol":"cxxbridge1$box$rust_png$Reader$drop","symbolLocation":191108,"imageIndex":1},{"imageOffset":20738064,"symbol":"cxxbridge1$box$rust_png$Reader$drop","symbolLocation":188464,"imageIndex":1},{"imageOffset":23271868,"symbol":"node::PrincipalRealm::async_hooks_callback_trampoline() const","symbolLocation":103452,"imageIndex":1},{"imageOffset":24622324,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144976,"imageIndex":1},{"imageOffset":24621672,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144324,"imageIndex":1},{"imageOffset":24621356,"symbol":"node::PrincipalRealm::crypto_key_object_private_constructor() const","symbolLocation":144008,"imageIndex":1},{"imageOffset":16230736,"symbol":"node::PrincipalRealm::maybe_cache_generated_source_map() const","symbolLocation":147224,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":6289413,"name":"com.apple.NSURLConnectionLoader","threadState":{"x":[{"value":268451845},{"value":21592279046},{"value":8589934592},{"value":707359638814720},{"value":0},{"value":707359638814720},{"value":2},{"value":4294967295},{"value":0},{"value":17179869184},{"value":0},{"value":2},{"value":0},{"value":0},{"value":164695},{"value":0},{"value":18446744073709551569},{"value":8408933984},{"value":0},{"value":4294967295},{"value":2},{"value":707359638814720},{"value":0},{"value":707359638814720},{"value":6102834504},{"value":8589934592},{"value":21592279046},{"value":18446744073709550527},{"value":4412409862}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6564683816},"cpsr":{"value":0},"fp":{"value":6102834352},"sp":{"value":6102834272},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564609076},"far":{"value":0}},"frames":[{"imageOffset":3124,"symbol":"mach_msg2_trap","symbolLocation":8,"imageIndex":19},{"imageOffset":77864,"symbol":"mach_msg2_internal","symbolLocation":76,"imageIndex":19},{"imageOffset":39308,"symbol":"mach_msg_overwrite","symbolLocation":484,"imageIndex":19},{"imageOffset":4020,"symbol":"mach_msg","symbolLocation":24,"imageIndex":19},{"imageOffset":392320,"symbol":"__CFRunLoopServiceMachPort","symbolLocation":160,"imageIndex":14},{"imageOffset":386520,"symbol":"__CFRunLoopRun","symbolLocation":1188,"imageIndex":14},{"imageOffset":1165464,"symbol":"_CFRunLoopRunSpecificWithOptions","symbolLocation":532,"imageIndex":14},{"imageOffset":2403388,"symbol":"+[__CFN_CoreSchedulingSetRunnable _run:]","symbolLocation":416,"imageIndex":24},{"imageOffset":157520,"symbol":"__NSThread__start__","symbolLocation":732,"imageIndex":22},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":18},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":18}]},{"id":7049106,"frames":[],"threadState":{"x":[{"value":6102265856},{"value":109987},{"value":6101729280},{"value":0},{"value":409604},{"value":18446744073709551615},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":0},"fp":{"value":0},"sp":{"value":6102265856},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564862828},"far":{"value":0}}},{"id":7050622,"frames":[],"threadState":{"x":[{"value":6101692416},{"value":143407},{"value":6101155840},{"value":0},{"value":409604},{"value":18446744073709551615},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":0},"fp":{"value":0},"sp":{"value":6101692416},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6564862828},"far":{"value":0}}}],
  "usedImages" : [
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4365746176,
    "CFBundleShortVersionString" : "1.103.1",
    "CFBundleIdentifier" : "com.microsoft.VSCode",
    "size" : 16384,
    "uuid" : "4c4c443e-5555-3144-a1db-8d5c6fed78b5",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/MacOS\/Electron",
    "name" : "Electron",
    "CFBundleVersion" : "1.103.1"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4718952448,
    "CFBundleIdentifier" : "com.github.Electron.framework",
    "size" : 155549696,
    "uuid" : "4c4c4459-5555-3144-a1ea-b7cc7b73dc85",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Frameworks\/Electron Framework.framework\/Versions\/A\/Electron Framework",
    "name" : "Electron Framework",
    "CFBundleVersion" : "37.2.3"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4366254080,
    "CFBundleShortVersionString" : "1.0",
    "CFBundleIdentifier" : "com.github.Squirrel",
    "size" : 98304,
    "uuid" : "4c4c44c2-5555-3144-a19d-a4d47264663a",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Frameworks\/Squirrel.framework\/Versions\/A\/Squirrel",
    "name" : "Squirrel",
    "CFBundleVersion" : "1"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4367269888,
    "CFBundleShortVersionString" : "3.1.0",
    "CFBundleIdentifier" : "com.electron.reactive",
    "size" : 278528,
    "uuid" : "4c4c449b-5555-3144-a17d-45c2dd34dd5e",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Frameworks\/ReactiveObjC.framework\/Versions\/A\/ReactiveObjC",
    "name" : "ReactiveObjC",
    "CFBundleVersion" : "0.0.0"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4366434304,
    "CFBundleShortVersionString" : "1.0",
    "CFBundleIdentifier" : "org.mantle.Mantle",
    "size" : 49152,
    "uuid" : "4c4c44b0-5555-3144-a1cf-86e87e5d78b9",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Frameworks\/Mantle.framework\/Versions\/A\/Mantle",
    "name" : "Mantle",
    "CFBundleVersion" : "0.0.0"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4374183936,
    "size" : 1687552,
    "uuid" : "4c4c4418-5555-3144-a1e8-df882823b6b5",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Frameworks\/Electron Framework.framework\/Versions\/A\/Libraries\/libffmpeg.dylib",
    "name" : "libffmpeg.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 4379082752,
    "size" : 49152,
    "uuid" : "580e4b29-8304-342d-a21c-2a869364dc35",
    "path" : "\/usr\/lib\/libobjc-trampolines.dylib",
    "name" : "libobjc-trampolines.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 5556862976,
    "CFBundleShortVersionString" : "340.26.1",
    "CFBundleIdentifier" : "com.apple.AGXMetalG16G-B0",
    "size" : 8536064,
    "uuid" : "3236991d-b08b-3d98-b928-10238b9fcd37",
    "path" : "\/System\/Library\/Extensions\/AGXMetalG16G_B0.bundle\/Contents\/MacOS\/AGXMetalG16G_B0",
    "name" : "AGXMetalG16G_B0",
    "CFBundleVersion" : "340.26.1"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 4386586624,
    "CFBundleShortVersionString" : "3.0",
    "CFBundleIdentifier" : "com.apple.security.csparser",
    "size" : 131072,
    "uuid" : "68d38a93-ae93-39b1-a636-19b0f3369545",
    "path" : "\/System\/Library\/Frameworks\/Security.framework\/Versions\/A\/PlugIns\/csparser.bundle\/Contents\/MacOS\/csparser",
    "name" : "csparser",
    "CFBundleVersion" : "61901.0.87.0.1"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4386832384,
    "size" : 49152,
    "uuid" : "f2bee164-0956-329c-acf2-7dcb7e69965f",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Resources\/app\/node_modules\/@vscode\/policy-watcher\/build\/Release\/vscode-policy-watcher.node",
    "name" : "vscode-policy-watcher.node"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4698423296,
    "size" : 245760,
    "uuid" : "634649a7-7523-3506-8075-0aa8f8a344ca",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Resources\/app\/node_modules\/@vscode\/spdlog\/build\/Release\/spdlog.node",
    "name" : "spdlog.node"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4708663296,
    "size" : 1687552,
    "uuid" : "200a8d95-9f94-3463-95bd-64b04cd883b8",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Resources\/app\/node_modules\/@vscode\/sqlite3\/build\/Release\/vscode-sqlite3.node",
    "name" : "vscode-sqlite3.node"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4704927744,
    "size" : 16384,
    "uuid" : "81fbfda6-ae68-342a-b0a7-3288461e02a1",
    "path" : "\/Applications\/Visual Studio Code.app\/Contents\/Resources\/app\/node_modules\/native-keymap\/build\/Release\/keymapping.node",
    "name" : "keymapping.node"
  },
  {
    "size" : 0,
    "source" : "A",
    "base" : 0,
    "uuid" : "00000000-0000-0000-0000-000000000000"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6565142528,
    "CFBundleShortVersionString" : "6.9",
    "CFBundleIdentifier" : "com.apple.CoreFoundation",
    "size" : 5558144,
    "uuid" : "abc6831d-f275-379e-a645-84102778d2a3",
    "path" : "\/System\/Library\/Frameworks\/CoreFoundation.framework\/Versions\/A\/CoreFoundation",
    "name" : "CoreFoundation",
    "CFBundleVersion" : "4040.1"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6776389632,
    "CFBundleShortVersionString" : "2.1.1",
    "CFBundleIdentifier" : "com.apple.HIToolbox",
    "size" : 3155680,
    "uuid" : "d25cb3ee-608d-3934-bc87-b97c714e332c",
    "path" : "\/System\/Library\/Frameworks\/Carbon.framework\/Versions\/A\/Frameworks\/HIToolbox.framework\/Versions\/A\/HIToolbox",
    "name" : "HIToolbox"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6636597248,
    "CFBundleShortVersionString" : "6.9",
    "CFBundleIdentifier" : "com.apple.AppKit",
    "size" : 24085856,
    "uuid" : "80f05729-fb1b-34d0-b4f3-052ee9037b03",
    "path" : "\/System\/Library\/Frameworks\/AppKit.framework\/Versions\/C\/AppKit",
    "name" : "AppKit",
    "CFBundleVersion" : "2685.10.100"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6560927744,
    "size" : 648932,
    "uuid" : "09b89563-df74-3b6c-a915-241c4752e5b4",
    "path" : "\/usr\/lib\/dyld",
    "name" : "dyld"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6564855808,
    "size" : 51816,
    "uuid" : "1db1f8c5-d5d8-3485-b5e2-c5f75a9d689e",
    "path" : "\/usr\/lib\/system\/libsystem_pthread.dylib",
    "name" : "libsystem_pthread.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6564605952,
    "size" : 246880,
    "uuid" : "f422da94-53ac-36ae-a166-82e4c905ecd2",
    "path" : "\/usr\/lib\/system\/libsystem_kernel.dylib",
    "name" : "libsystem_kernel.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6564909056,
    "size" : 32864,
    "uuid" : "6d8d83b9-f558-376b-b0b5-53fa7d7d5731",
    "path" : "\/usr\/lib\/system\/libsystem_platform.dylib",
    "name" : "libsystem_platform.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6563057664,
    "size" : 290400,
    "uuid" : "553d7026-4684-3483-8faf-eee6ffa9a0a6",
    "path" : "\/usr\/lib\/system\/libdispatch.dylib",
    "name" : "libdispatch.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6590566400,
    "CFBundleShortVersionString" : "6.9",
    "CFBundleIdentifier" : "com.apple.Foundation",
    "size" : 16299488,
    "uuid" : "b7f5a950-39e3-3616-b895-f260036c9590",
    "path" : "\/System\/Library\/Frameworks\/Foundation.framework\/Versions\/C\/Foundation",
    "name" : "Foundation",
    "CFBundleVersion" : "4040.1"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6560727040,
    "size" : 199345,
    "uuid" : "be17cf9e-d613-3012-b515-72181b2f008e",
    "path" : "\/usr\/lib\/system\/libdyld.dylib",
    "name" : "libdyld.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6668525568,
    "CFBundleShortVersionString" : "1.0",
    "CFBundleIdentifier" : "com.apple.CFNetwork",
    "size" : 3906176,
    "uuid" : "10bc915e-16e7-3b21-8e1b-3295a051249f",
    "path" : "\/System\/Library\/Frameworks\/CFNetwork.framework\/Versions\/A\/CFNetwork",
    "name" : "CFNetwork",
    "CFBundleVersion" : "3860.100.1"
  }
],
  "sharedCache" : {
  "base" : 6559858688,
  "size" : 5552390144,
  "uuid" : "2a12dabc-5478-3d88-893e-38e38cf4f458"
},
  "legacyInfo" : {
  "threadTriggered" : {
    "name" : "CrBrowserMain"
  }
},
  "logWritingSignature" : "43acd69aa1e04c05be234bb72b30d5404722ba72",
  "trialInfo" : {
  "rollouts" : [
    {
      "rolloutId" : "60f8ddccefea4203d95cbeef",
      "factorPackIds" : [

      ],
      "deploymentId" : 250000033
    },
    {
      "rolloutId" : "6761d0c9df60af01adb250fb",
      "factorPackIds" : [

      ],
      "deploymentId" : 250000008
    }
  ],
  "experiments" : [

  ]
}
}

Model: Mac16,13, BootROM 13822.1.2, proc 10:4:6 processors, 16 GB, SMC 
Graphics: Apple M4, Apple M4, Built-In
Display: Color LCD, spdisplays_2880x1864Retina, Main, MirrorOff, Online
Memory Module: LPDDR5, Micron
AirPort: spairport_wireless_card_type_wifi (0x14E4, 0x4388), wl0: Jul 23 2025 02:15:41 version 23.41.4.0.41.51.197 FWID 01-94e410f5
IO80211_driverkit-1525.88 "IO80211_driverkit-1525.88" Aug  6 2025 22:24:44
AirPort: 
Bluetooth: Version (null), 0 services, 0 devices, 0 incoming serial ports
Network Service: Ethernet Adapter (en3), Ethernet, en3
Network Service: Ethernet Adapter (en4), Ethernet, en4
Network Service: Wi-Fi, AirPort, en0
Thunderbolt Bus: MacBook Air, Apple Inc.
Thunderbolt Bus: MacBook Air, Apple Inc.
