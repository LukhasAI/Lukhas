-------------------------------------
Translated Report (Full Report Below)
-------------------------------------
Process:             Python [49036]
Path:                /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
Identifier:          com.apple.python3
Version:             3.9.6 (3.9.6)
Build Info:          python3-141000000500005~678
Code Type:           ARM-64 (Native)
Role:                Unspecified
Parent Process:      Exited process [49034]
Coalition:           com.microsoft.VSCode [24052]
Responsible Process: Electron [22668]
User ID:             501

Date/Time:           2025-10-12 03:07:19.6460 +0100
Launch Time:         2025-10-12 03:07:17.1661 +0100
Hardware Model:      Mac16,13
OS Version:          macOS 26.1 (25B5057f)
Release Type:        User

Crash Reporter Key:  4E207357-19A3-A70F-DAD5-7940E32325FE
Incident Identifier: D6F16153-9402-4999-92B7-7D4785799419

Sleep/Wake UUID:       A69A2551-0142-4426-AA55-C245322EC7B3

Time Awake Since Boot: 240000 seconds
Time Since Wake:       163 seconds

System Integrity Protection: enabled

Triggered by Thread: 0, Dispatch Queue: com.apple.main-thread

Exception Type:    EXC_CRASH (SIGABRT)
Exception Codes:   0x0000000000000000, 0x0000000000000000

Termination Reason:  Namespace SIGNAL, Code 6, Abort trap: 6
Terminating Process: Python [49036]


Application Specific Information:
abort() called


Thread 0 Crashed::  Dispatch queue: com.apple.main-thread
0    libsystem_kernel.dylib        	       0x19d4675b0 __pthread_kill + 8
1    libsystem_pthread.dylib       	       0x19d4a1888 pthread_kill + 296
2    libsystem_c.dylib             	       0x19d3a6850 abort + 124
3    Python3                       	       0x10114d610 0x101000000 + 1365520
4    Python3                       	       0x10114d3d4 0x101000000 + 1364948
5    Python3                       	       0x10114d170 _Py_FatalErrorFunc + 40
6    Python3                       	       0x10110f928 _Py_CheckRecursiveCall + 72
7    Python3                       	       0x10104a704 0x101000000 + 304900
8    Python3                       	       0x101042c00 PyObject_VectorcallMethod + 144
9    Python3                       	       0x10114cc74 0x101000000 + 1363060
10   Python3                       	       0x10114d3c8 0x101000000 + 1364936
11   Python3                       	       0x10114d170 _Py_FatalErrorFunc + 40
12   Python3                       	       0x101114d44 _PyEval_EvalFrameDefault + 21164
13   Python3                       	       0x101117134 0x101000000 + 1143092
14   Python3                       	       0x101041bd8 _PyFunction_Vectorcall + 228
15   Python3                       	       0x101042ef0 0x101000000 + 274160
16   Python3                       	       0x101043070 _PyObject_CallMethodIdObjArgs + 112
17   Python3                       	       0x10113b1ec PyImport_ImportModuleLevelObject + 1500
18   Python3                       	       0x10110b4b4 0x101000000 + 1094836
19   Python3                       	       0x1010856d0 0x101000000 + 546512
20   Python3                       	       0x10104136c _PyObject_MakeTpCall + 356
21   Python3                       	       0x10111643c 0x101000000 + 1139772
22   Python3                       	       0x101110da8 _PyEval_EvalFrameDefault + 4880
23   Python3                       	       0x101117134 0x101000000 + 1143092
24   Python3                       	       0x101041bd8 _PyFunction_Vectorcall + 228
25   Python3                       	       0x1011163dc 0x101000000 + 1139676
-------- RECURSION LEVEL 1026
26   Python3                       	       0x101111cb0 _PyEval_EvalFrameDefault + 8728
27   Python3                       	       0x101117134 0x101000000 + 1143092
28   Python3                       	       0x101041bd8 _PyFunction_Vectorcall + 228
29   Python3                       	       0x101043e94 0x101000000 + 278164
30   Python3                       	       0x1011163dc 0x101000000 + 1139676
-------- RECURSION LEVEL 1025
31   Python3                       	       0x10111256c _PyEval_EvalFrameDefault + 10964
32   Python3                       	       0x101117134 0x101000000 + 1143092
33   Python3                       	       0x101041bd8 _PyFunction_Vectorcall + 228
34   Python3                       	       0x1011163dc 0x101000000 + 1139676
-------- RECURSION LEVEL 1024
--------
-------- ELIDED 1020 LEVELS OF RECURSION THROUGH 0x1011163dc 0x101000000 + 1139676
--------
4500 Python3                       	       0x10111256c _PyEval_EvalFrameDefault + 10964
4501 Python3                       	       0x101041d6c 0x101000000 + 269676
4502 Python3                       	       0x1011163dc 0x101000000 + 1139676
-------- RECURSION LEVEL 3
4503 Python3                       	       0x101111cb0 _PyEval_EvalFrameDefault + 8728
4504 Python3                       	       0x101117134 0x101000000 + 1143092
4505 Python3                       	       0x10110f9d0 PyEval_EvalCode + 80
4506 Python3                       	       0x10110c33c 0x101000000 + 1098556
4507 Python3                       	       0x101084cec 0x101000000 + 543980
4508 Python3                       	       0x1011163dc 0x101000000 + 1139676
-------- RECURSION LEVEL 2
4509 Python3                       	       0x10111256c _PyEval_EvalFrameDefault + 10964
4510 Python3                       	       0x101117134 0x101000000 + 1143092
4511 Python3                       	       0x101041bd8 _PyFunction_Vectorcall + 228
4512 Python3                       	       0x1011163dc 0x101000000 + 1139676
-------- RECURSION LEVEL 1
4513 Python3                       	       0x10111256c _PyEval_EvalFrameDefault + 10964
4514 Python3                       	       0x101117134 0x101000000 + 1143092
4515 Python3                       	       0x101041bd8 _PyFunction_Vectorcall + 228
4516 Python3                       	       0x10116f234 0x101000000 + 1503796
4517 Python3                       	       0x10116ea9c Py_RunMain + 824
4518 Python3                       	       0x10116f0c0 0x101000000 + 1503424
4519 Python3                       	       0x10116f160 Py_BytesMain + 40
4520 dyld                          	       0x19d0d9d54 start + 7184

Thread 1:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 2:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 3:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 4:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 5:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 6:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 7:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 8:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 9:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas64_.0.dylib        	       0x108990394 blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 10:

Thread 11:

Thread 12:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 13:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 14:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 15:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 16:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 17:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 18:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 19:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8

Thread 20:
0   libsystem_kernel.dylib        	       0x19d4624f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d4a20dc _pthread_cond_wait + 984
2   libopenblas.0.dylib           	       0x12ec4593c blas_thread_server + 360
3   libsystem_pthread.dylib       	       0x19d4a1c08 _pthread_start + 136
4   libsystem_pthread.dylib       	       0x19d49cba8 thread_start + 8


Thread 0 crashed with ARM Thread State (64-bit):
    x0: 0x0000000000000000   x1: 0x0000000000000000   x2: 0x0000000000000000   x3: 0x0000000000000000
    x4: 0x00000000ffffffff   x5: 0x0000000000000068   x6: 0x0000000000000068   x7: 0x000000016f42b478
    x8: 0x82b655b9703a21e1   x9: 0x82b655bb79d9fce1  x10: 0x0000000000000002  x11: 0x0000010000000000
   x12: 0x00000000fffffffd  x13: 0x0000000000000000  x14: 0x0000000000000000  x15: 0x0000000000000000
   x16: 0x0000000000000148  x17: 0x000000020b4610d8  x18: 0x0000000000000000  x19: 0x0000000000000006
   x20: 0x0000000000000103  x21: 0x0000000209e3dde0  x22: 0x0000000209e45410  x23: 0x00000001011e350e
   x24: 0x0000000000000001  x25: 0x0000000000000003  x26: 0x000000010130be50  x27: 0x000000016f42b460
   x28: 0x000000010130be50   fp: 0x000000016f42af20   lr: 0x000000019d4a1888
    sp: 0x000000016f42af00   pc: 0x000000019d4675b0 cpsr: 0x40000000
   far: 0x0000000000000000  esr: 0x56000080 (Syscall)

Binary Images:
       0x100904000 -        0x100907fff com.apple.python3 (3.9.6) <6eb25e2c-229f-3707-b5bb-7c6ff0239635> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
       0x101000000 -        0x101263fff com.apple.python3 (3.9.6) <1f7e9bdf-34d6-33d3-81a7-24c47e0d5992> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Python3
       0x100fd8000 -        0x100fdffff _heapq.cpython-39-darwin.so (*) <5ab95036-7a84-3805-a505-b552447b5184> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_heapq.cpython-39-darwin.so
       0x1059f8000 -        0x1059fbfff _opcode.cpython-39-darwin.so (*) <7bf4e0ff-7cbb-3cd1-a766-0c409645a739> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_opcode.cpython-39-darwin.so
       0x105a8c000 -        0x105a8ffff _bisect.cpython-39-darwin.so (*) <09195126-ae27-364b-bf8f-53eb189b9870> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_bisect.cpython-39-darwin.so
       0x105aa0000 -        0x105aa7fff zlib.cpython-39-darwin.so (*) <6d627f31-aa64-3572-a55f-9ae208481c5e> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/zlib.cpython-39-darwin.so
       0x105af8000 -        0x105afbfff _bz2.cpython-39-darwin.so (*) <6105c19e-4d4e-32b8-8843-e91223dad09d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_bz2.cpython-39-darwin.so
       0x105b0c000 -        0x105b13fff _lzma.cpython-39-darwin.so (*) <6e3d646a-7f92-3cde-82d7-0089e18f1a12> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_lzma.cpython-39-darwin.so
       0x105b24000 -        0x105b27fff grp.cpython-39-darwin.so (*) <5bee5e54-876a-3b18-b11e-a7ef4e8fff33> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/grp.cpython-39-darwin.so
       0x105b78000 -        0x105b7ffff _csv.cpython-39-darwin.so (*) <22bd65a7-4756-3cfa-aac1-d10d882cb42a> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_csv.cpython-39-darwin.so
       0x105b90000 -        0x105b97fff binascii.cpython-39-darwin.so (*) <9918a271-0a03-32f3-9756-be0e71ff616d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/binascii.cpython-39-darwin.so
       0x105ba8000 -        0x105baffff _struct.cpython-39-darwin.so (*) <75342080-6784-350b-812d-206d3b221cdb> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_struct.cpython-39-darwin.so
       0x105d00000 -        0x105d03fff _uuid.cpython-39-darwin.so (*) <99cfcbb6-fd85-3797-a698-6db9cc7b8355> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_uuid.cpython-39-darwin.so
       0x105f50000 -        0x10605ffff unicodedata.cpython-39-darwin.so (*) <87ddbc0f-f489-3d19-b4ae-0062421cddc9> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/unicodedata.cpython-39-darwin.so
       0x1009b8000 -        0x1009c7fff _socket.cpython-39-darwin.so (*) <d399388c-9a55-3b85-a653-0f586e3d6767> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_socket.cpython-39-darwin.so
       0x1060b0000 -        0x1060bbfff math.cpython-39-darwin.so (*) <19157ce8-1e08-3232-b29f-1ef4f809619f> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/math.cpython-39-darwin.so
       0x105f14000 -        0x105f27fff _datetime.cpython-39-darwin.so (*) <463cfec4-d1dd-3f01-a398-971f300f1b23> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_datetime.cpython-39-darwin.so
       0x105f38000 -        0x105f3ffff _json.cpython-39-darwin.so (*) <c3a948a4-59e1-3d7b-968e-8e3094728d6d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_json.cpython-39-darwin.so
       0x1009d8000 -        0x1009dbfff _random.cpython-39-darwin.so (*) <aee77fda-eaa9-35a6-9eb4-a85148a27ed4> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_random.cpython-39-darwin.so
       0x106138000 -        0x10613ffff _sha512.cpython-39-darwin.so (*) <ff1ac68a-03fb-33b8-80e9-70687d58d21d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_sha512.cpython-39-darwin.so
       0x106210000 -        0x106213fff _posixsubprocess.cpython-39-darwin.so (*) <21025db5-0dba-3a36-a038-3a9f649cd3d2> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_posixsubprocess.cpython-39-darwin.so
       0x106224000 -        0x10622bfff select.cpython-39-darwin.so (*) <96082726-10ef-3d3a-a53f-2b60f155317d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/select.cpython-39-darwin.so
       0x106320000 -        0x106363fff _decimal.cpython-39-darwin.so (*) <8c71d159-05e1-347d-b8c1-84755996ffc2> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_decimal.cpython-39-darwin.so
       0x10610c000 -        0x106117fff _elementtree.cpython-39-darwin.so (*) <05f0dbce-3794-31c9-aca5-04f56606f7ec> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_elementtree.cpython-39-darwin.so
       0x1064e8000 -        0x10650ffff pyexpat.cpython-39-darwin.so (*) <994f7633-f40a-39bb-9867-800e21b4124c> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/pyexpat.cpython-39-darwin.so
       0x1062fc000 -        0x106307fff array.cpython-39-darwin.so (*) <3b0cc2b7-b4c5-3886-9d09-d843de60a266> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/array.cpython-39-darwin.so
       0x1064b4000 -        0x1064cbfff _ssl.cpython-39-darwin.so (*) <0f89f536-3122-3986-aaae-90d5d41f6500> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_ssl.cpython-39-darwin.so
       0x106684000 -        0x106687fff _contextvars.cpython-39-darwin.so (*) <8f323497-2e9d-342a-b2e1-345685a4af6d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_contextvars.cpython-39-darwin.so
       0x106660000 -        0x10666bfff _asyncio.cpython-39-darwin.so (*) <c8f017a4-9e91-37af-bded-65d7a78fde96> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_asyncio.cpython-39-darwin.so
       0x1068c4000 -        0x1068cbfff _hashlib.cpython-39-darwin.so (*) <679e7231-a59a-3cad-90cf-241a5e2fdb8f> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_hashlib.cpython-39-darwin.so
       0x106898000 -        0x1068a3fff _blake2.cpython-39-darwin.so (*) <476639d2-b0ab-3f91-a682-dd890ee9bca9> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_blake2.cpython-39-darwin.so
       0x10691c000 -        0x10692bfff _sha3.cpython-39-darwin.so (*) <6b89b147-f807-32a9-88ab-ce2c09511e3d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_sha3.cpython-39-darwin.so
       0x106960000 -        0x106963fff _queue.cpython-39-darwin.so (*) <d7f10ed3-5c76-3423-9cd7-c20343a58e2c> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_queue.cpython-39-darwin.so
       0x10693c000 -        0x106943fff readline.cpython-39-darwin.so (*) <969c04d4-ce82-388f-8fee-f84b71ef893b> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/readline.cpython-39-darwin.so
       0x106b30000 -        0x106b3bfff _sqlite3.cpython-39-darwin.so (*) <fe9ef126-b321-3315-b3fa-007dd1d2f62d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_sqlite3.cpython-39-darwin.so
       0x106edc000 -        0x107157fff _multiarray_umath.cpython-39-darwin.so (*) <1a279e5d-158d-356b-9729-587af84e2c79> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/core/_multiarray_umath.cpython-39-darwin.so
       0x108828000 -        0x109bfffff libopenblas64_.0.dylib (*) <3dd132fc-be72-33cc-baf0-4c7df2669307> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/.dylibs/libopenblas64_.0.dylib
       0x107288000 -        0x1075e3fff libgfortran.5.dylib (*) <dd0e012a-b6de-31b1-a28e-260c7b51e595> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/.dylibs/libgfortran.5.dylib
       0x106bac000 -        0x106bf7fff libquadmath.0.dylib (*) <6d39d54b-d80e-3218-a095-b81ad0b3be90> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/.dylibs/libquadmath.0.dylib
       0x106b50000 -        0x106b5ffff libgcc_s.1.1.dylib (*) <d9875303-8f38-33d9-a0d3-ab0adff3b915> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/.dylibs/libgcc_s.1.1.dylib
       0x106af4000 -        0x106b0bfff _pickle.cpython-39-darwin.so (*) <587afe91-9cab-31e2-96fd-e264bbdb9d6d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_pickle.cpython-39-darwin.so
       0x106dc8000 -        0x106dd7fff _multiarray_tests.cpython-39-darwin.so (*) <60c7a0dd-16b9-31dc-bafc-c3183b3c0ab8> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/core/_multiarray_tests.cpython-39-darwin.so
       0x106b74000 -        0x106b87fff _ctypes.cpython-39-darwin.so (*) <1f89dcab-1d9f-3949-8233-5a0aeb436d27> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_ctypes.cpython-39-darwin.so
       0x106ea4000 -        0x106ebbfff _umath_linalg.cpython-39-darwin.so (*) <b7a5137f-a42d-33d9-97a5-01f49eac03e2> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/linalg/_umath_linalg.cpython-39-darwin.so
       0x1076d0000 -        0x1076dffff _pocketfft_internal.cpython-39-darwin.so (*) <d4f1aa1b-1d5b-31c0-914b-f7573e69b12c> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/fft/_pocketfft_internal.cpython-39-darwin.so
       0x1077e0000 -        0x10784ffff mtrand.cpython-39-darwin.so (*) <0f6b1dcc-ce9c-3f80-bfd1-3f4dcd96ae39> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/mtrand.cpython-39-darwin.so
       0x10772c000 -        0x10774bfff bit_generator.cpython-39-darwin.so (*) <a15db2c2-1645-3e76-8f83-8c56aeb363f2> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/bit_generator.cpython-39-darwin.so
       0x107898000 -        0x1078cbfff _common.cpython-39-darwin.so (*) <ae6c2a49-3ede-3b9d-b195-7f461dc3318b> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/_common.cpython-39-darwin.so
       0x1078dc000 -        0x107927fff _bounded_integers.cpython-39-darwin.so (*) <0f54435f-099c-3111-b308-7824f4906be6> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/_bounded_integers.cpython-39-darwin.so
       0x107760000 -        0x10776ffff _mt19937.cpython-39-darwin.so (*) <82b876ee-db08-3781-b69b-ab08d1fa32e6> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/_mt19937.cpython-39-darwin.so
       0x107780000 -        0x10778ffff _philox.cpython-39-darwin.so (*) <6cb4e48e-045e-3c48-bb3c-a501e1abb0ad> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/_philox.cpython-39-darwin.so
       0x1077a0000 -        0x1077affff _pcg64.cpython-39-darwin.so (*) <0108ef0a-c7f5-3124-b3fa-1803b488f8fc> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/_pcg64.cpython-39-darwin.so
       0x106e88000 -        0x106e8ffff _sfc64.cpython-39-darwin.so (*) <fb47f6b2-3649-33c6-91ed-ce6f7d76ec93> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/_sfc64.cpython-39-darwin.so
       0x107a10000 -        0x107a9bfff _generator.cpython-39-darwin.so (*) <a8e6f7df-e5a5-3f57-ab85-60318792ee83> /Users/USER/Library/Python/3.9/lib/python/site-packages/numpy/random/_generator.cpython-39-darwin.so
       0x107f6c000 -        0x10826bfff lib.cpython-39-darwin.so (*) <e25299f6-7128-354b-b033-f8610a240ad9> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/lib.cpython-39-darwin.so
       0x107d40000 -        0x107e5bfff libarrow_python.2000.dylib (*) <9116691d-b326-32a0-93f6-c0335c8f07e2> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/libarrow_python.2000.dylib
       0x11ddcc000 -        0x11df57fff libarrow_substrait.2000.dylib (*) <f7d19036-3b8a-3d39-812f-272a95f5bf24> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/libarrow_substrait.2000.dylib
       0x11e0bc000 -        0x11e1effff libarrow_dataset.2000.dylib (*) <625921f5-6c1a-3a3f-a7de-d0a3d5c028af> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/libarrow_dataset.2000.dylib
       0x11e344000 -        0x11e56ffff libparquet.2000.dylib (*) <aec6ca22-a37d-3d14-bba3-405331f24a63> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/libparquet.2000.dylib
       0x108590000 -        0x1086abfff libarrow_acero.2000.dylib (*) <5fe3208d-25e2-388d-b810-b74357848ea4> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/libarrow_acero.2000.dylib
       0x121b28000 -        0x123dc7fff libarrow.2000.dylib (*) <11bde922-a023-36f1-8807-f03d74e19f0d> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/libarrow.2000.dylib
       0x1077c0000 -        0x1077c7fff pandas_parser.cpython-39-darwin.so (*) <6586461d-6253-3202-9e53-68ee6efbf945> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/pandas_parser.cpython-39-darwin.so
       0x1079fc000 -        0x107a03fff pandas_datetime.cpython-39-darwin.so (*) <6e002f61-21d7-3bf4-aff8-4bc8b7d685ab> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/pandas_datetime.cpython-39-darwin.so
       0x11e720000 -        0x11e7fbfff interval.cpython-39-darwin.so (*) <1f353248-ea36-3092-a0a7-6e5c9c790559> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/interval.cpython-39-darwin.so
       0x11e824000 -        0x11e99bfff hashtable.cpython-39-darwin.so (*) <6d81e7a7-a51d-3455-9141-5fd00ddfab1b> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/hashtable.cpython-39-darwin.so
       0x107f1c000 -        0x107f3ffff missing.cpython-39-darwin.so (*) <5dd857ed-e3d1-37cb-9766-499b7b952893> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/missing.cpython-39-darwin.so
       0x1083a4000 -        0x1083c3fff dtypes.cpython-39-darwin.so (*) <b7f2fc9f-4552-363e-962b-cc93b299198f> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/dtypes.cpython-39-darwin.so
       0x107d24000 -        0x107d2ffff ccalendar.cpython-39-darwin.so (*) <1fc24201-40d8-3336-ba1a-777d07bb5763> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/ccalendar.cpython-39-darwin.so
       0x108400000 -        0x108417fff np_datetime.cpython-39-darwin.so (*) <5eabb00b-ce23-3e4b-9b34-90367333cb70> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/np_datetime.cpython-39-darwin.so
       0x10846c000 -        0x10849bfff conversion.cpython-39-darwin.so (*) <713cf5c9-d629-3381-9360-c69f54853479> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/conversion.cpython-39-darwin.so
       0x107f50000 -        0x107f5bfff base.cpython-39-darwin.so (*) <a74c8fcd-6e06-3594-a68d-1d6897686154> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/base.cpython-39-darwin.so
       0x11e9dc000 -        0x11ea8ffff offsets.cpython-39-darwin.so (*) <e2b3c951-a016-3557-ae04-9d20d2044667> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/offsets.cpython-39-darwin.so
       0x10879c000 -        0x108807fff timestamps.cpython-39-darwin.so (*) <01f7a3b7-81e0-3de2-b1a7-240c4fc6d447> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/timestamps.cpython-39-darwin.so
       0x1084f0000 -        0x10851bfff nattype.cpython-39-darwin.so (*) <921014dd-1da4-3928-bddb-37c06d98e9e3> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/nattype.cpython-39-darwin.so
       0x11eb38000 -        0x11eb9bfff timedeltas.cpython-39-darwin.so (*) <93b2c0ab-caae-34e6-a58a-9b5cd76269a8> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/timedeltas.cpython-39-darwin.so
       0x108530000 -        0x10855bfff timezones.cpython-39-darwin.so (*) <852a04e8-c0fa-3f5a-9729-d1cc62d2ef22> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/timezones.cpython-39-darwin.so
       0x106e70000 -        0x106e77fff _zoneinfo.cpython-39-darwin.so (*) <d022a2fc-a33f-3393-9240-db6d3a356662> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_zoneinfo.cpython-39-darwin.so
       0x11ebb8000 -        0x11ebebfff fields.cpython-39-darwin.so (*) <c10e79d3-e0b3-3117-bf2a-2103b8b1cbe2> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/fields.cpython-39-darwin.so
       0x11ec44000 -        0x11ec73fff tzconversion.cpython-39-darwin.so (*) <d03b1ec3-a5ab-38ba-8ab2-73165660be89> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/tzconversion.cpython-39-darwin.so
       0x108570000 -        0x10857bfff properties.cpython-39-darwin.so (*) <debdd017-0dc0-3ea4-be2a-85d3f47e3503> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/properties.cpython-39-darwin.so
       0x11ece0000 -        0x11ed23fff parsing.cpython-39-darwin.so (*) <0890f306-10c2-3756-9d16-0b513497e587> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/parsing.cpython-39-darwin.so
       0x11ed38000 -        0x11ed73fff strptime.cpython-39-darwin.so (*) <7d35b498-af4b-398b-bf35-42fbaa737609> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/strptime.cpython-39-darwin.so
       0x11edf4000 -        0x11ee47fff period.cpython-39-darwin.so (*) <bd8bf755-f604-3560-b01b-9613b730f6ee> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/period.cpython-39-darwin.so
       0x11ec88000 -        0x11ecabfff vectorized.cpython-39-darwin.so (*) <93e5d267-95c2-369e-a903-d0afeab027f2> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslibs/vectorized.cpython-39-darwin.so
       0x1083ec000 -        0x1083f3fff ops_dispatch.cpython-39-darwin.so (*) <1c9746bf-6f0a-3479-bca4-5131245fbb6e> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/ops_dispatch.cpython-39-darwin.so
       0x11efec000 -        0x11f157fff algos.cpython-39-darwin.so (*) <f5e9a071-2b02-3387-86db-a4bb874c0e5b> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/algos.cpython-39-darwin.so
       0x11ef0c000 -        0x11ef97fff lib.cpython-39-darwin.so (*) <1f62c85d-ae06-336d-9d76-8b7e30e252cf> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/lib.cpython-39-darwin.so
       0x11f2e8000 -        0x11f397fff _compute.cpython-39-darwin.so (*) <9d0ab309-ab51-3d71-90b8-fa64384e232c> /Users/USER/Library/Python/3.9/lib/python/site-packages/pyarrow/_compute.cpython-39-darwin.so
       0x11f4d4000 -        0x11f4fbfff ops.cpython-39-darwin.so (*) <4955067c-aa39-368a-8212-7157e72114ad> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/ops.cpython-39-darwin.so
       0x11efb8000 -        0x11efd7fff hashing.cpython-39-darwin.so (*) <de2b52db-24d8-3d1b-a076-b5d5a9276f4e> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/hashing.cpython-39-darwin.so
       0x11ecbc000 -        0x11eccffff arrays.cpython-39-darwin.so (*) <9453eadc-14f2-363b-9eb7-cc9adced3496> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/arrays.cpython-39-darwin.so
       0x11f694000 -        0x11f6c7fff tslib.cpython-39-darwin.so (*) <3560928e-a6e1-3761-9271-79490d8230e2> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/tslib.cpython-39-darwin.so
       0x11f7c8000 -        0x11f85ffff sparse.cpython-39-darwin.so (*) <5bf4eebd-eb45-3e2f-87c5-b8dd0ac7406d> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/sparse.cpython-39-darwin.so
       0x11f8cc000 -        0x11f90bfff internals.cpython-39-darwin.so (*) <6b992add-fd46-35a9-95ef-459f1a4882b2> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/internals.cpython-39-darwin.so
       0x11eb14000 -        0x11eb1ffff indexing.cpython-39-darwin.so (*) <6b4d37fc-86b4-3781-af29-2936684d6132> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/indexing.cpython-39-darwin.so
       0x11faa0000 -        0x11fb3bfff index.cpython-39-darwin.so (*) <0811a5d5-c591-30ef-9e12-6195f5926407> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/index.cpython-39-darwin.so
       0x11fa18000 -        0x11fa3bfff writers.cpython-39-darwin.so (*) <5d3b106a-5077-346d-9436-674cf49356a1> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/writers.cpython-39-darwin.so
       0x11fc5c000 -        0x11fd3ffff join.cpython-39-darwin.so (*) <9e9150c3-fb9c-345b-b464-808e8b46fa0e> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/join.cpython-39-darwin.so
       0x11eafc000 -        0x11eb03fff mmap.cpython-39-darwin.so (*) <82e15567-d8ad-38e1-bcd2-e48993feff49> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/mmap.cpython-39-darwin.so
       0x11feb0000 -        0x11feeffff aggregations.cpython-39-darwin.so (*) <96b7ce8c-c4cd-3085-a293-c7a0502b3b42> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/window/aggregations.cpython-39-darwin.so
       0x11fc20000 -        0x11fc3ffff indexers.cpython-39-darwin.so (*) <5b1a7ba9-7bd4-3a5f-94a8-6b837b6b9d37> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/window/indexers.cpython-39-darwin.so
       0x11ffc8000 -        0x11fff7fff reshape.cpython-39-darwin.so (*) <f8c0c784-acdd-3532-b001-4ba195a7ba41> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/reshape.cpython-39-darwin.so
       0x120238000 -        0x1203fffff groupby.cpython-39-darwin.so (*) <881035ae-b8f4-34cb-ac75-733a761868af> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/groupby.cpython-39-darwin.so
       0x11eee0000 -        0x11eeebfff json.cpython-39-darwin.so (*) <3f17644c-ce59-374f-bffe-5771eb561ec9> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/json.cpython-39-darwin.so
       0x120428000 -        0x12047ffff parsers.cpython-39-darwin.so (*) <804e14ec-29f1-3561-b97f-f2eaed4721e9> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/parsers.cpython-39-darwin.so
       0x11f2c0000 -        0x11f2d3fff testing.cpython-39-darwin.so (*) <9c6d2c65-bea7-3494-a668-9c457bd4e76e> /Users/USER/Library/Python/3.9/lib/python/site-packages/pandas/_libs/testing.cpython-39-darwin.so
       0x11f79c000 -        0x11f7a3fff cmath.cpython-39-darwin.so (*) <1b9ddaf1-6d95-3893-99aa-3f9f015083c7> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/cmath.cpython-39-darwin.so
       0x1083d8000 -        0x1083dbfff _scproxy.cpython-39-darwin.so (*) <25a6e224-d711-363c-8e28-ba41d4f0439c> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_scproxy.cpython-39-darwin.so
       0x11eef8000 -        0x11eefbfff resource.cpython-39-darwin.so (*) <8a749554-2a89-3445-bc29-08a20a0ca27c> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/resource.cpython-39-darwin.so
       0x120c74000 -        0x121007fff _pydantic_core.cpython-39-darwin.so (*) <8a370734-3093-332f-8582-b45fd9efee3f> /Users/USER/Library/Python/3.9/lib/python/site-packages/pydantic_core/_pydantic_core.cpython-39-darwin.so
       0x11f7b4000 -        0x11f7b7fff termios.cpython-39-darwin.so (*) <7586df51-b08f-3909-83e9-14ff3629f3ed> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/termios.cpython-39-darwin.so
       0x11f8b8000 -        0x11f8bbfff _statistics.cpython-39-darwin.so (*) <03f76456-5133-3b2c-bce1-ef7e47484205> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_statistics.cpython-39-darwin.so
       0x126408000 -        0x126b5ffff _rust.abi3.so (*) <16e50586-dc06-3720-a8de-02bf03e0413f> /Users/USER/Library/Python/3.9/lib/python/site-packages/cryptography/hazmat/bindings/_rust.abi3.so
       0x120c3c000 -        0x120c5bfff _cffi_backend.cpython-39-darwin.so (*) <8b8affa2-8401-309e-a9a4-a4c38bfcc8b6> /Users/USER/Library/Python/3.9/lib/python/site-packages/_cffi_backend.cpython-39-darwin.so
       0x1219f0000 -        0x121a53fff _bcrypt.abi3.so (*) <059797ef-4c70-3224-bb1c-904ad963f12c> /Users/USER/Library/Python/3.9/lib/python/site-packages/bcrypt/_bcrypt.abi3.so
       0x11f9e4000 -        0x11f9f7fff _c_internal_utils.cpython-39-darwin.so (*) <2343bafa-fab1-373c-80dc-c872d77a8466> /Users/USER/Library/Python/3.9/lib/python/site-packages/matplotlib/_c_internal_utils.cpython-39-darwin.so
       0x12502c000 -        0x12508bfff _imaging.cpython-39-darwin.so (*) <8a5eea42-01b4-3c5d-a2da-3bdc5102b14d> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/_imaging.cpython-39-darwin.so
       0x125184000 -        0x12522ffff libtiff.6.dylib (*) <76ab410c-4898-3fde-a872-5cefcdd51b56> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/.dylibs/libtiff.6.dylib
       0x125250000 -        0x1252d3fff libjpeg.62.4.0.dylib (*) <688c6473-716c-32eb-8cfe-f11203c4574d> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/.dylibs/libjpeg.62.4.0.dylib
       0x1252ec000 -        0x125383fff libopenjp2.2.5.3.dylib (*) <6994e1d8-b3e5-38d6-aef0-721586b2d5ce> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/.dylibs/libopenjp2.2.5.3.dylib
       0x12020c000 -        0x120223fff libz.1.3.1.zlib-ng.dylib (*) <5be17d28-46cf-3336-bfae-f315e9891018> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/.dylibs/libz.1.3.1.zlib-ng.dylib
       0x124fe4000 -        0x12500bfff libxcb.1.1.0.dylib (*) <6fa02d7f-daaa-3c79-8b0d-c5319e003f3d> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/.dylibs/libxcb.1.1.0.dylib
       0x12510c000 -        0x12514bfff liblzma.5.dylib (*) <8dfe23b8-ad17-3d21-8c5e-5525cd8953db> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/.dylibs/liblzma.5.dylib
       0x11eddc000 -        0x11eddffff libXau.6.dylib (*) <32a172ad-f11b-381b-9270-3f9a195cbe7f> /Users/USER/Library/Python/3.9/lib/python/site-packages/PIL/.dylibs/libXau.6.dylib
       0x12542c000 -        0x12545ffff _path.cpython-39-darwin.so (*) <adc46467-3226-3781-9b3b-70c1c747858e> /Users/USER/Library/Python/3.9/lib/python/site-packages/matplotlib/_path.cpython-39-darwin.so
       0x1257ac000 -        0x12583bfff ft2font.cpython-39-darwin.so (*) <0f5cb38b-c2f8-30da-91e5-31a756dd5fc6> /Users/USER/Library/Python/3.9/lib/python/site-packages/matplotlib/ft2font.cpython-39-darwin.so
       0x125774000 -        0x12578ffff _cext.cpython-39-darwin.so (*) <71124f3e-5dce-30c7-9010-63e30c4c0520> /Users/USER/Library/Python/3.9/lib/python/site-packages/kiwisolver/_cext.cpython-39-darwin.so
       0x125d70000 -        0x125da7fff _image.cpython-39-darwin.so (*) <5edf27d6-bb3d-3000-966f-6be2038bf55b> /Users/USER/Library/Python/3.9/lib/python/site-packages/matplotlib/_image.cpython-39-darwin.so
       0x121afc000 -        0x121b0bfff _multidict.cpython-39-darwin.so (*) <a3a21801-d9f3-331e-b87f-e91ebeccf742> /Users/USER/Library/Python/3.9/lib/python/site-packages/multidict/_multidict.cpython-39-darwin.so
       0x12573c000 -        0x12574ffff _quoting_c.cpython-39-darwin.so (*) <36e934ee-c120-395b-af57-d0d4c01a6760> /Users/USER/Library/Python/3.9/lib/python/site-packages/yarl/_quoting_c.cpython-39-darwin.so
       0x125160000 -        0x12516ffff _helpers_c.cpython-39-darwin.so (*) <b13384eb-b7fc-32cf-8d54-bc8b0f65d4bd> /Users/USER/Library/Python/3.9/lib/python/site-packages/propcache/_helpers_c.cpython-39-darwin.so
       0x126244000 -        0x12624bfff _http_writer.cpython-39-darwin.so (*) <bbfd8fd9-2b08-3f7b-a7f3-791ec3f3f930> /Users/USER/Library/Python/3.9/lib/python/site-packages/aiohttp/_http_writer.cpython-39-darwin.so
       0x1262bc000 -        0x1262fbfff _http_parser.cpython-39-darwin.so (*) <81c7fbe1-ce76-37b8-bc63-caccbce3f931> /Users/USER/Library/Python/3.9/lib/python/site-packages/aiohttp/_http_parser.cpython-39-darwin.so
       0x11fa8c000 -        0x11fa93fff mask.cpython-39-darwin.so (*) <be905f48-56eb-33f7-b559-b0914d88caff> /Users/USER/Library/Python/3.9/lib/python/site-packages/aiohttp/_websocket/mask.cpython-39-darwin.so
       0x12631c000 -        0x12633bfff reader_c.cpython-39-darwin.so (*) <9b837c85-99a2-3d1f-a07c-ef02ff8bdc9d> /Users/USER/Library/Python/3.9/lib/python/site-packages/aiohttp/_websocket/reader_c.cpython-39-darwin.so
       0x1263d0000 -        0x1263dffff _frozenlist.cpython-39-darwin.so (*) <feeb7c6c-bb1f-3471-bd7a-73cb266f79d3> /Users/USER/Library/Python/3.9/lib/python/site-packages/frozenlist/_frozenlist.cpython-39-darwin.so
       0x127348000 -        0x127357fff _ccallback_c.cpython-39-darwin.so (*) <d2ff9762-ad40-3c2d-8df7-35ae011fc7c3> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/_lib/_ccallback_c.cpython-39-darwin.so
       0x1277c0000 -        0x127ad3fff _sparsetools.cpython-39-darwin.so (*) <6eb4e546-18ce-3c62-977b-3491edc1d682> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/_sparsetools.cpython-39-darwin.so
       0x1274f0000 -        0x127563fff _csparsetools.cpython-39-darwin.so (*) <cf45f738-0d13-3e01-bf68-430a59c1f08f> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/_csparsetools.cpython-39-darwin.so
       0x127604000 -        0x12764ffff _fblas.cpython-39-darwin.so (*) <6ad48c6c-bc1b-3591-97f8-e2874a4a92c4> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_fblas.cpython-39-darwin.so
       0x12ead4000 -        0x12fc37fff libopenblas.0.dylib (*) <00198043-5605-391a-8ef7-a1e9a3d1ac7a> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/.dylibs/libopenblas.0.dylib
       0x127d1c000 -        0x127e6bfff libgfortran.5.dylib (*) <ae3c441b-de1b-3bb8-8c6e-1a2411185d0e> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/.dylibs/libgfortran.5.dylib
       0x12768c000 -        0x1276cbfff libquadmath.0.dylib (*) <81355d03-a464-3826-b89b-106d33d94d39> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/.dylibs/libquadmath.0.dylib
       0x12757c000 -        0x12758bfff libgcc_s.1.1.dylib (*) <ad4f9635-aa1c-370d-a9a6-8889ebb4d94b> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/.dylibs/libgcc_s.1.1.dylib
       0x127ee0000 -        0x127fcffff _flapack.cpython-39-darwin.so (*) <da91db33-d7ae-3255-ad3d-2d98d311c095> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_flapack.cpython-39-darwin.so
       0x127b58000 -        0x127bb7fff _cythonized_array_utils.cpython-39-darwin.so (*) <5552de67-4c63-3f49-be74-41457f654521> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_cythonized_array_utils.cpython-39-darwin.so
       0x127bcc000 -        0x127c3bfff cython_lapack.cpython-39-darwin.so (*) <e984658e-55a1-3e34-8eaa-5256c49d521e> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/cython_lapack.cpython-39-darwin.so
       0x12775c000 -        0x127783fff _solve_toeplitz.cpython-39-darwin.so (*) <09d7669a-07cd-3c23-a157-0703c080c682> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_solve_toeplitz.cpython-39-darwin.so
       0x127c78000 -        0x127c9bfff _decomp_lu_cython.cpython-39-darwin.so (*) <6e1a890d-8b07-3fb5-b5ea-04681c854563> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_decomp_lu_cython.cpython-39-darwin.so
       0x127cac000 -        0x127ccffff _matfuncs_sqrtm_triu.cpython-39-darwin.so (*) <8ca6d4e4-22ae-37ce-844a-d733fe952554> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_matfuncs_sqrtm_triu.cpython-39-darwin.so
       0x1280e4000 -        0x12812ffff _matfuncs_expm.cpython-39-darwin.so (*) <58eb3a00-7b9c-3b61-907e-cc08583cf080> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_matfuncs_expm.cpython-39-darwin.so
       0x128144000 -        0x12816ffff cython_blas.cpython-39-darwin.so (*) <107858bc-637d-3568-847f-221df1a8d0dd> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/cython_blas.cpython-39-darwin.so
       0x1281d0000 -        0x128207fff _decomp_update.cpython-39-darwin.so (*) <4c64f3bf-0aa9-3934-a35a-2d07b1217607> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_decomp_update.cpython-39-darwin.so
       0x12826c000 -        0x1282abfff _superlu.cpython-39-darwin.so (*) <7163bc21-3a81-35ab-b955-25bacb78e312> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/linalg/_dsolve/_superlu.cpython-39-darwin.so
       0x128338000 -        0x12838ffff _arpack.cpython-39-darwin.so (*) <ced47fb6-8bfe-37d5-b635-76a72e3c36cb> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/linalg/_eigen/arpack/_arpack.cpython-39-darwin.so
       0x127794000 -        0x1277a7fff _spropack.cpython-39-darwin.so (*) <b5c6dac3-44aa-3363-86d6-2fd531d165cc> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/linalg/_propack/_spropack.cpython-39-darwin.so
       0x127ce0000 -        0x127cf3fff _dpropack.cpython-39-darwin.so (*) <4d730e6b-87e0-3d13-9398-e4e03e53a02e> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/linalg/_propack/_dpropack.cpython-39-darwin.so
       0x128218000 -        0x12822ffff _cpropack.cpython-39-darwin.so (*) <6a4d4aaf-403a-3b89-9365-1d991680b7f7> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/linalg/_propack/_cpropack.cpython-39-darwin.so
       0x1282c0000 -        0x1282d7fff _zpropack.cpython-39-darwin.so (*) <b51e54ca-b2ae-3af3-a6f5-ba83a3f5ea21> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/linalg/_propack/_zpropack.cpython-39-darwin.so
       0x12844c000 -        0x128493fff _shortest_path.cpython-39-darwin.so (*) <54c20cfd-84bf-3fab-8805-3b5af4e513cf> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/csgraph/_shortest_path.cpython-39-darwin.so
       0x1283f0000 -        0x12840ffff _tools.cpython-39-darwin.so (*) <53a5568d-6b60-3f93-bb86-243d539fe3f2> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/csgraph/_tools.cpython-39-darwin.so
       0x12851c000 -        0x12857bfff _traversal.cpython-39-darwin.so (*) <8ca85fa1-920b-3ffa-826e-5e64346423ca> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/csgraph/_traversal.cpython-39-darwin.so
       0x1284a8000 -        0x1284cbfff _min_spanning_tree.cpython-39-darwin.so (*) <6611dbe5-92ba-3158-835a-df707883eb5b> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/csgraph/_min_spanning_tree.cpython-39-darwin.so
       0x128590000 -        0x1285bffff _flow.cpython-39-darwin.so (*) <392aec02-a55e-3f55-a255-a3541d156a52> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/csgraph/_flow.cpython-39-darwin.so
       0x128648000 -        0x12867bfff _matching.cpython-39-darwin.so (*) <7c507c67-d497-39ff-bd65-285d4b58f902> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/csgraph/_matching.cpython-39-darwin.so
       0x128604000 -        0x128633fff _reordering.cpython-39-darwin.so (*) <416c664a-ee1e-3558-81e7-16f8044db891> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/sparse/csgraph/_reordering.cpython-39-darwin.so
       0x12872c000 -        0x1287affff _ckdtree.cpython-39-darwin.so (*) <dc292569-ccad-321a-b93f-69dc43b61832> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/spatial/_ckdtree.cpython-39-darwin.so
       0x12d968000 -        0x12da27fff _qhull.cpython-39-darwin.so (*) <b27e258f-f310-3fba-87f2-a4ed6c0758a2> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/spatial/_qhull.cpython-39-darwin.so
       0x1262a0000 -        0x1262abfff messagestream.cpython-39-darwin.so (*) <1a6dd70b-9a8f-3f56-9ed5-2ff2375cb01a> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/_lib/messagestream.cpython-39-darwin.so
       0x1285d0000 -        0x1285effff _voronoi.cpython-39-darwin.so (*) <f0748945-bf27-31f6-b16a-447670685fd7> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/spatial/_voronoi.cpython-39-darwin.so
       0x1275e0000 -        0x1275f3fff _distance_wrap.cpython-39-darwin.so (*) <6db70aca-2f87-316a-8426-bb092686b551> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/spatial/_distance_wrap.cpython-39-darwin.so
       0x12868c000 -        0x1286abfff _hausdorff.cpython-39-darwin.so (*) <7a424ac8-1715-3b37-9f40-fbc51f41282a> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/spatial/_hausdorff.cpython-39-darwin.so
       0x12db40000 -        0x12dc17fff _ufuncs.cpython-39-darwin.so (*) <596aa827-0222-318f-8a67-baaaad840c9e> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/special/_ufuncs.cpython-39-darwin.so
       0x12d800000 -        0x12d84ffff _ufuncs_cxx.cpython-39-darwin.so (*) <6c2ed104-0745-37e1-9f9c-8659dcc6686e> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/special/_ufuncs_cxx.cpython-39-darwin.so
       0x1286bc000 -        0x1286dbfff _cdflib.cpython-39-darwin.so (*) <f8ab2561-dd82-3de4-895d-7f8799f2f04f> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/special/_cdflib.cpython-39-darwin.so
       0x12d908000 -        0x12d933fff _specfun.cpython-39-darwin.so (*) <998148fe-dafb-34fb-b830-a7000270ab8c> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/special/_specfun.cpython-39-darwin.so
       0x11fe9c000 -        0x11fea3fff _comb.cpython-39-darwin.so (*) <330bd195-4d59-3c15-9977-0f4020faee53> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/special/_comb.cpython-39-darwin.so
       0x128420000 -        0x12842ffff _ellip_harm_2.cpython-39-darwin.so (*) <e028919a-cfd3-376b-b834-eb67a487f042> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/special/_ellip_harm_2.cpython-39-darwin.so
       0x12dc40000 -        0x12dca7fff _distance_pybind.cpython-39-darwin.so (*) <0e0b047e-606d-3e01-8dd9-4cd349c928b7> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/spatial/_distance_pybind.cpython-39-darwin.so
       0x12dccc000 -        0x12dd63fff _rotation.cpython-39-darwin.so (*) <995c503d-ea5a-3a35-a94e-d5ac3f96c668> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/spatial/transform/_rotation.cpython-39-darwin.so
       0x1287d0000 -        0x1287ebfff _nd_image.cpython-39-darwin.so (*) <ae5fd338-595e-3219-9302-077d6ce1942c> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/ndimage/_nd_image.cpython-39-darwin.so
       0x12de20000 -        0x12de5ffff _ni_label.cpython-39-darwin.so (*) <bf656840-09ea-3eee-801d-8724a5cacdfb> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/ndimage/_ni_label.cpython-39-darwin.so
       0x1219d0000 -        0x1219d7fff _minpack2.cpython-39-darwin.so (*) <2e4160e1-05ab-30c4-a7f0-a3b949fe993d> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_minpack2.cpython-39-darwin.so
       0x127724000 -        0x12772ffff _group_columns.cpython-39-darwin.so (*) <ac5de565-ee02-3184-b89b-f5105cc99735> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_group_columns.cpython-39-darwin.so
       0x12df0c000 -        0x12df3ffff _trlib.cpython-39-darwin.so (*) <3366f993-46d4-3e6f-8c12-e93a5c764401> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_trlib/_trlib.cpython-39-darwin.so
       0x12d944000 -        0x12d957fff _lbfgsb.cpython-39-darwin.so (*) <bd97736a-b3a8-366b-860c-9295f03e6d11> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_lbfgsb.cpython-39-darwin.so
       0x12db08000 -        0x12db1ffff _moduleTNC.cpython-39-darwin.so (*) <fb932be1-f87a-38b2-8340-ef9b26474b3f> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_moduleTNC.cpython-39-darwin.so
       0x1280c4000 -        0x1280d3fff _cobyla.cpython-39-darwin.so (*) <94e55800-8326-36a7-88e2-fa588efbb397> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_cobyla.cpython-39-darwin.so
       0x12d8cc000 -        0x12d8dbfff _slsqp.cpython-39-darwin.so (*) <41fbe287-b41b-3ddf-897a-60becc216a51> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_slsqp.cpython-39-darwin.so
       0x12773c000 -        0x127747fff _minpack.cpython-39-darwin.so (*) <31f6425f-98fe-38ce-a817-6302fa93a722> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_minpack.cpython-39-darwin.so
       0x12df58000 -        0x12df77fff givens_elimination.cpython-39-darwin.so (*) <de0dbe69-87d6-3fbd-8ea0-94ed3221715b> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_lsq/givens_elimination.cpython-39-darwin.so
       0x1068b4000 -        0x1068b7fff _zeros.cpython-39-darwin.so (*) <f1d4bb12-dcd2-3159-8dd4-29f3babdba4d> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_zeros.cpython-39-darwin.so
       0x12e6d4000 -        0x12e963fff _highs_wrapper.cpython-39-darwin.so (*) <32ed7d9f-d0c1-31b3-a2b1-2874e11fb213> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_highs/_highs_wrapper.cpython-39-darwin.so
       0x1250f8000 -        0x1250fffff _highs_constants.cpython-39-darwin.so (*) <ab030583-6d05-34b9-9d2b-812cae79af5c> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_highs/_highs_constants.cpython-39-darwin.so
       0x12e17c000 -        0x12e1c3fff _interpolative.cpython-39-darwin.so (*) <c9f4f965-c26f-3d68-b44b-0a28517eb12d> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/linalg/_interpolative.cpython-39-darwin.so
       0x12e2f4000 -        0x12e327fff _bglu_dense.cpython-39-darwin.so (*) <6a647c65-847d-34af-9d32-b01796e56ad9> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_bglu_dense.cpython-39-darwin.so
       0x125760000 -        0x125767fff _lsap.cpython-39-darwin.so (*) <b4f8d4d1-7aa7-381f-8b80-21db1f3fd75c> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_lsap.cpython-39-darwin.so
       0x12dff8000 -        0x12e00ffff _pava_pybind.cpython-39-darwin.so (*) <cc9c208b-c59f-354a-b4b1-b3c9bc8f7142> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_pava_pybind.cpython-39-darwin.so
       0x125d5c000 -        0x125d63fff _direct.cpython-39-darwin.so (*) <fb1fe974-ce25-3b5c-b660-058c2319fedc> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/optimize/_direct.cpython-39-darwin.so
       0x12deb4000 -        0x12dec3fff _odepack.cpython-39-darwin.so (*) <0f3a634d-04ac-31de-8860-6f98ab1bef7c> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/integrate/_odepack.cpython-39-darwin.so
       0x12e24c000 -        0x12e25ffff _quadpack.cpython-39-darwin.so (*) <0d4b0e73-da1f-3a85-91b2-649886cd619a> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/integrate/_quadpack.cpython-39-darwin.so
       0x12e4b4000 -        0x12e4d3fff _vode.cpython-39-darwin.so (*) <150fdb3d-f7a8-31ed-ae1f-f4c56c0a78d2> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/integrate/_vode.cpython-39-darwin.so
       0x12e2b0000 -        0x12e2c3fff _dop.cpython-39-darwin.so (*) <604f756e-2dc8-33bb-af1e-8da42ae0ee4a> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/integrate/_dop.cpython-39-darwin.so
       0x12e35c000 -        0x12e36ffff _lsoda.cpython-39-darwin.so (*) <08d7a991-fbe7-3219-b738-bb0bb6fc375a> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/integrate/_lsoda.cpython-39-darwin.so
       0x141e9c000 -        0x141f0bfff _stats.cpython-39-darwin.so (*) <e291d4ce-e422-3219-8bcd-af68ec94dadc> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_stats.cpython-39-darwin.so
       0x142208000 -        0x1423abfff cython_special.cpython-39-darwin.so (*) <cb25e63b-c8cb-35d4-a96a-062dc48b85c6> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/special/cython_special.cpython-39-darwin.so
       0x12ea54000 -        0x12ea6ffff beta_ufunc.cpython-39-darwin.so (*) <5235a646-3e24-394e-8efb-85c16c410318> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/beta_ufunc.cpython-39-darwin.so
       0x12ea84000 -        0x12ea9bfff binom_ufunc.cpython-39-darwin.so (*) <17a93990-02b9-3986-9845-5ea342dd0028> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/binom_ufunc.cpython-39-darwin.so
       0x141df0000 -        0x141e07fff nbinom_ufunc.cpython-39-darwin.so (*) <e4531596-e1f3-3382-89cb-f1795de24efb> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/nbinom_ufunc.cpython-39-darwin.so
       0x12e464000 -        0x12e477fff hypergeom_ufunc.cpython-39-darwin.so (*) <a3eaa986-d84c-37fe-b7fa-44d8a2f3956e> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/hypergeom_ufunc.cpython-39-darwin.so
       0x141e44000 -        0x141e57fff ncf_ufunc.cpython-39-darwin.so (*) <947fca9d-4db3-3134-9ad7-f6ff3f108ba2> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/ncf_ufunc.cpython-39-darwin.so
       0x141f50000 -        0x141f67fff ncx2_ufunc.cpython-39-darwin.so (*) <cb71ca30-70e7-3279-a1e0-96ef08ed37ba> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/ncx2_ufunc.cpython-39-darwin.so
       0x141fb4000 -        0x141fd3fff nct_ufunc.cpython-39-darwin.so (*) <d756230c-9685-3e61-be72-05f26ac4dca2> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/nct_ufunc.cpython-39-darwin.so
       0x12e208000 -        0x12e213fff skewnorm_ufunc.cpython-39-darwin.so (*) <c2cb808c-f5ea-3447-9374-64fcfb85fdb4> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/skewnorm_ufunc.cpython-39-darwin.so
       0x141f7c000 -        0x141f93fff invgauss_ufunc.cpython-39-darwin.so (*) <769a7561-b8e1-3910-8073-8fecf36bd241> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_boost/invgauss_ufunc.cpython-39-darwin.so
       0x12e5e8000 -        0x12e5f7fff _fitpack.cpython-39-darwin.so (*) <41f9081f-4398-33e5-ba22-cbfe3d04d1d8> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/interpolate/_fitpack.cpython-39-darwin.so
       0x1425e8000 -        0x14261bfff dfitpack.cpython-39-darwin.so (*) <4c2955d3-3fb9-3748-8448-ec6e2f1ae0e3> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/interpolate/dfitpack.cpython-39-darwin.so
       0x142780000 -        0x1427dbfff _bspl.cpython-39-darwin.so (*) <37dad04a-f5c2-353d-b098-3133a5076f0e> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/interpolate/_bspl.cpython-39-darwin.so
       0x1426f4000 -        0x142737fff _ppoly.cpython-39-darwin.so (*) <c80d9fcf-fadd-3186-8d2a-807307ac84c0> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/interpolate/_ppoly.cpython-39-darwin.so
       0x142810000 -        0x142853fff interpnd.cpython-39-darwin.so (*) <6672bc6c-0899-38fc-bbc8-af632c0aeca5> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/interpolate/interpnd.cpython-39-darwin.so
       0x142680000 -        0x1426bbfff _rbfinterp_pythran.cpython-39-darwin.so (*) <49063788-81ac-3111-a1bf-a98c313fda66> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/interpolate/_rbfinterp_pythran.cpython-39-darwin.so
       0x142634000 -        0x14265bfff _rgi_cython.cpython-39-darwin.so (*) <ca7ea6e5-3957-3d1f-bd83-b4f2c7c651dd> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/interpolate/_rgi_cython.cpython-39-darwin.so
       0x14298c000 -        0x1429b7fff _biasedurn.cpython-39-darwin.so (*) <150fdc46-55ab-31fa-9e51-4b0659b11f1d> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_biasedurn.cpython-39-darwin.so
       0x1263f0000 -        0x1263f7fff levyst.cpython-39-darwin.so (*) <4b874b1e-6f88-371f-937d-689014ad2927> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_levy_stable/levyst.cpython-39-darwin.so
       0x141f24000 -        0x141f3bfff _stats_pythran.cpython-39-darwin.so (*) <846d474f-2345-3972-bcce-f6eac3a44c16> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_stats_pythran.cpython-39-darwin.so
       0x141dac000 -        0x141dbbfff _uarray.cpython-39-darwin.so (*) <e1a49db6-5eaa-39c0-87a4-04b4d0f127ce> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/_lib/_uarray/_uarray.cpython-39-darwin.so
       0x142d3c000 -        0x142ddbfff pypocketfft.cpython-39-darwin.so (*) <b7c57958-2778-3c52-baf6-86f6531e04b4> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/fft/_pocketfft/pypocketfft.cpython-39-darwin.so
       0x1428a8000 -        0x1428cbfff _ansari_swilk_statistics.cpython-39-darwin.so (*) <4a830a5b-417e-3d0e-987d-e7b4bbf6a5dc> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_ansari_swilk_statistics.cpython-39-darwin.so
       0x142cc8000 -        0x142d03fff _sobol.cpython-39-darwin.so (*) <ba64cbc7-d73e-318d-9845-3a0fc22080d9> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_sobol.cpython-39-darwin.so
       0x142bd4000 -        0x142bfbfff _qmc_cy.cpython-39-darwin.so (*) <f737016d-bf86-3adc-86c5-81bc9e688da3> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_qmc_cy.cpython-39-darwin.so
       0x142f94000 -        0x142fa3fff _mvn.cpython-39-darwin.so (*) <ac395167-668b-3d13-bd94-bd3bebe86329> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_mvn.cpython-39-darwin.so
       0x142ec0000 -        0x142eebfff rcont.cpython-39-darwin.so (*) <3f838b45-9a3b-3439-9f42-963435cc353c> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_rcont/rcont.cpython-39-darwin.so
       0x143304000 -        0x1433fffff unuran_wrapper.cpython-39-darwin.so (*) <8960cef1-9c85-3d1c-85b9-44561f8cac32> /Users/USER/Library/Python/3.9/lib/python/site-packages/scipy/stats/_unuran/unuran_wrapper.cpython-39-darwin.so
       0x143698000 -        0x14373ffff rpds.cpython-39-darwin.so (*) <1f17e9f9-30bf-3330-ba79-6bd9cb7f08ee> /Users/USER/Library/Python/3.9/lib/python/site-packages/rpds/rpds.cpython-39-darwin.so
       0x12d8e8000 -        0x12d8effff _psutil_osx.abi3.so (*) <75343fe3-84d4-3b23-9c84-cec8f6719f12> /Users/USER/Library/Python/3.9/lib/python/site-packages/psutil/_psutil_osx.abi3.so
       0x106b9c000 -        0x106b9ffff _psutil_posix.abi3.so (*) <8114b100-139b-377b-b475-99f6dc33b187> /Users/USER/Library/Python/3.9/lib/python/site-packages/psutil/_psutil_posix.abi3.so
       0x19d45e000 -        0x19d49a4af libsystem_kernel.dylib (*) <5e7de3d9-6e8a-3cd7-aa53-523e7e474157> /usr/lib/system/libsystem_kernel.dylib
       0x19d49b000 -        0x19d4a7abb libsystem_pthread.dylib (*) <f37b8a66-9bab-32a0-b222-76d650a69d19> /usr/lib/system/libsystem_pthread.dylib
       0x19d32d000 -        0x19d3af047 libsystem_c.dylib (*) <781016be-85b8-3d8f-8698-c02c17adc7a3> /usr/lib/system/libsystem_c.dylib
       0x19d0d1000 -        0x19d16ff67 dyld (*) <0b370235-e5de-3f28-b9a1-fb3dad42b317> /usr/lib/dyld
               0x0 - 0xffffffffffffffff ??? (*) <00000000-0000-0000-0000-000000000000> ???

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

{"app_name":"Python","timestamp":"2025-10-12 03:07:20.00 +0100","app_version":"3.9.6","slice_uuid":"6eb25e2c-229f-3707-b5bb-7c6ff0239635","build_version":"3.9.6","platform":1,"bundleID":"com.apple.python3","share_with_app_devs":0,"is_first_party":0,"bug_type":"309","os_version":"macOS 26.1 (25B5057f)","roots_installed":0,"name":"Python","incident_id":"D6F16153-9402-4999-92B7-7D4785799419"}
{
  "uptime" : 240000,
  "procRole" : "Unspecified",
  "version" : 2,
  "userID" : 501,
  "deployVersion" : 210,
  "modelCode" : "Mac16,13",
  "coalitionID" : 24052,
  "osVersion" : {
    "train" : "macOS 26.1",
    "build" : "25B5057f",
    "releaseType" : "User"
  },
  "captureTime" : "2025-10-12 03:07:19.6460 +0100",
  "codeSigningMonitor" : 2,
  "incident" : "D6F16153-9402-4999-92B7-7D4785799419",
  "pid" : 49036,
  "translated" : false,
  "cpuType" : "ARM-64",
  "roots_installed" : 0,
  "bug_type" : "309",
  "procLaunch" : "2025-10-12 03:07:17.1661 +0100",
  "procStartAbsTime" : 5907491268144,
  "procExitAbsTime" : 5907550774319,
  "procName" : "Python",
  "procPath" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/Resources\/Python.app\/Contents\/MacOS\/Python",
  "bundleInfo" : {"CFBundleShortVersionString":"3.9.6","CFBundleVersion":"3.9.6","CFBundleIdentifier":"com.apple.python3"},
  "buildInfo" : {"ProjectName":"python3","SourceVersion":"141000000500005","BuildVersion":"678"},
  "storeInfo" : {"deviceIdentifierForVendor":"CA424AFA-E33D-5B56-BD82-DCB980E3568A","thirdParty":true},
  "parentProc" : "Exited process",
  "parentPid" : 49034,
  "coalitionName" : "com.microsoft.VSCode",
  "crashReporterKey" : "4E207357-19A3-A70F-DAD5-7940E32325FE",
  "developerMode" : 1,
  "responsiblePid" : 22668,
  "responsibleProc" : "Electron",
  "codeSigningID" : "com.apple.python3",
  "codeSigningTeamID" : "",
  "codeSigningFlags" : 570442241,
  "codeSigningValidationCategory" : 1,
  "codeSigningTrustLevel" : 4294967295,
  "codeSigningAuxiliaryInfo" : 0,
  "instructionByteStream" : {"beforePC":"fyMD1f17v6n9AwCRFOD\/l78DAJH9e8Go\/w9f1sADX9YQKYDSARAA1A==","atPC":"AwEAVH8jA9X9e7+p\/QMAkQng\/5e\/AwCR\/XvBqP8PX9bAA1\/WcAqA0g=="},
  "bootSessionUUID" : "7328F4B2-3451-4820-BFE5-66E9D5D39527",
  "wakeTime" : 163,
  "sleepWakeUUID" : "A69A2551-0142-4426-AA55-C245322EC7B3",
  "sip" : "enabled",
  "exception" : {"codes":"0x0000000000000000, 0x0000000000000000","rawCodes":[0,0],"type":"EXC_CRASH","signal":"SIGABRT"},
  "termination" : {"flags":0,"code":6,"namespace":"SIGNAL","indicator":"Abort trap: 6","byProc":"Python","byPid":49036},
  "asi" : {"libsystem_c.dylib":["abort() called"]},
  "extMods" : {"caller":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"system":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"targeted":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"warnings":0},
  "faultingThread" : 0,
  "threads" : [{"frames":[{"imageOffset":38320,"symbol":"__pthread_kill","symbolLocation":8,"imageIndex":236},{"imageOffset":26760,"symbol":"pthread_kill","symbolLocation":296,"imageIndex":237},{"imageOffset":497744,"symbol":"abort","symbolLocation":124,"imageIndex":238},{"imageOffset":1365520,"imageIndex":1},{"imageOffset":1364948,"imageIndex":1},{"imageOffset":1364336,"symbol":"_Py_FatalErrorFunc","symbolLocation":40,"imageIndex":1},{"imageOffset":1112360,"symbol":"_Py_CheckRecursiveCall","symbolLocation":72,"imageIndex":1},{"imageOffset":304900,"imageIndex":1},{"imageOffset":273408,"symbol":"PyObject_VectorcallMethod","symbolLocation":144,"imageIndex":1},{"imageOffset":1363060,"imageIndex":1},{"imageOffset":1364936,"imageIndex":1},{"imageOffset":1364336,"symbol":"_Py_FatalErrorFunc","symbolLocation":40,"imageIndex":1},{"imageOffset":1133892,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":21164,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":274160,"imageIndex":1},{"imageOffset":274544,"symbol":"_PyObject_CallMethodIdObjArgs","symbolLocation":112,"imageIndex":1},{"imageOffset":1290732,"symbol":"PyImport_ImportModuleLevelObject","symbolLocation":1500,"imageIndex":1},{"imageOffset":1094836,"imageIndex":1},{"imageOffset":546512,"imageIndex":1},{"imageOffset":267116,"symbol":"_PyObject_MakeTpCall","symbolLocation":356,"imageIndex":1},{"imageOffset":1139772,"imageIndex":1},{"imageOffset":1117608,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":4880,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121456,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8728,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":278164,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1123692,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":10964,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1123692,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":10964,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121456,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8728,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":1112528,"symbol":"PyEval_EvalCode","symbolLocation":80,"imageIndex":1},{"imageOffset":1098556,"imageIndex":1},{"imageOffset":543980,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1123692,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":10964,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1123692,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":10964,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1503796,"imageIndex":1},{"imageOffset":1501852,"symbol":"Py_RunMain","symbolLocation":824,"imageIndex":1},{"imageOffset":1503424,"imageIndex":1},{"imageOffset":1503584,"symbol":"Py_BytesMain","symbolLocation":40,"imageIndex":1},{"imageOffset":36180,"symbol":"start","symbolLocation":7184,"imageIndex":239}],"id":6100046,"recursionInfoArray":[{"hottestElided":35,"coldestElided":4499,"depth":1026,"keyFrame":{"imageOffset":1139676,"imageIndex":1}}],"originalLength":4522,"triggered":true,"threadState":{"x":[{"value":0},{"value":0},{"value":0},{"value":0},{"value":4294967295},{"value":104},{"value":104},{"value":6161609848},{"value":9418809925632139745},{"value":9418809934383545569},{"value":2},{"value":1099511627776},{"value":4294967293},{"value":0},{"value":0},{"value":0},{"value":328},{"value":8779075800},{"value":0},{"value":6},{"value":259},{"value":8755863008,"symbolLocation":224,"symbol":"_main_thread"},{"value":8755893264,"symbolLocation":304,"symbol":"__sF"},{"value":4313724174},{"value":1},{"value":3},{"value":4314938960},{"value":6161609824},{"value":4314938960}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933846152},"cpsr":{"value":1073741824},"fp":{"value":6161608480},"sp":{"value":6161608448},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933607856,"matchesCrashFrame":1},"far":{"value":0}},"queue":"com.apple.main-thread"},{"id":6100047,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6163017416},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458663952,"symbolLocation":16,"symbol":"thread_status"},{"value":4458664016,"symbolLocation":80,"symbol":"thread_status"},{"value":6163017952},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6163017536},"sp":{"value":6163017392},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100048,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6163590856},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664080,"symbolLocation":144,"symbol":"thread_status"},{"value":4458664144,"symbolLocation":208,"symbol":"thread_status"},{"value":6163591392},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6163590976},"sp":{"value":6163590832},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100049,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6164164296},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664208,"symbolLocation":272,"symbol":"thread_status"},{"value":4458664272,"symbolLocation":336,"symbol":"thread_status"},{"value":6164164832},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6164164416},"sp":{"value":6164164272},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100050,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6164737736},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664336,"symbolLocation":400,"symbol":"thread_status"},{"value":4458664400,"symbolLocation":464,"symbol":"thread_status"},{"value":6164738272},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6164737856},"sp":{"value":6164737712},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100051,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6165311176},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664464,"symbolLocation":528,"symbol":"thread_status"},{"value":4458664528,"symbolLocation":592,"symbol":"thread_status"},{"value":6165311712},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6165311296},"sp":{"value":6165311152},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100052,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6165884616},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664592,"symbolLocation":656,"symbol":"thread_status"},{"value":4458664656,"symbolLocation":720,"symbol":"thread_status"},{"value":6165885152},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6165884736},"sp":{"value":6165884592},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100053,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6166458056},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664720,"symbolLocation":784,"symbol":"thread_status"},{"value":4458664784,"symbolLocation":848,"symbol":"thread_status"},{"value":6166458592},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6166458176},"sp":{"value":6166458032},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100054,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6167031496},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664848,"symbolLocation":912,"symbol":"thread_status"},{"value":4458664912,"symbolLocation":976,"symbol":"thread_status"},{"value":6167032032},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6167031616},"sp":{"value":6167031472},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100055,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1475476,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":36},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6167604936},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":4458664976,"symbolLocation":1040,"symbol":"thread_status"},{"value":4458665040,"symbolLocation":1104,"symbol":"thread_status"},{"value":6167605472},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4458582016,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6167605056},"sp":{"value":6167604912},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100056,"frames":[],"threadState":{"x":[{"value":6168178688},{"value":10243},{"value":6167642112},{"value":0},{"value":409604},{"value":18446744073709551615},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":0},"fp":{"value":0},"sp":{"value":6168178688},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933826452},"far":{"value":0}}},{"id":6100057,"frames":[],"threadState":{"x":[{"value":6168752128},{"value":9475},{"value":6168215552},{"value":0},{"value":409604},{"value":18446744073709551615},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":0},"cpsr":{"value":0},"fp":{"value":0},"sp":{"value":6168752128},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933826452},"far":{"value":0}}},{"id":6100112,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6169325256},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096411152,"symbolLocation":16,"symbol":"thread_status"},{"value":5096411216,"symbolLocation":80,"symbol":"thread_status"},{"value":6169325792},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6169325376},"sp":{"value":6169325232},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100113,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6169898696},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096411280,"symbolLocation":144,"symbol":"thread_status"},{"value":5096411344,"symbolLocation":208,"symbol":"thread_status"},{"value":6169899232},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6169898816},"sp":{"value":6169898672},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100114,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6170472136},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096411408,"symbolLocation":272,"symbol":"thread_status"},{"value":5096411472,"symbolLocation":336,"symbol":"thread_status"},{"value":6170472672},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6170472256},"sp":{"value":6170472112},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100115,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6171045576},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096411536,"symbolLocation":400,"symbol":"thread_status"},{"value":5096411600,"symbolLocation":464,"symbol":"thread_status"},{"value":6171046112},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6171045696},"sp":{"value":6171045552},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100116,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6171619016},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096411664,"symbolLocation":528,"symbol":"thread_status"},{"value":5096411728,"symbolLocation":592,"symbol":"thread_status"},{"value":6171619552},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6171619136},"sp":{"value":6171618992},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100117,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6172192456},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096411792,"symbolLocation":656,"symbol":"thread_status"},{"value":5096411856,"symbolLocation":720,"symbol":"thread_status"},{"value":6172192992},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6172192576},"sp":{"value":6172192432},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100118,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6172765896},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096411920,"symbolLocation":784,"symbol":"thread_status"},{"value":5096411984,"symbolLocation":848,"symbol":"thread_status"},{"value":6172766432},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6172766016},"sp":{"value":6172765872},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100119,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6173339336},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096412048,"symbolLocation":912,"symbol":"thread_status"},{"value":5096412112,"symbolLocation":976,"symbol":"thread_status"},{"value":6173339872},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6173339456},"sp":{"value":6173339312},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}},{"id":6100120,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":236},{"imageOffset":28892,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":237},{"imageOffset":1513788,"symbol":"blas_thread_server","symbolLocation":360,"imageIndex":140},{"imageOffset":27656,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":237},{"imageOffset":7080,"symbol":"thread_start","symbolLocation":8,"imageIndex":237}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6173912776},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8779075728},{"value":0},{"value":5096412176,"symbolLocation":1040,"symbol":"thread_status"},{"value":5096412240,"symbolLocation":1104,"symbol":"thread_status"},{"value":6173913312},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":5096345600,"symbolLocation":32,"symbol":"gemm_driver.level3_lock"},{"value":1}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6933848284},"cpsr":{"value":1610612736},"fp":{"value":6173912896},"sp":{"value":6173912752},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6933587192},"far":{"value":0}}}],
  "usedImages" : [
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4304420864,
    "CFBundleShortVersionString" : "3.9.6",
    "CFBundleIdentifier" : "com.apple.python3",
    "size" : 16384,
    "uuid" : "6eb25e2c-229f-3707-b5bb-7c6ff0239635",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/Resources\/Python.app\/Contents\/MacOS\/Python",
    "name" : "Python",
    "CFBundleVersion" : "3.9.6"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4311744512,
    "CFBundleShortVersionString" : "3.9.6",
    "CFBundleIdentifier" : "com.apple.python3",
    "size" : 2506752,
    "uuid" : "1f7e9bdf-34d6-33d3-81a7-24c47e0d5992",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/Python3",
    "name" : "Python3",
    "CFBundleVersion" : "3.9.6"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4311580672,
    "size" : 32768,
    "uuid" : "5ab95036-7a84-3805-a505-b552447b5184",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_heapq.cpython-39-darwin.so",
    "name" : "_heapq.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4389306368,
    "size" : 16384,
    "uuid" : "7bf4e0ff-7cbb-3cd1-a766-0c409645a739",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_opcode.cpython-39-darwin.so",
    "name" : "_opcode.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4389912576,
    "size" : 16384,
    "uuid" : "09195126-ae27-364b-bf8f-53eb189b9870",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_bisect.cpython-39-darwin.so",
    "name" : "_bisect.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4389994496,
    "size" : 32768,
    "uuid" : "6d627f31-aa64-3572-a55f-9ae208481c5e",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/zlib.cpython-39-darwin.so",
    "name" : "zlib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4390354944,
    "size" : 16384,
    "uuid" : "6105c19e-4d4e-32b8-8843-e91223dad09d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_bz2.cpython-39-darwin.so",
    "name" : "_bz2.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4390436864,
    "size" : 32768,
    "uuid" : "6e3d646a-7f92-3cde-82d7-0089e18f1a12",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_lzma.cpython-39-darwin.so",
    "name" : "_lzma.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4390535168,
    "size" : 16384,
    "uuid" : "5bee5e54-876a-3b18-b11e-a7ef4e8fff33",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/grp.cpython-39-darwin.so",
    "name" : "grp.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4390879232,
    "size" : 32768,
    "uuid" : "22bd65a7-4756-3cfa-aac1-d10d882cb42a",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_csv.cpython-39-darwin.so",
    "name" : "_csv.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4390977536,
    "size" : 32768,
    "uuid" : "9918a271-0a03-32f3-9756-be0e71ff616d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/binascii.cpython-39-darwin.so",
    "name" : "binascii.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4391075840,
    "size" : 32768,
    "uuid" : "75342080-6784-350b-812d-206d3b221cdb",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_struct.cpython-39-darwin.so",
    "name" : "_struct.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4392484864,
    "size" : 16384,
    "uuid" : "99cfcbb6-fd85-3797-a698-6db9cc7b8355",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_uuid.cpython-39-darwin.so",
    "name" : "_uuid.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4394909696,
    "size" : 1114112,
    "uuid" : "87ddbc0f-f489-3d19-b4ae-0062421cddc9",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/unicodedata.cpython-39-darwin.so",
    "name" : "unicodedata.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4305158144,
    "size" : 65536,
    "uuid" : "d399388c-9a55-3b85-a653-0f586e3d6767",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_socket.cpython-39-darwin.so",
    "name" : "_socket.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4396351488,
    "size" : 49152,
    "uuid" : "19157ce8-1e08-3232-b29f-1ef4f809619f",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/math.cpython-39-darwin.so",
    "name" : "math.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4394663936,
    "size" : 81920,
    "uuid" : "463cfec4-d1dd-3f01-a398-971f300f1b23",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_datetime.cpython-39-darwin.so",
    "name" : "_datetime.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4394811392,
    "size" : 32768,
    "uuid" : "c3a948a4-59e1-3d7b-968e-8e3094728d6d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_json.cpython-39-darwin.so",
    "name" : "_json.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4305289216,
    "size" : 16384,
    "uuid" : "aee77fda-eaa9-35a6-9eb4-a85148a27ed4",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_random.cpython-39-darwin.so",
    "name" : "_random.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4396908544,
    "size" : 32768,
    "uuid" : "ff1ac68a-03fb-33b8-80e9-70687d58d21d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_sha512.cpython-39-darwin.so",
    "name" : "_sha512.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4397793280,
    "size" : 16384,
    "uuid" : "21025db5-0dba-3a36-a038-3a9f649cd3d2",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_posixsubprocess.cpython-39-darwin.so",
    "name" : "_posixsubprocess.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4397875200,
    "size" : 32768,
    "uuid" : "96082726-10ef-3d3a-a53f-2b60f155317d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/select.cpython-39-darwin.so",
    "name" : "select.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4398907392,
    "size" : 278528,
    "uuid" : "8c71d159-05e1-347d-b8c1-84755996ffc2",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_decimal.cpython-39-darwin.so",
    "name" : "_decimal.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4396728320,
    "size" : 49152,
    "uuid" : "05f0dbce-3794-31c9-aca5-04f56606f7ec",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_elementtree.cpython-39-darwin.so",
    "name" : "_elementtree.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4400775168,
    "size" : 163840,
    "uuid" : "994f7633-f40a-39bb-9867-800e21b4124c",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/pyexpat.cpython-39-darwin.so",
    "name" : "pyexpat.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4398759936,
    "size" : 49152,
    "uuid" : "3b0cc2b7-b4c5-3886-9d09-d843de60a266",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/array.cpython-39-darwin.so",
    "name" : "array.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4400562176,
    "size" : 98304,
    "uuid" : "0f89f536-3122-3986-aaae-90d5d41f6500",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_ssl.cpython-39-darwin.so",
    "name" : "_ssl.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4402462720,
    "size" : 16384,
    "uuid" : "8f323497-2e9d-342a-b2e1-345685a4af6d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_contextvars.cpython-39-darwin.so",
    "name" : "_contextvars.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4402315264,
    "size" : 49152,
    "uuid" : "c8f017a4-9e91-37af-bded-65d7a78fde96",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_asyncio.cpython-39-darwin.so",
    "name" : "_asyncio.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4404822016,
    "size" : 32768,
    "uuid" : "679e7231-a59a-3cad-90cf-241a5e2fdb8f",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_hashlib.cpython-39-darwin.so",
    "name" : "_hashlib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4404641792,
    "size" : 49152,
    "uuid" : "476639d2-b0ab-3f91-a682-dd890ee9bca9",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_blake2.cpython-39-darwin.so",
    "name" : "_blake2.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4405182464,
    "size" : 65536,
    "uuid" : "6b89b147-f807-32a9-88ab-ce2c09511e3d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_sha3.cpython-39-darwin.so",
    "name" : "_sha3.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4405460992,
    "size" : 16384,
    "uuid" : "d7f10ed3-5c76-3423-9cd7-c20343a58e2c",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_queue.cpython-39-darwin.so",
    "name" : "_queue.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4405313536,
    "size" : 32768,
    "uuid" : "969c04d4-ce82-388f-8fee-f84b71ef893b",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/readline.cpython-39-darwin.so",
    "name" : "readline.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4407361536,
    "size" : 49152,
    "uuid" : "fe9ef126-b321-3315-b3fa-007dd1d2f62d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_sqlite3.cpython-39-darwin.so",
    "name" : "_sqlite3.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4411211776,
    "size" : 2605056,
    "uuid" : "1a279e5d-158d-356b-9729-587af84e2c79",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/core\/_multiarray_umath.cpython-39-darwin.so",
    "name" : "_multiarray_umath.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4437737472,
    "size" : 20807680,
    "uuid" : "3dd132fc-be72-33cc-baf0-4c7df2669307",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/.dylibs\/libopenblas64_.0.dylib",
    "name" : "libopenblas64_.0.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4415062016,
    "size" : 3522560,
    "uuid" : "dd0e012a-b6de-31b1-a28e-260c7b51e595",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/.dylibs\/libgfortran.5.dylib",
    "name" : "libgfortran.5.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4407869440,
    "size" : 311296,
    "uuid" : "6d39d54b-d80e-3218-a095-b81ad0b3be90",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/.dylibs\/libquadmath.0.dylib",
    "name" : "libquadmath.0.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4407492608,
    "size" : 65536,
    "uuid" : "d9875303-8f38-33d9-a0d3-ab0adff3b915",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/.dylibs\/libgcc_s.1.1.dylib",
    "name" : "libgcc_s.1.1.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4407115776,
    "size" : 98304,
    "uuid" : "587afe91-9cab-31e2-96fd-e264bbdb9d6d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_pickle.cpython-39-darwin.so",
    "name" : "_pickle.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4410081280,
    "size" : 65536,
    "uuid" : "60c7a0dd-16b9-31dc-bafc-c3183b3c0ab8",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/core\/_multiarray_tests.cpython-39-darwin.so",
    "name" : "_multiarray_tests.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4407640064,
    "size" : 81920,
    "uuid" : "1f89dcab-1d9f-3949-8233-5a0aeb436d27",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_ctypes.cpython-39-darwin.so",
    "name" : "_ctypes.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4410982400,
    "size" : 98304,
    "uuid" : "b7a5137f-a42d-33d9-97a5-01f49eac03e2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/linalg\/_umath_linalg.cpython-39-darwin.so",
    "name" : "_umath_linalg.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4419551232,
    "size" : 65536,
    "uuid" : "d4f1aa1b-1d5b-31c0-914b-f7573e69b12c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/fft\/_pocketfft_internal.cpython-39-darwin.so",
    "name" : "_pocketfft_internal.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420665344,
    "size" : 458752,
    "uuid" : "0f6b1dcc-ce9c-3f80-bfd1-3f4dcd96ae39",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/mtrand.cpython-39-darwin.so",
    "name" : "mtrand.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4419928064,
    "size" : 131072,
    "uuid" : "a15db2c2-1645-3e76-8f83-8c56aeb363f2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/bit_generator.cpython-39-darwin.so",
    "name" : "bit_generator.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4421419008,
    "size" : 212992,
    "uuid" : "ae6c2a49-3ede-3b9d-b195-7f461dc3318b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/_common.cpython-39-darwin.so",
    "name" : "_common.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4421697536,
    "size" : 311296,
    "uuid" : "0f54435f-099c-3111-b308-7824f4906be6",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/_bounded_integers.cpython-39-darwin.so",
    "name" : "_bounded_integers.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420141056,
    "size" : 65536,
    "uuid" : "82b876ee-db08-3781-b69b-ab08d1fa32e6",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/_mt19937.cpython-39-darwin.so",
    "name" : "_mt19937.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420272128,
    "size" : 65536,
    "uuid" : "6cb4e48e-045e-3c48-bb3c-a501e1abb0ad",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/_philox.cpython-39-darwin.so",
    "name" : "_philox.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420403200,
    "size" : 65536,
    "uuid" : "0108ef0a-c7f5-3124-b3fa-1803b488f8fc",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/_pcg64.cpython-39-darwin.so",
    "name" : "_pcg64.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4410867712,
    "size" : 32768,
    "uuid" : "fb47f6b2-3649-33c6-91ed-ce6f7d76ec93",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/_sfc64.cpython-39-darwin.so",
    "name" : "_sfc64.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4422959104,
    "size" : 573440,
    "uuid" : "a8e6f7df-e5a5-3f57-ab85-60318792ee83",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/numpy\/random\/_generator.cpython-39-darwin.so",
    "name" : "_generator.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4428578816,
    "size" : 3145728,
    "uuid" : "e25299f6-7128-354b-b033-f8610a240ad9",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/lib.cpython-39-darwin.so",
    "name" : "lib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4426301440,
    "size" : 1163264,
    "uuid" : "9116691d-b326-32a0-93f6-c0335c8f07e2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/libarrow_python.2000.dylib",
    "name" : "libarrow_python.2000.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4795973632,
    "size" : 1622016,
    "uuid" : "f7d19036-3b8a-3d39-812f-272a95f5bf24",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/libarrow_substrait.2000.dylib",
    "name" : "libarrow_substrait.2000.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4799053824,
    "size" : 1261568,
    "uuid" : "625921f5-6c1a-3a3f-a7de-d0a3d5c028af",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/libarrow_dataset.2000.dylib",
    "name" : "libarrow_dataset.2000.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4801708032,
    "size" : 2277376,
    "uuid" : "aec6ca22-a37d-3d14-bba3-405331f24a63",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/libparquet.2000.dylib",
    "name" : "libparquet.2000.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4435017728,
    "size" : 1163264,
    "uuid" : "5fe3208d-25e2-388d-b810-b74357848ea4",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/libarrow_acero.2000.dylib",
    "name" : "libarrow_acero.2000.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4860313600,
    "size" : 36306944,
    "uuid" : "11bde922-a023-36f1-8807-f03d74e19f0d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/libarrow.2000.dylib",
    "name" : "libarrow.2000.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420534272,
    "size" : 32768,
    "uuid" : "6586461d-6253-3202-9e53-68ee6efbf945",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/pandas_parser.cpython-39-darwin.so",
    "name" : "pandas_parser.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4422877184,
    "size" : 32768,
    "uuid" : "6e002f61-21d7-3bf4-aff8-4bc8b7d685ab",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/pandas_datetime.cpython-39-darwin.so",
    "name" : "pandas_datetime.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4805754880,
    "size" : 901120,
    "uuid" : "1f353248-ea36-3092-a0a7-6e5c9c790559",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/interval.cpython-39-darwin.so",
    "name" : "interval.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4806819840,
    "size" : 1540096,
    "uuid" : "6d81e7a7-a51d-3455-9141-5fd00ddfab1b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/hashtable.cpython-39-darwin.so",
    "name" : "hashtable.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4428251136,
    "size" : 147456,
    "uuid" : "5dd857ed-e3d1-37cb-9766-499b7b952893",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/missing.cpython-39-darwin.so",
    "name" : "missing.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4433002496,
    "size" : 131072,
    "uuid" : "b7f2fc9f-4552-363e-962b-cc93b299198f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/dtypes.cpython-39-darwin.so",
    "name" : "dtypes.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4426186752,
    "size" : 49152,
    "uuid" : "1fc24201-40d8-3336-ba1a-777d07bb5763",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/ccalendar.cpython-39-darwin.so",
    "name" : "ccalendar.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4433379328,
    "size" : 98304,
    "uuid" : "5eabb00b-ce23-3e4b-9b34-90367333cb70",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/np_datetime.cpython-39-darwin.so",
    "name" : "np_datetime.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4433821696,
    "size" : 196608,
    "uuid" : "713cf5c9-d629-3381-9360-c69f54853479",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/conversion.cpython-39-darwin.so",
    "name" : "conversion.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4428464128,
    "size" : 49152,
    "uuid" : "a74c8fcd-6e06-3594-a68d-1d6897686154",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/base.cpython-39-darwin.so",
    "name" : "base.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4808622080,
    "size" : 737280,
    "uuid" : "e2b3c951-a016-3557-ae04-9d20d2044667",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/offsets.cpython-39-darwin.so",
    "name" : "offsets.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4437164032,
    "size" : 442368,
    "uuid" : "01f7a3b7-81e0-3de2-b1a7-240c4fc6d447",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/timestamps.cpython-39-darwin.so",
    "name" : "timestamps.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4434362368,
    "size" : 180224,
    "uuid" : "921014dd-1da4-3928-bddb-37c06d98e9e3",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/nattype.cpython-39-darwin.so",
    "name" : "nattype.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4810047488,
    "size" : 409600,
    "uuid" : "93b2c0ab-caae-34e6-a58a-9b5cd76269a8",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/timedeltas.cpython-39-darwin.so",
    "name" : "timedeltas.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4434624512,
    "size" : 180224,
    "uuid" : "852a04e8-c0fa-3f5a-9729-d1cc62d2ef22",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/timezones.cpython-39-darwin.so",
    "name" : "timezones.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4410769408,
    "size" : 32768,
    "uuid" : "d022a2fc-a33f-3393-9240-db6d3a356662",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_zoneinfo.cpython-39-darwin.so",
    "name" : "_zoneinfo.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4810571776,
    "size" : 212992,
    "uuid" : "c10e79d3-e0b3-3117-bf2a-2103b8b1cbe2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/fields.cpython-39-darwin.so",
    "name" : "fields.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4811145216,
    "size" : 196608,
    "uuid" : "d03b1ec3-a5ab-38ba-8ab2-73165660be89",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/tzconversion.cpython-39-darwin.so",
    "name" : "tzconversion.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4434886656,
    "size" : 49152,
    "uuid" : "debdd017-0dc0-3ea4-be2a-85d3f47e3503",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/properties.cpython-39-darwin.so",
    "name" : "properties.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4811784192,
    "size" : 278528,
    "uuid" : "0890f306-10c2-3756-9d16-0b513497e587",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/parsing.cpython-39-darwin.so",
    "name" : "parsing.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4812144640,
    "size" : 245760,
    "uuid" : "7d35b498-af4b-398b-bf35-42fbaa737609",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/strptime.cpython-39-darwin.so",
    "name" : "strptime.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4812914688,
    "size" : 344064,
    "uuid" : "bd8bf755-f604-3560-b01b-9613b730f6ee",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/period.cpython-39-darwin.so",
    "name" : "period.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4811423744,
    "size" : 147456,
    "uuid" : "93e5d267-95c2-369e-a903-d0afeab027f2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslibs\/vectorized.cpython-39-darwin.so",
    "name" : "vectorized.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4433297408,
    "size" : 32768,
    "uuid" : "1c9746bf-6f0a-3479-bca4-5131245fbb6e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/ops_dispatch.cpython-39-darwin.so",
    "name" : "ops_dispatch.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4814979072,
    "size" : 1490944,
    "uuid" : "f5e9a071-2b02-3387-86db-a4bb874c0e5b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/algos.cpython-39-darwin.so",
    "name" : "algos.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4814061568,
    "size" : 573440,
    "uuid" : "1f62c85d-ae06-336d-9d76-8b7e30e252cf",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/lib.cpython-39-darwin.so",
    "name" : "lib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4818108416,
    "size" : 720896,
    "uuid" : "9d0ab309-ab51-3d71-90b8-fa64384e232c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pyarrow\/_compute.cpython-39-darwin.so",
    "name" : "_compute.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4820123648,
    "size" : 163840,
    "uuid" : "4955067c-aa39-368a-8212-7157e72114ad",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/ops.cpython-39-darwin.so",
    "name" : "ops.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4814766080,
    "size" : 131072,
    "uuid" : "de2b52db-24d8-3d1b-a076-b5d5a9276f4e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/hashing.cpython-39-darwin.so",
    "name" : "hashing.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4811636736,
    "size" : 81920,
    "uuid" : "9453eadc-14f2-363b-9eb7-cc9adced3496",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/arrays.cpython-39-darwin.so",
    "name" : "arrays.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4821958656,
    "size" : 212992,
    "uuid" : "3560928e-a6e1-3761-9271-79490d8230e2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/tslib.cpython-39-darwin.so",
    "name" : "tslib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4823220224,
    "size" : 622592,
    "uuid" : "5bf4eebd-eb45-3e2f-87c5-b8dd0ac7406d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/sparse.cpython-39-darwin.so",
    "name" : "sparse.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4824285184,
    "size" : 262144,
    "uuid" : "6b992add-fd46-35a9-95ef-459f1a4882b2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/internals.cpython-39-darwin.so",
    "name" : "internals.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4809900032,
    "size" : 49152,
    "uuid" : "6b4d37fc-86b4-3781-af29-2936684d6132",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/indexing.cpython-39-darwin.so",
    "name" : "indexing.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4826202112,
    "size" : 638976,
    "uuid" : "0811a5d5-c591-30ef-9e12-6195f5926407",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/index.cpython-39-darwin.so",
    "name" : "index.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4825645056,
    "size" : 147456,
    "uuid" : "5d3b106a-5077-346d-9436-674cf49356a1",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/writers.cpython-39-darwin.so",
    "name" : "writers.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4828020736,
    "size" : 933888,
    "uuid" : "9e9150c3-fb9c-345b-b464-808e8b46fa0e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/join.cpython-39-darwin.so",
    "name" : "join.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4809801728,
    "size" : 32768,
    "uuid" : "82e15567-d8ad-38e1-bcd2-e48993feff49",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/mmap.cpython-39-darwin.so",
    "name" : "mmap.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4830461952,
    "size" : 262144,
    "uuid" : "96b7ce8c-c4cd-3085-a293-c7a0502b3b42",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/window\/aggregations.cpython-39-darwin.so",
    "name" : "aggregations.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4827774976,
    "size" : 131072,
    "uuid" : "5b1a7ba9-7bd4-3a5f-94a8-6b837b6b9d37",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/window\/indexers.cpython-39-darwin.so",
    "name" : "indexers.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4831608832,
    "size" : 196608,
    "uuid" : "f8c0c784-acdd-3532-b001-4ba195a7ba41",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/reshape.cpython-39-darwin.so",
    "name" : "reshape.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4834164736,
    "size" : 1867776,
    "uuid" : "881035ae-b8f4-34cb-ac75-733a761868af",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/groupby.cpython-39-darwin.so",
    "name" : "groupby.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4813881344,
    "size" : 49152,
    "uuid" : "3f17644c-ce59-374f-bffe-5771eb561ec9",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/json.cpython-39-darwin.so",
    "name" : "json.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4836196352,
    "size" : 360448,
    "uuid" : "804e14ec-29f1-3561-b97f-f2eaed4721e9",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/parsers.cpython-39-darwin.so",
    "name" : "parsers.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4817944576,
    "size" : 81920,
    "uuid" : "9c6d2c65-bea7-3494-a668-9c457bd4e76e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pandas\/_libs\/testing.cpython-39-darwin.so",
    "name" : "testing.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4823040000,
    "size" : 32768,
    "uuid" : "1b9ddaf1-6d95-3893-99aa-3f9f015083c7",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/cmath.cpython-39-darwin.so",
    "name" : "cmath.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4433215488,
    "size" : 16384,
    "uuid" : "25a6e224-d711-363c-8e28-ba41d4f0439c",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_scproxy.cpython-39-darwin.so",
    "name" : "_scproxy.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4813979648,
    "size" : 16384,
    "uuid" : "8a749554-2a89-3445-bc29-08a20a0ca27c",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/resource.cpython-39-darwin.so",
    "name" : "resource.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4844896256,
    "size" : 3751936,
    "uuid" : "8a370734-3093-332f-8582-b45fd9efee3f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pydantic_core\/_pydantic_core.cpython-39-darwin.so",
    "name" : "_pydantic_core.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4823138304,
    "size" : 16384,
    "uuid" : "7586df51-b08f-3909-83e9-14ff3629f3ed",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/termios.cpython-39-darwin.so",
    "name" : "termios.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4824203264,
    "size" : 16384,
    "uuid" : "03f76456-5133-3b2c-bce1-ef7e47484205",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_statistics.cpython-39-darwin.so",
    "name" : "_statistics.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4936728576,
    "size" : 7700480,
    "uuid" : "16e50586-dc06-3720-a8de-02bf03e0413f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/cryptography\/hazmat\/bindings\/_rust.abi3.so",
    "name" : "_rust.abi3.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4844666880,
    "size" : 131072,
    "uuid" : "8b8affa2-8401-309e-a9a4-a4c38bfcc8b6",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/_cffi_backend.cpython-39-darwin.so",
    "name" : "_cffi_backend.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4859035648,
    "size" : 409600,
    "uuid" : "059797ef-4c70-3224-bb1c-904ad963f12c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/bcrypt\/_bcrypt.abi3.so",
    "name" : "_bcrypt.abi3.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4825432064,
    "size" : 81920,
    "uuid" : "2343bafa-fab1-373c-80dc-c872d77a8466",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/matplotlib\/_c_internal_utils.cpython-39-darwin.so",
    "name" : "_c_internal_utils.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4915904512,
    "size" : 393216,
    "uuid" : "8a5eea42-01b4-3c5d-a2da-3bdc5102b14d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/_imaging.cpython-39-darwin.so",
    "name" : "_imaging.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4917313536,
    "size" : 704512,
    "uuid" : "76ab410c-4898-3fde-a872-5cefcdd51b56",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/.dylibs\/libtiff.6.dylib",
    "name" : "libtiff.6.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4918149120,
    "size" : 540672,
    "uuid" : "688c6473-716c-32eb-8cfe-f11203c4574d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/.dylibs\/libjpeg.62.4.0.dylib",
    "name" : "libjpeg.62.4.0.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4918788096,
    "size" : 622592,
    "uuid" : "6994e1d8-b3e5-38d6-aef0-721586b2d5ce",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/.dylibs\/libopenjp2.2.5.3.dylib",
    "name" : "libopenjp2.2.5.3.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4833984512,
    "size" : 98304,
    "uuid" : "5be17d28-46cf-3336-bfae-f315e9891018",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/.dylibs\/libz.1.3.1.zlib-ng.dylib",
    "name" : "libz.1.3.1.zlib-ng.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4915609600,
    "size" : 163840,
    "uuid" : "6fa02d7f-daaa-3c79-8b0d-c5319e003f3d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/.dylibs\/libxcb.1.1.0.dylib",
    "name" : "libxcb.1.1.0.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4916822016,
    "size" : 262144,
    "uuid" : "8dfe23b8-ad17-3d21-8c5e-5525cd8953db",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/.dylibs\/liblzma.5.dylib",
    "name" : "liblzma.5.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4812816384,
    "size" : 16384,
    "uuid" : "32a172ad-f11b-381b-9270-3f9a195cbe7f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/PIL\/.dylibs\/libXau.6.dylib",
    "name" : "libXau.6.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4920098816,
    "size" : 212992,
    "uuid" : "adc46467-3226-3781-9b3b-70c1c747858e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/matplotlib\/_path.cpython-39-darwin.so",
    "name" : "_path.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4923768832,
    "size" : 589824,
    "uuid" : "0f5cb38b-c2f8-30da-91e5-31a756dd5fc6",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/matplotlib\/ft2font.cpython-39-darwin.so",
    "name" : "ft2font.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4923539456,
    "size" : 114688,
    "uuid" : "71124f3e-5dce-30c7-9010-63e30c4c0520",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/kiwisolver\/_cext.cpython-39-darwin.so",
    "name" : "_cext.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4929814528,
    "size" : 229376,
    "uuid" : "5edf27d6-bb3d-3000-966f-6be2038bf55b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/matplotlib\/_image.cpython-39-darwin.so",
    "name" : "_image.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4860133376,
    "size" : 65536,
    "uuid" : "a3a21801-d9f3-331e-b87f-e91ebeccf742",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/multidict\/_multidict.cpython-39-darwin.so",
    "name" : "_multidict.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4923310080,
    "size" : 81920,
    "uuid" : "36e934ee-c120-395b-af57-d0d4c01a6760",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/yarl\/_quoting_c.cpython-39-darwin.so",
    "name" : "_quoting_c.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4917166080,
    "size" : 65536,
    "uuid" : "b13384eb-b7fc-32cf-8d54-bc8b0f65d4bd",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/propcache\/_helpers_c.cpython-39-darwin.so",
    "name" : "_helpers_c.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4934877184,
    "size" : 32768,
    "uuid" : "bbfd8fd9-2b08-3f7b-a7f3-791ec3f3f930",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/aiohttp\/_http_writer.cpython-39-darwin.so",
    "name" : "_http_writer.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4935368704,
    "size" : 262144,
    "uuid" : "81c7fbe1-ce76-37b8-bc63-caccbce3f931",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/aiohttp\/_http_parser.cpython-39-darwin.so",
    "name" : "_http_parser.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4826120192,
    "size" : 32768,
    "uuid" : "be905f48-56eb-33f7-b559-b0914d88caff",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/aiohttp\/_websocket\/mask.cpython-39-darwin.so",
    "name" : "mask.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4935761920,
    "size" : 131072,
    "uuid" : "9b837c85-99a2-3d1f-a07c-ef02ff8bdc9d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/aiohttp\/_websocket\/reader_c.cpython-39-darwin.so",
    "name" : "reader_c.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4936499200,
    "size" : 65536,
    "uuid" : "feeb7c6c-bb1f-3471-bd7a-73cb266f79d3",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/frozenlist\/_frozenlist.cpython-39-darwin.so",
    "name" : "_frozenlist.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4952719360,
    "size" : 65536,
    "uuid" : "d2ff9762-ad40-3c2d-8df7-35ae011fc7c3",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/_lib\/_ccallback_c.cpython-39-darwin.so",
    "name" : "_ccallback_c.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4957405184,
    "size" : 3227648,
    "uuid" : "6eb4e546-18ce-3c62-977b-3491edc1d682",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/_sparsetools.cpython-39-darwin.so",
    "name" : "_sparsetools.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4954456064,
    "size" : 475136,
    "uuid" : "cf45f738-0d13-3e01-bf68-430a59c1f08f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/_csparsetools.cpython-39-darwin.so",
    "name" : "_csparsetools.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4955586560,
    "size" : 311296,
    "uuid" : "6ad48c6c-bc1b-3591-97f8-e2874a4a92c4",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_fblas.cpython-39-darwin.so",
    "name" : "_fblas.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5078073344,
    "size" : 18235392,
    "uuid" : "00198043-5605-391a-8ef7-a1e9a3d1ac7a",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/.dylibs\/libopenblas.0.dylib",
    "name" : "libopenblas.0.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4963024896,
    "size" : 1376256,
    "uuid" : "ae3c441b-de1b-3bb8-8c6e-1a2411185d0e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/.dylibs\/libgfortran.5.dylib",
    "name" : "libgfortran.5.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4956143616,
    "size" : 262144,
    "uuid" : "81355d03-a464-3826-b89b-106d33d94d39",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/.dylibs\/libquadmath.0.dylib",
    "name" : "libquadmath.0.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4955029504,
    "size" : 65536,
    "uuid" : "ad4f9635-aa1c-370d-a9a6-8889ebb4d94b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/.dylibs\/libgcc_s.1.1.dylib",
    "name" : "libgcc_s.1.1.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4964876288,
    "size" : 983040,
    "uuid" : "da91db33-d7ae-3255-ad3d-2d98d311c095",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_flapack.cpython-39-darwin.so",
    "name" : "_flapack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4961173504,
    "size" : 393216,
    "uuid" : "5552de67-4c63-3f49-be74-41457f654521",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_cythonized_array_utils.cpython-39-darwin.so",
    "name" : "_cythonized_array_utils.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4961648640,
    "size" : 458752,
    "uuid" : "e984658e-55a1-3e34-8eaa-5256c49d521e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/cython_lapack.cpython-39-darwin.so",
    "name" : "cython_lapack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4956995584,
    "size" : 163840,
    "uuid" : "09d7669a-07cd-3c23-a157-0703c080c682",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_solve_toeplitz.cpython-39-darwin.so",
    "name" : "_solve_toeplitz.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4962353152,
    "size" : 147456,
    "uuid" : "6e1a890d-8b07-3fb5-b5ea-04681c854563",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_decomp_lu_cython.cpython-39-darwin.so",
    "name" : "_decomp_lu_cython.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4962566144,
    "size" : 147456,
    "uuid" : "8ca6d4e4-22ae-37ce-844a-d733fe952554",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_matfuncs_sqrtm_triu.cpython-39-darwin.so",
    "name" : "_matfuncs_sqrtm_triu.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4966989824,
    "size" : 311296,
    "uuid" : "58eb3a00-7b9c-3b61-907e-cc08583cf080",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_matfuncs_expm.cpython-39-darwin.so",
    "name" : "_matfuncs_expm.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4967383040,
    "size" : 180224,
    "uuid" : "107858bc-637d-3568-847f-221df1a8d0dd",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/cython_blas.cpython-39-darwin.so",
    "name" : "cython_blas.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4967956480,
    "size" : 229376,
    "uuid" : "4c64f3bf-0aa9-3934-a35a-2d07b1217607",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_decomp_update.cpython-39-darwin.so",
    "name" : "_decomp_update.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4968595456,
    "size" : 262144,
    "uuid" : "7163bc21-3a81-35ab-b955-25bacb78e312",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/linalg\/_dsolve\/_superlu.cpython-39-darwin.so",
    "name" : "_superlu.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4969431040,
    "size" : 360448,
    "uuid" : "ced47fb6-8bfe-37d5-b635-76a72e3c36cb",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/linalg\/_eigen\/arpack\/_arpack.cpython-39-darwin.so",
    "name" : "_arpack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4957224960,
    "size" : 81920,
    "uuid" : "b5c6dac3-44aa-3363-86d6-2fd531d165cc",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/linalg\/_propack\/_spropack.cpython-39-darwin.so",
    "name" : "_spropack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4962779136,
    "size" : 81920,
    "uuid" : "4d730e6b-87e0-3d13-9398-e4e03e53a02e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/linalg\/_propack\/_dpropack.cpython-39-darwin.so",
    "name" : "_dpropack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4968251392,
    "size" : 98304,
    "uuid" : "6a4d4aaf-403a-3b89-9365-1d991680b7f7",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/linalg\/_propack\/_cpropack.cpython-39-darwin.so",
    "name" : "_cpropack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4968939520,
    "size" : 98304,
    "uuid" : "b51e54ca-b2ae-3af3-a6f5-ba83a3f5ea21",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/linalg\/_propack\/_zpropack.cpython-39-darwin.so",
    "name" : "_zpropack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4970561536,
    "size" : 294912,
    "uuid" : "54c20cfd-84bf-3fab-8805-3b5af4e513cf",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/csgraph\/_shortest_path.cpython-39-darwin.so",
    "name" : "_shortest_path.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4970184704,
    "size" : 131072,
    "uuid" : "53a5568d-6b60-3f93-bb86-243d539fe3f2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/csgraph\/_tools.cpython-39-darwin.so",
    "name" : "_tools.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4971413504,
    "size" : 393216,
    "uuid" : "8ca85fa1-920b-3ffa-826e-5e64346423ca",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/csgraph\/_traversal.cpython-39-darwin.so",
    "name" : "_traversal.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4970938368,
    "size" : 147456,
    "uuid" : "6611dbe5-92ba-3158-835a-df707883eb5b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/csgraph\/_min_spanning_tree.cpython-39-darwin.so",
    "name" : "_min_spanning_tree.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4971888640,
    "size" : 196608,
    "uuid" : "392aec02-a55e-3f55-a255-a3541d156a52",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/csgraph\/_flow.cpython-39-darwin.so",
    "name" : "_flow.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4972642304,
    "size" : 212992,
    "uuid" : "7c507c67-d497-39ff-bd65-285d4b58f902",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/csgraph\/_matching.cpython-39-darwin.so",
    "name" : "_matching.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4972363776,
    "size" : 196608,
    "uuid" : "416c664a-ee1e-3558-81e7-16f8044db891",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/sparse\/csgraph\/_reordering.cpython-39-darwin.so",
    "name" : "_reordering.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4973576192,
    "size" : 540672,
    "uuid" : "dc292569-ccad-321a-b93f-69dc43b61832",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/spatial\/_ckdtree.cpython-39-darwin.so",
    "name" : "_ckdtree.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5059805184,
    "size" : 786432,
    "uuid" : "b27e258f-f310-3fba-87f2-a4ed6c0758a2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/spatial\/_qhull.cpython-39-darwin.so",
    "name" : "_qhull.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4935254016,
    "size" : 49152,
    "uuid" : "1a6dd70b-9a8f-3f56-9ed5-2ff2375cb01a",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/_lib\/messagestream.cpython-39-darwin.so",
    "name" : "messagestream.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4972150784,
    "size" : 131072,
    "uuid" : "f0748945-bf27-31f6-b16a-447670685fd7",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/spatial\/_voronoi.cpython-39-darwin.so",
    "name" : "_voronoi.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4955439104,
    "size" : 81920,
    "uuid" : "6db70aca-2f87-316a-8426-bb092686b551",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/spatial\/_distance_wrap.cpython-39-darwin.so",
    "name" : "_distance_wrap.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4972920832,
    "size" : 131072,
    "uuid" : "7a424ac8-1715-3b37-9f40-fbc51f41282a",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/spatial\/_hausdorff.cpython-39-darwin.so",
    "name" : "_hausdorff.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5061738496,
    "size" : 884736,
    "uuid" : "596aa827-0222-318f-8a67-baaaad840c9e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/special\/_ufuncs.cpython-39-darwin.so",
    "name" : "_ufuncs.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5058330624,
    "size" : 327680,
    "uuid" : "6c2ed104-0745-37e1-9f9c-8659dcc6686e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/special\/_ufuncs_cxx.cpython-39-darwin.so",
    "name" : "_ufuncs_cxx.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4973117440,
    "size" : 131072,
    "uuid" : "f8ab2561-dd82-3de4-895d-7f8799f2f04f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/special\/_cdflib.cpython-39-darwin.so",
    "name" : "_cdflib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5059411968,
    "size" : 180224,
    "uuid" : "998148fe-dafb-34fb-b830-a7000270ab8c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/special\/_specfun.cpython-39-darwin.so",
    "name" : "_specfun.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4830380032,
    "size" : 32768,
    "uuid" : "330bd195-4d59-3c15-9977-0f4020faee53",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/special\/_comb.cpython-39-darwin.so",
    "name" : "_comb.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4970381312,
    "size" : 65536,
    "uuid" : "e028919a-cfd3-376b-b834-eb67a487f042",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/special\/_ellip_harm_2.cpython-39-darwin.so",
    "name" : "_ellip_harm_2.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5062787072,
    "size" : 425984,
    "uuid" : "0e0b047e-606d-3e01-8dd9-4cd349c928b7",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/spatial\/_distance_pybind.cpython-39-darwin.so",
    "name" : "_distance_pybind.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5063360512,
    "size" : 622592,
    "uuid" : "995c503d-ea5a-3a35-a94e-d5ac3f96c668",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/spatial\/transform\/_rotation.cpython-39-darwin.so",
    "name" : "_rotation.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4974247936,
    "size" : 114688,
    "uuid" : "ae5fd338-595e-3219-9302-077d6ce1942c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/ndimage\/_nd_image.cpython-39-darwin.so",
    "name" : "_nd_image.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5064753152,
    "size" : 262144,
    "uuid" : "bf656840-09ea-3eee-801d-8724a5cacdfb",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/ndimage\/_ni_label.cpython-39-darwin.so",
    "name" : "_ni_label.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4858904576,
    "size" : 32768,
    "uuid" : "2e4160e1-05ab-30c4-a7f0-a3b949fe993d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_minpack2.cpython-39-darwin.so",
    "name" : "_minpack2.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4956766208,
    "size" : 49152,
    "uuid" : "ac5de565-ee02-3184-b89b-f5105cc99735",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_group_columns.cpython-39-darwin.so",
    "name" : "_group_columns.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5065719808,
    "size" : 212992,
    "uuid" : "3366f993-46d4-3e6f-8c12-e93a5c764401",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_trlib\/_trlib.cpython-39-darwin.so",
    "name" : "_trlib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5059657728,
    "size" : 81920,
    "uuid" : "bd97736a-b3a8-366b-860c-9295f03e6d11",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_lbfgsb.cpython-39-darwin.so",
    "name" : "_lbfgsb.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5061509120,
    "size" : 98304,
    "uuid" : "fb932be1-f87a-38b2-8340-ef9b26474b3f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_moduleTNC.cpython-39-darwin.so",
    "name" : "_moduleTNC.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4966858752,
    "size" : 65536,
    "uuid" : "94e55800-8326-36a7-88e2-fa588efbb397",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_cobyla.cpython-39-darwin.so",
    "name" : "_cobyla.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5059166208,
    "size" : 65536,
    "uuid" : "41fbe287-b41b-3ddf-897a-60becc216a51",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_slsqp.cpython-39-darwin.so",
    "name" : "_slsqp.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4956864512,
    "size" : 49152,
    "uuid" : "31f6425f-98fe-38ce-a817-6302fa93a722",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_minpack.cpython-39-darwin.so",
    "name" : "_minpack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5066031104,
    "size" : 131072,
    "uuid" : "de0dbe69-87d6-3fbd-8ea0-94ed3221715b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_lsq\/givens_elimination.cpython-39-darwin.so",
    "name" : "givens_elimination.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4404756480,
    "size" : 16384,
    "uuid" : "f1d4bb12-dcd2-3159-8dd4-29f3babdba4d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_zeros.cpython-39-darwin.so",
    "name" : "_zeros.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5073879040,
    "size" : 2686976,
    "uuid" : "32ed7d9f-d0c1-31b3-a2b1-2874e11fb213",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_highs\/_highs_wrapper.cpython-39-darwin.so",
    "name" : "_highs_wrapper.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4916740096,
    "size" : 32768,
    "uuid" : "ab030583-6d05-34b9-9d2b-812cae79af5c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_highs\/_highs_constants.cpython-39-darwin.so",
    "name" : "_highs_constants.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5068275712,
    "size" : 294912,
    "uuid" : "c9f4f965-c26f-3d68-b44b-0a28517eb12d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/linalg\/_interpolative.cpython-39-darwin.so",
    "name" : "_interpolative.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5069815808,
    "size" : 212992,
    "uuid" : "6a647c65-847d-34af-9d32-b01796e56ad9",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_bglu_dense.cpython-39-darwin.so",
    "name" : "_bglu_dense.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4923457536,
    "size" : 32768,
    "uuid" : "b4f8d4d1-7aa7-381f-8b80-21db1f3fd75c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_lsap.cpython-39-darwin.so",
    "name" : "_lsap.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5066686464,
    "size" : 98304,
    "uuid" : "cc9c208b-c59f-354a-b4b1-b3c9bc8f7142",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_pava_pybind.cpython-39-darwin.so",
    "name" : "_pava_pybind.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4929732608,
    "size" : 32768,
    "uuid" : "fb1fe974-ce25-3b5c-b660-058c2319fedc",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/optimize\/_direct.cpython-39-darwin.so",
    "name" : "_direct.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5065359360,
    "size" : 65536,
    "uuid" : "0f3a634d-04ac-31de-8860-6f98ab1bef7c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/integrate\/_odepack.cpython-39-darwin.so",
    "name" : "_odepack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5069127680,
    "size" : 81920,
    "uuid" : "0d4b0e73-da1f-3a85-91b2-649886cd619a",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/integrate\/_quadpack.cpython-39-darwin.so",
    "name" : "_quadpack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5071650816,
    "size" : 131072,
    "uuid" : "150fdb3d-f7a8-31ed-ae1f-f4c56c0a78d2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/integrate\/_vode.cpython-39-darwin.so",
    "name" : "_vode.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5069537280,
    "size" : 81920,
    "uuid" : "604f756e-2dc8-33bb-af1e-8da42ae0ee4a",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/integrate\/_dop.cpython-39-darwin.so",
    "name" : "_dop.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5070241792,
    "size" : 81920,
    "uuid" : "08d7a991-fbe7-3219-b738-bb0bb6fc375a",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/integrate\/_lsoda.cpython-39-darwin.so",
    "name" : "_lsoda.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5400805376,
    "size" : 458752,
    "uuid" : "e291d4ce-e422-3219-8bcd-af68ec94dadc",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_stats.cpython-39-darwin.so",
    "name" : "_stats.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5404393472,
    "size" : 1720320,
    "uuid" : "cb25e63b-c8cb-35d4-a96a-062dc48b85c6",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/special\/cython_special.cpython-39-darwin.so",
    "name" : "cython_special.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5077549056,
    "size" : 114688,
    "uuid" : "5235a646-3e24-394e-8efb-85c16c410318",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/beta_ufunc.cpython-39-darwin.so",
    "name" : "beta_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5077745664,
    "size" : 98304,
    "uuid" : "17a93990-02b9-3986-9845-5ea342dd0028",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/binom_ufunc.cpython-39-darwin.so",
    "name" : "binom_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5400100864,
    "size" : 98304,
    "uuid" : "e4531596-e1f3-3382-89cb-f1795de24efb",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/nbinom_ufunc.cpython-39-darwin.so",
    "name" : "nbinom_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5071323136,
    "size" : 81920,
    "uuid" : "a3eaa986-d84c-37fe-b7fa-44d8a2f3956e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/hypergeom_ufunc.cpython-39-darwin.so",
    "name" : "hypergeom_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5400444928,
    "size" : 81920,
    "uuid" : "947fca9d-4db3-3134-9ad7-f6ff3f108ba2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/ncf_ufunc.cpython-39-darwin.so",
    "name" : "ncf_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5401542656,
    "size" : 98304,
    "uuid" : "cb71ca30-70e7-3279-a1e0-96ef08ed37ba",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/ncx2_ufunc.cpython-39-darwin.so",
    "name" : "ncx2_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5401952256,
    "size" : 131072,
    "uuid" : "d756230c-9685-3e61-be72-05f26ac4dca2",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/nct_ufunc.cpython-39-darwin.so",
    "name" : "nct_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5068849152,
    "size" : 49152,
    "uuid" : "c2cb808c-f5ea-3447-9374-64fcfb85fdb4",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/skewnorm_ufunc.cpython-39-darwin.so",
    "name" : "skewnorm_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5401722880,
    "size" : 98304,
    "uuid" : "769a7561-b8e1-3910-8073-8fecf36bd241",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_boost\/invgauss_ufunc.cpython-39-darwin.so",
    "name" : "invgauss_ufunc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5072912384,
    "size" : 65536,
    "uuid" : "41f9081f-4398-33e5-ba22-cbfe3d04d1d8",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/interpolate\/_fitpack.cpython-39-darwin.so",
    "name" : "_fitpack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5408456704,
    "size" : 212992,
    "uuid" : "4c2955d3-3fb9-3748-8448-ec6e2f1ae0e3",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/interpolate\/dfitpack.cpython-39-darwin.so",
    "name" : "dfitpack.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5410127872,
    "size" : 376832,
    "uuid" : "37dad04a-f5c2-353d-b098-3133a5076f0e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/interpolate\/_bspl.cpython-39-darwin.so",
    "name" : "_bspl.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5409554432,
    "size" : 278528,
    "uuid" : "c80d9fcf-fadd-3186-8d2a-807307ac84c0",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/interpolate\/_ppoly.cpython-39-darwin.so",
    "name" : "_ppoly.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5410717696,
    "size" : 278528,
    "uuid" : "6672bc6c-0899-38fc-bbc8-af632c0aeca5",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/interpolate\/interpnd.cpython-39-darwin.so",
    "name" : "interpnd.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5409079296,
    "size" : 245760,
    "uuid" : "49063788-81ac-3111-a1bf-a98c313fda66",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/interpolate\/_rbfinterp_pythran.cpython-39-darwin.so",
    "name" : "_rbfinterp_pythran.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5408768000,
    "size" : 163840,
    "uuid" : "ca7ea6e5-3957-3d1f-bd83-b4f2c7c651dd",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/interpolate\/_rgi_cython.cpython-39-darwin.so",
    "name" : "_rgi_cython.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5412274176,
    "size" : 180224,
    "uuid" : "150fdc46-55ab-31fa-9e51-4b0659b11f1d",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_biasedurn.cpython-39-darwin.so",
    "name" : "_biasedurn.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4936630272,
    "size" : 32768,
    "uuid" : "4b874b1e-6f88-371f-937d-689014ad2927",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_levy_stable\/levyst.cpython-39-darwin.so",
    "name" : "levyst.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5401362432,
    "size" : 98304,
    "uuid" : "846d474f-2345-3972-bcce-f6eac3a44c16",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_stats_pythran.cpython-39-darwin.so",
    "name" : "_stats_pythran.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5399822336,
    "size" : 65536,
    "uuid" : "e1a49db6-5eaa-39c0-87a4-04b4d0f127ce",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/_lib\/_uarray\/_uarray.cpython-39-darwin.so",
    "name" : "_uarray.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5416140800,
    "size" : 655360,
    "uuid" : "b7c57958-2778-3c52-baf6-86f6531e04b4",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/fft\/_pocketfft\/pypocketfft.cpython-39-darwin.so",
    "name" : "pypocketfft.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5411340288,
    "size" : 147456,
    "uuid" : "4a830a5b-417e-3d0e-987d-e7b4bbf6a5dc",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_ansari_swilk_statistics.cpython-39-darwin.so",
    "name" : "_ansari_swilk_statistics.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5415665664,
    "size" : 245760,
    "uuid" : "ba64cbc7-d73e-318d-9845-3a0fc22080d9",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_sobol.cpython-39-darwin.so",
    "name" : "_sobol.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5414666240,
    "size" : 163840,
    "uuid" : "f737016d-bf86-3adc-86c5-81bc9e688da3",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_qmc_cy.cpython-39-darwin.so",
    "name" : "_qmc_cy.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5418598400,
    "size" : 65536,
    "uuid" : "ac395167-668b-3d13-bd94-bd3bebe86329",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_mvn.cpython-39-darwin.so",
    "name" : "_mvn.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5417730048,
    "size" : 180224,
    "uuid" : "3f838b45-9a3b-3439-9f42-963435cc353c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_rcont\/rcont.cpython-39-darwin.so",
    "name" : "rcont.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5422202880,
    "size" : 1032192,
    "uuid" : "8960cef1-9c85-3d1c-85b9-44561f8cac32",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/scipy\/stats\/_unuran\/unuran_wrapper.cpython-39-darwin.so",
    "name" : "unuran_wrapper.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5425954816,
    "size" : 688128,
    "uuid" : "1f17e9f9-30bf-3330-ba79-6bd9cb7f08ee",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/rpds\/rpds.cpython-39-darwin.so",
    "name" : "rpds.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 5059280896,
    "size" : 32768,
    "uuid" : "75343fe3-84d4-3b23-9c84-cec8f6719f12",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/psutil\/_psutil_osx.abi3.so",
    "name" : "_psutil_osx.abi3.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4407803904,
    "size" : 16384,
    "uuid" : "8114b100-139b-377b-b475-99f6dc33b187",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/psutil\/_psutil_posix.abi3.so",
    "name" : "_psutil_posix.abi3.so"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6933569536,
    "size" : 246960,
    "uuid" : "5e7de3d9-6e8a-3cd7-aa53-523e7e474157",
    "path" : "\/usr\/lib\/system\/libsystem_kernel.dylib",
    "name" : "libsystem_kernel.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6933819392,
    "size" : 51900,
    "uuid" : "f37b8a66-9bab-32a0-b222-76d650a69d19",
    "path" : "\/usr\/lib\/system\/libsystem_pthread.dylib",
    "name" : "libsystem_pthread.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6932320256,
    "size" : 532552,
    "uuid" : "781016be-85b8-3d8f-8698-c02c17adc7a3",
    "path" : "\/usr\/lib\/system\/libsystem_c.dylib",
    "name" : "libsystem_c.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6929846272,
    "size" : 651112,
    "uuid" : "0b370235-e5de-3f28-b9a1-fb3dad42b317",
    "path" : "\/usr\/lib\/dyld",
    "name" : "dyld"
  },
  {
    "size" : 0,
    "source" : "A",
    "base" : 0,
    "uuid" : "00000000-0000-0000-0000-000000000000"
  }
],
  "sharedCache" : {
  "base" : 6928760832,
  "size" : 5585453056,
  "uuid" : "d6964fd6-816a-39a1-88ec-49cb87145dd1"
},
  "legacyInfo" : {
  "threadTriggered" : {
    "queue" : "com.apple.main-thread"
  }
},
  "logWritingSignature" : "d45f23e72bac9c55abe9486ef9444fa4aa4c6fd3",
  "trialInfo" : {
  "rollouts" : [
    {
      "rolloutId" : "645197bf528fbf3c3af54105",
      "factorPackIds" : [
        "663e65b4a1526e1ca0e288a1"
      ],
      "deploymentId" : 240000002
    },
    {
      "rolloutId" : "67181b10c68c361a728c7cfa",
      "factorPackIds" : [

      ],
      "deploymentId" : 250000003
    }
  ],
  "experiments" : [

  ]
}
}

Model: Mac16,13, BootROM 13822.40.107.0.1, proc 10:4:6 processors, 16 GB, SMC 
Graphics: Apple M4, Apple M4, Built-In
Display: Color LCD, spdisplays_2880x1864Retina, Main, MirrorOff, Online
Memory Module: LPDDR5, Micron
AirPort: spairport_wireless_card_type_wifi (0x14E4, 0x4388), wl0: Sep 22 2025 23:12:38 version 23.41.6.0.41.51.199 FWID 01-c9b7802d
IO80211_driverkit-1530.15 "IO80211_driverkit-1530.15" Sep 28 2025 21:32:04
AirPort: 
Bluetooth: Version (null), 0 services, 0 devices, 0 incoming serial ports
Network Service: Ethernet Adapter (en3), Ethernet, en3
Network Service: Ethernet Adapter (en4), Ethernet, en4
Network Service: Wi-Fi, AirPort, en0
Thunderbolt Bus: MacBook Air, Apple Inc.
Thunderbolt Bus: MacBook Air, Apple Inc.
