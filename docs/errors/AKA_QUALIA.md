---
status: wip
type: documentation
---
-------------------------------------
Translated Report (Full Report Below)
-------------------------------------
Process:             Python [30746]
Path:                /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
Identifier:          com.apple.python3
Version:             3.9.6 (3.9.6)
Build Info:          python3-141000000500005~558
Code Type:           ARM-64 (Native)
Role:                Unspecified
Parent Process:      Exited process [30744]
Coalition:           com.googlecode.iterm2 [2976]
Responsible Process: iTerm2 [82031]
User ID:             501

Date/Time:           2025-09-08 02:09:44.3728 +0100
Launch Time:         2025-09-08 02:09:43.9550 +0100
Hardware Model:      Mac16,13
OS Version:          macOS 26.0 (25A5351b)
Release Type:        User

Crash Reporter Key:  4E207357-19A3-A70F-DAD5-7940E32325FE
Incident Identifier: F1E5B336-5F7D-416F-8965-8B95B4F60D7B

Sleep/Wake UUID:       89A526E4-FDDB-41F1-9A6E-D69187D9F26A

Time Awake Since Boot: 35000 seconds
Time Since Wake:       19908 seconds

System Integrity Protection: enabled

Triggered by Thread: 1

Exception Type:    EXC_BAD_ACCESS (SIGSEGV)
Exception Subtype: KERN_INVALID_ADDRESS at 0x0000000c00000009
Exception Codes:   0x0000000000000001, 0x0000000c00000009

Termination Reason:  Namespace SIGNAL, Code 11, Segmentation fault: 11
Terminating Process: exc handler [30746]


VM Region Info: 0xc00000009 is not in any region.  Bytes after previous region: 5200936970  Bytes before following region: 16106127351
      REGION TYPE                    START - END         [ VSIZE] PRT/MAX SHRMOD  REGION DETAIL
      commpage (reserved)         7cbc00000-aca000000    [ 12.0G] ---/--- SM=NUL  reserved VM address space (unallocated)
--->  GAP OF 0x4f6000000 BYTES
      GPU Carveout (reserved)     fc0000000-1000000000   [  1.0G] ---/--- SM=NUL  reserved VM address space (unallocated)

Thread 0:
0   libsystem_kernel.dylib        	       0x19d29f4f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d2df09c _pthread_cond_wait + 984
2   Python3                       	       0x10271c30c PyThread_acquire_lock_timed + 540
3   Python3                       	       0x10276b150 0x1025bc000 + 1765712
4   Python3                       	       0x10276ae34 0x1025bc000 + 1764916
5   Python3                       	       0x1026063e4 0x1025bc000 + 304100
6   Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
7   Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
8   Python3                       	       0x1026d3134 0x1025bc000 + 1143092
9   Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
10  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
11  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
12  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
13  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
14  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
15  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
16  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
17  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
18  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
19  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
20  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
21  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
22  Python3                       	       0x1026ce56c _PyEval_EvalFrameDefault + 10964
23  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
24  Python3                       	       0x1026cb9d0 PyEval_EvalCode + 80
25  Python3                       	       0x10270f118 0x1025bc000 + 1388824
26  Python3                       	       0x10270f308 0x1025bc000 + 1389320
27  Python3                       	       0x10270dad0 PyRun_SimpleFileExFlags + 812
28  Python3                       	       0x10272ad0c Py_RunMain + 1448
29  Python3                       	       0x10272b0c0 0x1025bc000 + 1503424
30  Python3                       	       0x10272b160 Py_BytesMain + 40
31  dyld                          	       0x19cf21924 start + 6400

Thread 1 Crashed:
0   libsqlite3.dylib              	       0x1a52002d0 sqlite3DbMallocRawNNTyped + 52
1   libsqlite3.dylib              	       0x1a51911c4 exprDup + 168
2   libsqlite3.dylib              	       0x1a5233a74 sqlite3ExprCodeRunJustOnce + 172
3   libsqlite3.dylib              	       0x1a5239750 sqlite3ExprCodeFactorable + 148
4   libsqlite3.dylib              	       0x1a519ccf0 sqlite3Insert + 5548
5   libsqlite3.dylib              	       0x1a5159b94 yy_reduce + 6860
6   libsqlite3.dylib              	       0x1a5157084 sqlite3RunParser + 796
7   libsqlite3.dylib              	       0x1a5156550 sqlite3Prepare + 472
8   libsqlite3.dylib              	       0x1a51561ec sqlite3LockAndPrepare + 224
9   _sqlite3.cpython-39-darwin.so 	       0x10a07837c 0x10a070000 + 33660
10  _sqlite3.cpython-39-darwin.so 	       0x10a073c18 0x10a070000 + 15384
11  Python3                       	       0x1025fd36c _PyObject_MakeTpCall + 356
12  Python3                       	       0x1025fe41c 0x1025bc000 + 271388
13  Python3                       	       0x1025fe54c _PyObject_CallFunction_SizeT + 52
14  _sqlite3.cpython-39-darwin.so 	       0x10a071a58 0x10a070000 + 6744
15  _sqlite3.cpython-39-darwin.so 	       0x10a07584c 0x10a070000 + 22604
16  Python3                       	       0x10260625c 0x1025bc000 + 303708
17  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 10
18  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
19  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
20  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
21  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 9
22  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
23  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
24  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 8
--------
-------- ELIDED 4 LEVELS OF RECURSION THROUGH 0x1026d23dc 0x1025bc000 + 1139676
--------
41  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
42  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
43  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
44  Python3                       	       0x1025ffe94 0x1025bc000 + 278164
45  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 3
46  Python3                       	       0x1026ccda8 _PyEval_EvalFrameDefault + 4880
47  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
48  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
49  Python3                       	       0x1026ce17c _PyEval_EvalFrameDefault + 9956
50  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
51  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 2
52  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
53  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
54  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 1
55  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
56  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
57  Python3                       	       0x1025fff1c 0x1025bc000 + 278300
58  Python3                       	       0x10276be0c 0x1025bc000 + 1768972
59  Python3                       	       0x10271bec8 0x1025bc000 + 1441480
60  libsystem_pthread.dylib       	       0x19d2debc8 _pthread_start + 136
61  libsystem_pthread.dylib       	       0x19d2d9b80 thread_start + 8

Thread 2:
0   libsystem_kernel.dylib        	       0x19d29f4f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d2df09c _pthread_cond_wait + 984
2   Python3                       	       0x1026cab2c 0x1025bc000 + 1108780
3   Python3                       	       0x1026cb1dc PyEval_RestoreThread + 24
4   Python3                       	       0x102727930 _Py_read + 92
5   Python3                       	       0x10271295c 0x1025bc000 + 1403228
6   Python3                       	       0x10273a4f8 0x1025bc000 + 1565944
7   Python3                       	       0x102641180 0x1025bc000 + 545152
8   Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
9   Python3                       	       0x1026cdcb0 _PyEval_EvalFrameDefault + 8728
10  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
11  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
12  Python3                       	       0x1026cdcb0 _PyEval_EvalFrameDefault + 8728
13  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
14  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
15  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
16  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
17  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
18  Python3                       	       0x1025ffe94 0x1025bc000 + 278164
19  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
20  Python3                       	       0x1026ccda8 _PyEval_EvalFrameDefault + 4880
21  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
22  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
23  Python3                       	       0x1026ce17c _PyEval_EvalFrameDefault + 9956
24  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
25  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
26  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
27  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
28  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
29  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
30  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
31  Python3                       	       0x1025fff1c 0x1025bc000 + 278300
32  Python3                       	       0x10276be0c 0x1025bc000 + 1768972
33  Python3                       	       0x10271bec8 0x1025bc000 + 1441480
34  libsystem_pthread.dylib       	       0x19d2debc8 _pthread_start + 136
35  libsystem_pthread.dylib       	       0x19d2d9b80 thread_start + 8

Thread 3:
0   libsystem_kernel.dylib        	       0x19d29f4f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d2df09c _pthread_cond_wait + 984
2   Python3                       	       0x1026cab2c 0x1025bc000 + 1108780
3   Python3                       	       0x1026cb1dc PyEval_RestoreThread + 24
4   Python3                       	       0x102727930 _Py_read + 92
5   Python3                       	       0x10271295c 0x1025bc000 + 1403228
6   Python3                       	       0x10273a4f8 0x1025bc000 + 1565944
7   Python3                       	       0x102641180 0x1025bc000 + 545152
8   Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
9   Python3                       	       0x1026cdcb0 _PyEval_EvalFrameDefault + 8728
10  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
11  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
12  Python3                       	       0x1026cdcb0 _PyEval_EvalFrameDefault + 8728
13  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
14  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
15  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
16  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
17  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
18  Python3                       	       0x1025ffe94 0x1025bc000 + 278164
19  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
20  Python3                       	       0x1026ccda8 _PyEval_EvalFrameDefault + 4880
21  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
22  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
23  Python3                       	       0x1026ce17c _PyEval_EvalFrameDefault + 9956
24  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
25  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
26  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
27  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
28  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
29  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
30  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
31  Python3                       	       0x1025fff1c 0x1025bc000 + 278300
32  Python3                       	       0x10276be0c 0x1025bc000 + 1768972
33  Python3                       	       0x10271bec8 0x1025bc000 + 1441480
34  libsystem_pthread.dylib       	       0x19d2debc8 _pthread_start + 136
35  libsystem_pthread.dylib       	       0x19d2d9b80 thread_start + 8

Thread 4:
0   libsystem_kernel.dylib        	       0x19d29f4f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d2df09c _pthread_cond_wait + 984
2   Python3                       	       0x1026cab2c 0x1025bc000 + 1108780
3   Python3                       	       0x1026cb1dc PyEval_RestoreThread + 24
4   _sqlite3.cpython-39-darwin.so 	       0x10a075d8c 0x10a070000 + 23948
5   Python3                       	       0x10260625c 0x1025bc000 + 303708
6   Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 10
7   Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
8   Python3                       	       0x1026d3134 0x1025bc000 + 1143092
9   Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
10  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 9
11  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
12  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
13  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 8
--------
-------- ELIDED 4 LEVELS OF RECURSION THROUGH 0x1026d23dc 0x1025bc000 + 1139676
--------
30  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
31  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
32  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
33  Python3                       	       0x1025ffe94 0x1025bc000 + 278164
34  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 3
35  Python3                       	       0x1026ccda8 _PyEval_EvalFrameDefault + 4880
36  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
37  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
38  Python3                       	       0x1026ce17c _PyEval_EvalFrameDefault + 9956
39  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
40  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 2
41  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
42  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
43  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 1
44  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
45  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
46  Python3                       	       0x1025fff1c 0x1025bc000 + 278300
47  Python3                       	       0x10276be0c 0x1025bc000 + 1768972
48  Python3                       	       0x10271bec8 0x1025bc000 + 1441480
49  libsystem_pthread.dylib       	       0x19d2debc8 _pthread_start + 136
50  libsystem_pthread.dylib       	       0x19d2d9b80 thread_start + 8

Thread 5:
0   libsystem_kernel.dylib        	       0x19d29f4f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d2df09c _pthread_cond_wait + 984
2   Python3                       	       0x1026cab2c 0x1025bc000 + 1108780
3   Python3                       	       0x1026cb1dc PyEval_RestoreThread + 24
4   _sqlite3.cpython-39-darwin.so 	       0x10a078d00 0x10a070000 + 36096
5   _sqlite3.cpython-39-darwin.so 	       0x10a075df8 0x10a070000 + 24056
6   Python3                       	       0x10260625c 0x1025bc000 + 303708
7   Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 10
8   Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
9   Python3                       	       0x1026d3134 0x1025bc000 + 1143092
10  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
11  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 9
12  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
13  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
14  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 8
--------
-------- ELIDED 4 LEVELS OF RECURSION THROUGH 0x1026d23dc 0x1025bc000 + 1139676
--------
31  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
32  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
33  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
34  Python3                       	       0x1025ffe94 0x1025bc000 + 278164
35  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 3
36  Python3                       	       0x1026ccda8 _PyEval_EvalFrameDefault + 4880
37  Python3                       	       0x1026d3134 0x1025bc000 + 1143092
38  Python3                       	       0x1025fdbd8 _PyFunction_Vectorcall + 228
39  Python3                       	       0x1026ce17c _PyEval_EvalFrameDefault + 9956
40  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
41  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 2
42  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
43  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
44  Python3                       	       0x1026d23dc 0x1025bc000 + 1139676
-------- RECURSION LEVEL 1
45  Python3                       	       0x1026cdc88 _PyEval_EvalFrameDefault + 8688
46  Python3                       	       0x1025fdd6c 0x1025bc000 + 269676
47  Python3                       	       0x1025fff1c 0x1025bc000 + 278300
48  Python3                       	       0x10276be0c 0x1025bc000 + 1768972
49  Python3                       	       0x10271bec8 0x1025bc000 + 1441480
50  libsystem_pthread.dylib       	       0x19d2debc8 _pthread_start + 136
51  libsystem_pthread.dylib       	       0x19d2d9b80 thread_start + 8

Thread 6:
0   libsystem_kernel.dylib        	       0x19d29f4f8 __psynch_cvwait + 8
1   libsystem_pthread.dylib       	       0x19d2df09c _pthread_cond_wait + 984
2   Python3                       	       0x1026cab2c 0x1025bc000 + 1108780
3   Python3                       	       0x1026cb034 PyEval_AcquireThread + 24
4   Python3                       	       0x10276bdf0 0x1025bc000 + 1768944
5   Python3                       	       0x10271bec8 0x1025bc000 + 1441480
6   libsystem_pthread.dylib       	       0x19d2debc8 _pthread_start + 136
7   libsystem_pthread.dylib       	       0x19d2d9b80 thread_start + 8


Thread 1 crashed with ARM Thread State (64-bit):
    x0: 0x00000007c950ea00   x1: 0x0000000000000068   x2: 0x00000000150bf456   x3: 0x000000019d2e5984
    x4: 0x0000000000000000   x5: 0x0000000000000007   x6: 0x000000016e8e4244   x7: 0x000000000000000b
    x8: 0x0000000c00000009   x9: 0x0000000000000028  x10: 0x0000000000000006  x11: 0x00000000fffffffe
   x12: 0x0000000000000003  x13: 0x0000000000000001  x14: 0x0000000000000001  x15: 0x00000007cabe1168
   x16: 0x000000019d2e5a40  x17: 0x000000020b1a90d8  x18: 0x0000000000000000  x19: 0x0000000000000000
   x20: 0x00000007c950ea00  x21: 0x00000007cb811000  x22: 0x0000000000000000  x23: 0x0000000000000000
   x24: 0x0000000000000006  x25: 0x000000016e8e4d78  x26: 0x0000000000000011  x27: 0x00000007c96d0080
   x28: 0x00000007cabe1160   fp: 0x000000016e8e4060   lr: 0x00000001a51911c4
    sp: 0x000000016e8e4000   pc: 0x00000001a52002d0 cpsr: 0x80000000
   far: 0x0000000c00000009  esr: 0x92000006 (Data Abort) byte read Translation fault

Binary Images:
       0x102520000 -        0x102523fff com.apple.python3 (3.9.6) <808d48a0-1c2f-33bd-853f-9ae290dc4d95> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
       0x1025bc000 -        0x10281ffff com.apple.python3 (3.9.6) <0f563628-0fa8-30c9-9520-6e975bc8d93f> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Python3
       0x102bc4000 -        0x102bcbfff _heapq.cpython-39-darwin.so (*) <7b30aed2-0503-34fe-8a70-cc11cc935f05> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_heapq.cpython-39-darwin.so
       0x102bdc000 -        0x102be3fff zlib.cpython-39-darwin.so (*) <78031110-ab0e-3594-9955-fe8bd7cc3796> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/zlib.cpython-39-darwin.so
       0x107528000 -        0x10752bfff _bz2.cpython-39-darwin.so (*) <19bbc1ec-dc6d-3210-98f2-ed33c96916c0> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_bz2.cpython-39-darwin.so
       0x10753c000 -        0x107543fff _lzma.cpython-39-darwin.so (*) <ac8a4c97-44d3-3daa-bde1-7dd588b5dea7> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_lzma.cpython-39-darwin.so
       0x107554000 -        0x107557fff grp.cpython-39-darwin.so (*) <1c8a23f9-d152-35a9-8d7b-e1e5582632ac> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/grp.cpython-39-darwin.so
       0x1028c8000 -        0x1028d3fff math.cpython-39-darwin.so (*) <8e9c0437-ae12-3d89-8222-ac85ff6f2050> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/math.cpython-39-darwin.so
       0x1028e4000 -        0x1028e7fff _bisect.cpython-39-darwin.so (*) <9628500f-d3ad-3c77-a8cf-4670c10c510c> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_bisect.cpython-39-darwin.so
       0x10758c000 -        0x10758ffff _random.cpython-39-darwin.so (*) <4bbfa841-1a4a-37b6-a25d-c980c28e7680> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_random.cpython-39-darwin.so
       0x107568000 -        0x10756ffff _sha512.cpython-39-darwin.so (*) <beb14a7b-b3de-3aa1-b17e-39f34b441f4e> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_sha512.cpython-39-darwin.so
       0x107604000 -        0x107607fff _queue.cpython-39-darwin.so (*) <a9f5f2a6-4ac2-3195-9e4b-ebe07c0f769d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_queue.cpython-39-darwin.so
       0x1075e0000 -        0x1075e7fff _struct.cpython-39-darwin.so (*) <49ae3103-4e55-3f3b-89a3-6ed59d03a908> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_struct.cpython-39-darwin.so
       0x107704000 -        0x10770bfff binascii.cpython-39-darwin.so (*) <b3b0aed3-f8cb-37a4-ae0b-23e469841bea> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/binascii.cpython-39-darwin.so
       0x10771c000 -        0x107723fff _hashlib.cpython-39-darwin.so (*) <0e923671-4fb5-3cf1-b25b-62823af87f90> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_hashlib.cpython-39-darwin.so
       0x1076d8000 -        0x1076e3fff _blake2.cpython-39-darwin.so (*) <e0f957a1-bee3-3e36-8c74-31e2adefe2bb> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_blake2.cpython-39-darwin.so
       0x107774000 -        0x107783fff _sha3.cpython-39-darwin.so (*) <0eb51e69-389e-3de8-bad1-1d5ab698a265> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_sha3.cpython-39-darwin.so
       0x1077f8000 -        0x1077fbfff _opcode.cpython-39-darwin.so (*) <cf8e29c4-8f70-34bf-9792-644a7d06316e> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_opcode.cpython-39-darwin.so
       0x10784c000 -        0x10784ffff _posixsubprocess.cpython-39-darwin.so (*) <53de3c57-b242-399b-a604-24715f8b6c5d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_posixsubprocess.cpython-39-darwin.so
       0x1077d4000 -        0x1077dbfff select.cpython-39-darwin.so (*) <ec97e380-290c-31c0-bc27-516cf02fc85a> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/select.cpython-39-darwin.so
       0x107924000 -        0x107937fff _datetime.cpython-39-darwin.so (*) <6db62488-f4b5-37a5-935a-83567e6d83ab> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_datetime.cpython-39-darwin.so
       0x107974000 -        0x10797bfff _csv.cpython-39-darwin.so (*) <de17005f-a5be-3a2e-9691-0c1b1873c1fd> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_csv.cpython-39-darwin.so
       0x107948000 -        0x107957fff _socket.cpython-39-darwin.so (*) <35ca3347-d6a5-35e3-9477-6a3ccb283d23> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_socket.cpython-39-darwin.so
       0x107a40000 -        0x107a4bfff array.cpython-39-darwin.so (*) <ff860554-95bd-339d-96aa-e2846057a0d2> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/array.cpython-39-darwin.so
       0x107adc000 -        0x107adffff _contextvars.cpython-39-darwin.so (*) <49034e2f-bb91-3f9e-96fe-9f7606a1d9c2> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_contextvars.cpython-39-darwin.so
       0x107b90000 -        0x107bc7fff _message.abi3.so (*) <efc9bb47-4ab7-37e1-ac93-f1c928b2fb91> /Users/USER/Library/Python/3.9/lib/python/site-packages/google/_upb/_message.abi3.so
       0x107a0c000 -        0x107a23fff _pickle.cpython-39-darwin.so (*) <2bde962c-7928-359c-aa25-ac85a8b926c9> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_pickle.cpython-39-darwin.so
       0x107d80000 -        0x107d97fff _ssl.cpython-39-darwin.so (*) <b6b6cf56-cf37-3842-b979-1a70fd5b10dd> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_ssl.cpython-39-darwin.so
       0x107b70000 -        0x107b7bfff _asyncio.cpython-39-darwin.so (*) <5f18ee52-c95b-352e-b19d-5b09e63be3a1> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_asyncio.cpython-39-darwin.so
       0x107d64000 -        0x107d6bfff _json.cpython-39-darwin.so (*) <d6ec7673-c6b2-3cd0-aa68-0af178167af5> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_json.cpython-39-darwin.so
       0x107f14000 -        0x107f17fff _uuid.cpython-39-darwin.so (*) <6c7beb54-585b-3582-80b3-8425443e993d> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_uuid.cpython-39-darwin.so
       0x10828c000 -        0x1082cffff _decimal.cpython-39-darwin.so (*) <74560b51-827c-3636-bbb9-d0c73b90fec2> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_decimal.cpython-39-darwin.so
       0x109738000 -        0x109acbfff _pydantic_core.cpython-39-darwin.so (*) <8a370734-3093-332f-8582-b45fd9efee3f> /Users/USER/Library/Python/3.9/lib/python/site-packages/pydantic_core/_pydantic_core.cpython-39-darwin.so
       0x107ef0000 -        0x107ef7fff _zoneinfo.cpython-39-darwin.so (*) <56a26b83-6e8e-3d80-b3fa-9e48be682dac> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_zoneinfo.cpython-39-darwin.so
       0x1076f4000 -        0x1076f7fff md.cpython-39-darwin.so (*) <c6c0ba3a-867b-3d25-804c-427cd0223ba6> /Users/USER/Library/Python/3.9/lib/python/site-packages/charset_normalizer/md.cpython-39-darwin.so
       0x109b14000 -        0x109b3bfff md__mypyc.cpython-39-darwin.so (*) <a0a8f051-3e84-34d3-9804-42911ae70d3c> /Users/USER/Library/Python/3.9/lib/python/site-packages/charset_normalizer/md__mypyc.cpython-39-darwin.so
       0x109f10000 -        0x10a01ffff unicodedata.cpython-39-darwin.so (*) <d13600ad-15f6-3df0-9366-b00b8e51fbe7> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/unicodedata.cpython-39-darwin.so
       0x108268000 -        0x10826ffff _multibytecodec.cpython-39-darwin.so (*) <2ee10d7f-142f-3679-9461-3f8ac5cbb6d6> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_multibytecodec.cpython-39-darwin.so
       0x109720000 -        0x109723fff _scproxy.cpython-39-darwin.so (*) <acb15f58-f305-35c9-aeba-ca4a2fdbf959> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_scproxy.cpython-39-darwin.so
       0x109dec000 -        0x109e2bfff _yaml.cpython-39-darwin.so (*) <28d7d63e-0ac7-3dd0-b8fa-ca45281fac44> /Users/USER/Library/Python/3.9/lib/python/site-packages/yaml/_yaml.cpython-39-darwin.so
       0x109dd4000 -        0x109ddbfff mmap.cpython-39-darwin.so (*) <69d1a887-f91d-395a-9f3c-1038698321da> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/mmap.cpython-39-darwin.so
       0x10a094000 -        0x10a097fff resource.cpython-39-darwin.so (*) <e8d33c43-c414-32f1-bb90-2afea3c8e6ef> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/resource.cpython-39-darwin.so
       0x10a128000 -        0x10a14ffff collections.cpython-39-darwin.so (*) <e967e075-c022-38e0-b8ae-9f708eea9307> /Users/USER/Library/Python/3.9/lib/python/site-packages/sqlalchemy/cyextension/collections.cpython-39-darwin.so
       0x10a0e8000 -        0x10a0f7fff immutabledict.cpython-39-darwin.so (*) <020c57e8-f97a-35ce-ae1f-58c4d26dac92> /Users/USER/Library/Python/3.9/lib/python/site-packages/sqlalchemy/cyextension/immutabledict.cpython-39-darwin.so
       0x10a108000 -        0x10a113fff processors.cpython-39-darwin.so (*) <f641a2b0-5739-337f-a0d3-2ad757c7879e> /Users/USER/Library/Python/3.9/lib/python/site-packages/sqlalchemy/cyextension/processors.cpython-39-darwin.so
       0x10a168000 -        0x10a173fff resultproxy.cpython-39-darwin.so (*) <99470441-19dc-3f03-9b47-67ad20481b03> /Users/USER/Library/Python/3.9/lib/python/site-packages/sqlalchemy/cyextension/resultproxy.cpython-39-darwin.so
       0x10a184000 -        0x10a193fff util.cpython-39-darwin.so (*) <ab97462c-1da2-3010-a82d-26105078c95b> /Users/USER/Library/Python/3.9/lib/python/site-packages/sqlalchemy/cyextension/util.cpython-39-darwin.so
       0x10a070000 -        0x10a07bfff _sqlite3.cpython-39-darwin.so (*) <2a4818bb-3251-3d4d-a31a-dad940ff8659> /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/lib-dynload/_sqlite3.cpython-39-darwin.so
       0x19d29b000 -        0x19d2d745f libsystem_kernel.dylib (*) <2eb73bf1-8c71-3e1f-a160-6da83dc82606> /usr/lib/system/libsystem_kernel.dylib
       0x19d2d8000 -        0x19d2e4a67 libsystem_pthread.dylib (*) <6f3be508-fbaf-31d0-868b-fc5b5c9bc54c> /usr/lib/system/libsystem_pthread.dylib
       0x19cf19000 -        0x19cfb76db dyld (*) <0c2c14a0-a9e6-3a10-b39e-68d30d14e66c> /usr/lib/dyld
               0x0 - 0xffffffffffffffff ??? (*) <00000000-0000-0000-0000-000000000000> ???
       0x1a514d000 -        0x1a53343a3 libsqlite3.dylib (*) <a21dba03-168f-3a84-a03e-23c7d401b562> /usr/lib/libsqlite3.dylib
       0x19d2e5000 -        0x19d2ed05f libsystem_platform.dylib (*) <aac0cf6e-b9cd-3367-a544-a9ac62716721> /usr/lib/system/libsystem_platform.dylib

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

VM Region Summary:
ReadOnly portion of Libraries: Total=888.6M resident=0K(0%) swapped_out_or_unallocated=888.6M(100%)
Writable regions: Total=296.8M written=320K(0%) resident=320K(0%) swapped_out=0K(0%) unallocated=296.5M(100%)

                                VIRTUAL   REGION 
REGION TYPE                        SIZE    COUNT (non-coalesced) 
===========                     =======  ======= 
Activity Tracing                   256K        1 
ColorSync                           32K        2 
Kernel Alloc Once                   32K        1 
MALLOC                           124.0M       22 
MALLOC guard page                 3744K        4 
SQLite page cache                  128K        1 
STACK GUARD                        112K        7 
Stack                            128.2M        8 
Stack Guard                         16K        1 
VM_ALLOCATE                       44.3M      177 
__AUTH                            1311K      148 
__AUTH_CONST                      17.6M      347 
__CTF                               824        1 
__DATA                            5121K      352 
__DATA_CONST                      16.1M      395 
__DATA_DIRTY                      1314K      290 
__FONT_DATA                        2352        1 
__LINKEDIT                       594.8M       49 
__OBJC_RO                         78.1M        1 
__OBJC_RW                         2560K        1 
__TEXT                           293.7M      404 
__TPRO_CONST                       128K        2 
dyld private memory                160K        2 
mapped file                         80K        1 
page table in kernel               320K        1 
shared memory                       96K        4 
===========                     =======  ======= 
TOTAL                              1.3G     2223 


-----------
Full Report
-----------

{"app_name":"Python","timestamp":"2025-09-08 02:09:45.00 +0100","app_version":"3.9.6","slice_uuid":"808d48a0-1c2f-33bd-853f-9ae290dc4d95","build_version":"3.9.6","platform":1,"bundleID":"com.apple.python3","share_with_app_devs":1,"is_first_party":0,"bug_type":"309","os_version":"macOS 26.0 (25A5351b)","roots_installed":0,"name":"Python","incident_id":"F1E5B336-5F7D-416F-8965-8B95B4F60D7B"}
{
  "uptime" : 35000,
  "procRole" : "Unspecified",
  "version" : 2,
  "userID" : 501,
  "deployVersion" : 210,
  "modelCode" : "Mac16,13",
  "coalitionID" : 2976,
  "osVersion" : {
    "train" : "macOS 26.0",
    "build" : "25A5351b",
    "releaseType" : "User"
  },
  "captureTime" : "2025-09-08 02:09:44.3728 +0100",
  "codeSigningMonitor" : 2,
  "incident" : "F1E5B336-5F7D-416F-8965-8B95B4F60D7B",
  "pid" : 30746,
  "translated" : false,
  "cpuType" : "ARM-64",
  "roots_installed" : 0,
  "bug_type" : "309",
  "procLaunch" : "2025-09-08 02:09:43.9550 +0100",
  "procStartAbsTime" : 850442323718,
  "procExitAbsTime" : 850452345695,
  "procName" : "Python",
  "procPath" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/Resources\/Python.app\/Contents\/MacOS\/Python",
  "bundleInfo" : {"CFBundleShortVersionString":"3.9.6","CFBundleVersion":"3.9.6","CFBundleIdentifier":"com.apple.python3"},
  "buildInfo" : {"ProjectName":"python3","SourceVersion":"141000000500005","BuildVersion":"558"},
  "storeInfo" : {"deviceIdentifierForVendor":"CA424AFA-E33D-5B56-BD82-DCB980E3568A","thirdParty":true},
  "parentProc" : "Exited process",
  "parentPid" : 30744,
  "coalitionName" : "com.googlecode.iterm2",
  "crashReporterKey" : "4E207357-19A3-A70F-DAD5-7940E32325FE",
  "developerMode" : 1,
  "responsiblePid" : 82031,
  "responsibleProc" : "iTerm2",
  "codeSigningID" : "com.apple.python3",
  "codeSigningTeamID" : "",
  "codeSigningFlags" : 570442241,
  "codeSigningValidationCategory" : 1,
  "codeSigningTrustLevel" : 4294967295,
  "codeSigningAuxiliaryInfo" : 0,
  "instructionByteStream" : {"beforePC":"CLBBuQgCADQInEE5KAIANAAAgNLAA1\/WPwAC8egCAFQI9ED5iAEAtA==","atPC":"CQFA+Qn0APkJwEG5KQUAEQnAAbngAwiqwANf1gjEQbkIBQARCMQBuQ=="},
  "bootSessionUUID" : "5850EF2B-C83B-4727-9011-8204D41D63E2",
  "wakeTime" : 19908,
  "sleepWakeUUID" : "89A526E4-FDDB-41F1-9A6E-D69187D9F26A",
  "sip" : "enabled",
  "vmRegionInfo" : "0xc00000009 is not in any region.  Bytes after previous region: 5200936970  Bytes before following region: 16106127351\n      REGION TYPE                    START - END         [ VSIZE] PRT\/MAX SHRMOD  REGION DETAIL\n      commpage (reserved)         7cbc00000-aca000000    [ 12.0G] ---\/--- SM=NUL  reserved VM address space (unallocated)\n--->  GAP OF 0x4f6000000 BYTES\n      GPU Carveout (reserved)     fc0000000-1000000000   [  1.0G] ---\/--- SM=NUL  reserved VM address space (unallocated)",
  "exception" : {"codes":"0x0000000000000001, 0x0000000c00000009","rawCodes":[1,51539607561],"type":"EXC_BAD_ACCESS","signal":"SIGSEGV","subtype":"KERN_INVALID_ADDRESS at 0x0000000c00000009"},
  "termination" : {"flags":0,"code":11,"namespace":"SIGNAL","indicator":"Segmentation fault: 11","byProc":"exc handler","byPid":30746},
  "vmregioninfo" : "0xc00000009 is not in any region.  Bytes after previous region: 5200936970  Bytes before following region: 16106127351\n      REGION TYPE                    START - END         [ VSIZE] PRT\/MAX SHRMOD  REGION DETAIL\n      commpage (reserved)         7cbc00000-aca000000    [ 12.0G] ---\/--- SM=NUL  reserved VM address space (unallocated)\n--->  GAP OF 0x4f6000000 BYTES\n      GPU Carveout (reserved)     fc0000000-1000000000   [  1.0G] ---\/--- SM=NUL  reserved VM address space (unallocated)",
  "extMods" : {"caller":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"system":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"targeted":{"thread_create":0,"thread_set_state":0,"task_for_pid":0},"warnings":0},
  "faultingThread" : 1,
  "threads" : [{"id":4237918,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":48},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":49},{"imageOffset":1442572,"symbol":"PyThread_acquire_lock_timed","symbolLocation":540,"imageIndex":1},{"imageOffset":1765712,"imageIndex":1},{"imageOffset":1764916,"imageIndex":1},{"imageOffset":304100,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1123692,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":10964,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":1112528,"symbol":"PyEval_EvalCode","symbolLocation":80,"imageIndex":1},{"imageOffset":1388824,"imageIndex":1},{"imageOffset":1389320,"imageIndex":1},{"imageOffset":1383120,"symbol":"PyRun_SimpleFileExFlags","symbolLocation":812,"imageIndex":1},{"imageOffset":1502476,"symbol":"Py_RunMain","symbolLocation":1448,"imageIndex":1},{"imageOffset":1503424,"imageIndex":1},{"imageOffset":1503584,"symbol":"Py_BytesMain","symbolLocation":40,"imageIndex":1},{"imageOffset":35108,"symbol":"start","symbolLocation":6400,"imageIndex":50}],"threadState":{"x":[{"value":260},{"value":0},{"value":0},{"value":0},{"value":0},{"value":160},{"value":0},{"value":0},{"value":6132979816},{"value":0},{"value":0},{"value":2},{"value":2},{"value":0},{"value":0},{"value":0},{"value":305},{"value":8776228624},{"value":0},{"value":33474916792},{"value":33474916744},{"value":8752924320,"symbolLocation":224,"symbol":"_main_thread"},{"value":0},{"value":0},{"value":0},{"value":1},{"value":256},{"value":4417391732},{"value":4343458496}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6932000924},"cpsr":{"value":1610612736},"fp":{"value":6132979936},"sp":{"value":6132979792},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6931739896},"far":{"value":0}}},{"recursionInfoArray":[{"hottestElided":25,"coldestElided":40,"depth":10,"keyFrame":{"imageOffset":1139676,"imageIndex":1}}],"id":4237944,"originalLength":62,"triggered":true,"threadState":{"x":[{"value":33442294272},{"value":104},{"value":353104982},{"value":6932027780},{"value":0},{"value":7},{"value":6149784132},{"value":11},{"value":51539607561},{"value":40},{"value":6},{"value":4294967294},{"value":3},{"value":1},{"value":1},{"value":33466225000},{"value":6932027968,"symbolLocation":0,"symbol":"_platform_strlen"},{"value":8776224984},{"value":0},{"value":0},{"value":33442294272},{"value":33479004160},{"value":0},{"value":0},{"value":6},{"value":6149787000},{"value":17},{"value":33444135040},{"value":33466224992}],"flavor":"ARM_THREAD_STATE64","lr":{"value":7064850884},"cpsr":{"value":2147483648},"fp":{"value":6149783648},"sp":{"value":6149783552},"esr":{"value":2449473542,"description":"(Data Abort) byte read Translation fault"},"pc":{"value":7065305808,"matchesCrashFrame":1},"far":{"value":51539607561}},"frames":[{"imageOffset":733904,"symbol":"sqlite3DbMallocRawNNTyped","symbolLocation":52,"imageIndex":52},{"imageOffset":278980,"symbol":"exprDup","symbolLocation":168,"imageIndex":52},{"imageOffset":944756,"symbol":"sqlite3ExprCodeRunJustOnce","symbolLocation":172,"imageIndex":52},{"imageOffset":968528,"symbol":"sqlite3ExprCodeFactorable","symbolLocation":148,"imageIndex":52},{"imageOffset":326896,"symbol":"sqlite3Insert","symbolLocation":5548,"imageIndex":52},{"imageOffset":52116,"symbol":"yy_reduce","symbolLocation":6860,"imageIndex":52},{"imageOffset":41092,"symbol":"sqlite3RunParser","symbolLocation":796,"imageIndex":52},{"imageOffset":38224,"symbol":"sqlite3Prepare","symbolLocation":472,"imageIndex":52},{"imageOffset":37356,"symbol":"sqlite3LockAndPrepare","symbolLocation":224,"imageIndex":52},{"imageOffset":33660,"imageIndex":47},{"imageOffset":15384,"imageIndex":47},{"imageOffset":267116,"symbol":"_PyObject_MakeTpCall","symbolLocation":356,"imageIndex":1},{"imageOffset":271388,"imageIndex":1},{"imageOffset":271692,"symbol":"_PyObject_CallFunction_SizeT","symbolLocation":52,"imageIndex":1},{"imageOffset":6744,"imageIndex":47},{"imageOffset":22604,"imageIndex":47},{"imageOffset":303708,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":278164,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1117608,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":4880,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1122684,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":9956,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":278300,"imageIndex":1},{"imageOffset":1768972,"imageIndex":1},{"imageOffset":1441480,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":49},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":49}]},{"id":4237945,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":48},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":49},{"imageOffset":1108780,"imageIndex":1},{"imageOffset":1110492,"symbol":"PyEval_RestoreThread","symbolLocation":24,"imageIndex":1},{"imageOffset":1489200,"symbol":"_Py_read","symbolLocation":92,"imageIndex":1},{"imageOffset":1403228,"imageIndex":1},{"imageOffset":1565944,"imageIndex":1},{"imageOffset":545152,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121456,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8728,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121456,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8728,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":278164,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1117608,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":4880,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1122684,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":9956,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":278300,"imageIndex":1},{"imageOffset":1768972,"imageIndex":1},{"imageOffset":1441480,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":49},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":49}],"threadState":{"x":[{"value":4},{"value":0},{"value":15360},{"value":0},{"value":0},{"value":160},{"value":0},{"value":5000000},{"value":6166617128},{"value":0},{"value":10752},{"value":46179488377346},{"value":46179488377346},{"value":10752},{"value":0},{"value":46179488377344},{"value":305},{"value":8776228624},{"value":0},{"value":4337424704,"symbolLocation":432,"symbol":"_PyRuntime"},{"value":4337424656,"symbolLocation":384,"symbol":"_PyRuntime"},{"value":6166622432},{"value":5000000},{"value":0},{"value":15360},{"value":15360},{"value":16640},{"value":4427919576},{"value":33442124800}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6932000924},"cpsr":{"value":1610612736},"fp":{"value":6166617248},"sp":{"value":6166617104},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6931739896},"far":{"value":0}}},{"id":4237946,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":48},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":49},{"imageOffset":1108780,"imageIndex":1},{"imageOffset":1110492,"symbol":"PyEval_RestoreThread","symbolLocation":24,"imageIndex":1},{"imageOffset":1489200,"symbol":"_Py_read","symbolLocation":92,"imageIndex":1},{"imageOffset":1403228,"imageIndex":1},{"imageOffset":1565944,"imageIndex":1},{"imageOffset":545152,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121456,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8728,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121456,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8728,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":278164,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1117608,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":4880,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1122684,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":9956,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":278300,"imageIndex":1},{"imageOffset":1768972,"imageIndex":1},{"imageOffset":1441480,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":49},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":49}],"threadState":{"x":[{"value":4},{"value":0},{"value":15872},{"value":0},{"value":0},{"value":160},{"value":0},{"value":4999000},{"value":6183443496},{"value":0},{"value":10752},{"value":46179488377346},{"value":46179488377346},{"value":10752},{"value":0},{"value":46179488377344},{"value":305},{"value":8776228624},{"value":0},{"value":4337424704,"symbolLocation":432,"symbol":"_PyRuntime"},{"value":4337424656,"symbolLocation":384,"symbol":"_PyRuntime"},{"value":6183448800},{"value":4999000},{"value":0},{"value":15872},{"value":15872},{"value":17152},{"value":4427919576},{"value":33442125120}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6932000924},"cpsr":{"value":1610612736},"fp":{"value":6183443616},"sp":{"value":6183443472},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6931739896},"far":{"value":0}}},{"recursionInfoArray":[{"hottestElided":14,"coldestElided":29,"depth":10,"keyFrame":{"imageOffset":1139676,"imageIndex":1}}],"id":4237947,"originalLength":51,"threadState":{"x":[{"value":4},{"value":0},{"value":15360},{"value":0},{"value":0},{"value":160},{"value":0},{"value":5000000},{"value":6200266952},{"value":0},{"value":10752},{"value":46179488377346},{"value":46179488377346},{"value":10752},{"value":0},{"value":46179488377344},{"value":305},{"value":8776228624},{"value":0},{"value":4337424704,"symbolLocation":432,"symbol":"_PyRuntime"},{"value":4337424656,"symbolLocation":384,"symbol":"_PyRuntime"},{"value":6200275168},{"value":5000000},{"value":0},{"value":15360},{"value":15360},{"value":16896},{"value":4470610712},{"value":33442125440}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6932000924},"cpsr":{"value":1610612736},"fp":{"value":6200267072},"sp":{"value":6200266928},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6931739896},"far":{"value":0}},"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":48},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":49},{"imageOffset":1108780,"imageIndex":1},{"imageOffset":1110492,"symbol":"PyEval_RestoreThread","symbolLocation":24,"imageIndex":1},{"imageOffset":23948,"imageIndex":47},{"imageOffset":303708,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":278164,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1117608,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":4880,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1122684,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":9956,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":278300,"imageIndex":1},{"imageOffset":1768972,"imageIndex":1},{"imageOffset":1441480,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":49},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":49}]},{"recursionInfoArray":[{"hottestElided":15,"coldestElided":30,"depth":10,"keyFrame":{"imageOffset":1139676,"imageIndex":1}}],"id":4237948,"originalLength":52,"threadState":{"x":[{"value":4},{"value":0},{"value":15360},{"value":0},{"value":0},{"value":160},{"value":0},{"value":5000000},{"value":6217093288},{"value":0},{"value":10752},{"value":46179488377346},{"value":46179488377346},{"value":10752},{"value":0},{"value":46179488377344},{"value":305},{"value":8776228624},{"value":0},{"value":4337424704,"symbolLocation":432,"symbol":"_PyRuntime"},{"value":4337424656,"symbolLocation":384,"symbol":"_PyRuntime"},{"value":6217101536},{"value":5000000},{"value":0},{"value":15360},{"value":15360},{"value":16384},{"value":4470610712},{"value":33442125760}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6932000924},"cpsr":{"value":1610612736},"fp":{"value":6217093408},"sp":{"value":6217093264},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6931739896},"far":{"value":0}},"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":48},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":49},{"imageOffset":1108780,"imageIndex":1},{"imageOffset":1110492,"symbol":"PyEval_RestoreThread","symbolLocation":24,"imageIndex":1},{"imageOffset":36096,"imageIndex":47},{"imageOffset":24056,"imageIndex":47},{"imageOffset":303708,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":278164,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1117608,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":4880,"imageIndex":1},{"imageOffset":1143092,"imageIndex":1},{"imageOffset":269272,"symbol":"_PyFunction_Vectorcall","symbolLocation":228,"imageIndex":1},{"imageOffset":1122684,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":9956,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":1139676,"imageIndex":1},{"imageOffset":1121416,"symbol":"_PyEval_EvalFrameDefault","symbolLocation":8688,"imageIndex":1},{"imageOffset":269676,"imageIndex":1},{"imageOffset":278300,"imageIndex":1},{"imageOffset":1768972,"imageIndex":1},{"imageOffset":1441480,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":49},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":49}]},{"id":4237950,"frames":[{"imageOffset":17656,"symbol":"__psynch_cvwait","symbolLocation":8,"imageIndex":48},{"imageOffset":28828,"symbol":"_pthread_cond_wait","symbolLocation":984,"imageIndex":49},{"imageOffset":1108780,"imageIndex":1},{"imageOffset":1110068,"symbol":"PyEval_AcquireThread","symbolLocation":24,"imageIndex":1},{"imageOffset":1768944,"imageIndex":1},{"imageOffset":1441480,"imageIndex":1},{"imageOffset":27592,"symbol":"_pthread_start","symbolLocation":136,"imageIndex":49},{"imageOffset":7040,"symbol":"thread_start","symbolLocation":8,"imageIndex":49}],"threadState":{"x":[{"value":260},{"value":0},{"value":15360},{"value":0},{"value":0},{"value":160},{"value":0},{"value":5000000},{"value":6250753656},{"value":0},{"value":10752},{"value":46179488377346},{"value":46179488377346},{"value":10752},{"value":0},{"value":46179488377344},{"value":305},{"value":8776228624},{"value":0},{"value":4337424704,"symbolLocation":432,"symbol":"_PyRuntime"},{"value":4337424656,"symbolLocation":384,"symbol":"_PyRuntime"},{"value":6250754272},{"value":5000000},{"value":0},{"value":15360},{"value":15360},{"value":16128},{"value":0},{"value":0}],"flavor":"ARM_THREAD_STATE64","lr":{"value":6932000924},"cpsr":{"value":1610612736},"fp":{"value":6250753776},"sp":{"value":6250753632},"esr":{"value":1442840704,"description":"(Syscall)"},"pc":{"value":6931739896},"far":{"value":0}}}],
  "usedImages" : [
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4333895680,
    "CFBundleShortVersionString" : "3.9.6",
    "CFBundleIdentifier" : "com.apple.python3",
    "size" : 16384,
    "uuid" : "808d48a0-1c2f-33bd-853f-9ae290dc4d95",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/Resources\/Python.app\/Contents\/MacOS\/Python",
    "name" : "Python",
    "CFBundleVersion" : "3.9.6"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4334534656,
    "CFBundleShortVersionString" : "3.9.6",
    "CFBundleIdentifier" : "com.apple.python3",
    "size" : 2506752,
    "uuid" : "0f563628-0fa8-30c9-9520-6e975bc8d93f",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/Python3",
    "name" : "Python3",
    "CFBundleVersion" : "3.9.6"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4340858880,
    "size" : 32768,
    "uuid" : "7b30aed2-0503-34fe-8a70-cc11cc935f05",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_heapq.cpython-39-darwin.so",
    "name" : "_heapq.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4340957184,
    "size" : 32768,
    "uuid" : "78031110-ab0e-3594-9955-fe8bd7cc3796",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/zlib.cpython-39-darwin.so",
    "name" : "zlib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4417814528,
    "size" : 16384,
    "uuid" : "19bbc1ec-dc6d-3210-98f2-ed33c96916c0",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_bz2.cpython-39-darwin.so",
    "name" : "_bz2.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4417896448,
    "size" : 32768,
    "uuid" : "ac8a4c97-44d3-3daa-bde1-7dd588b5dea7",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_lzma.cpython-39-darwin.so",
    "name" : "_lzma.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4417994752,
    "size" : 16384,
    "uuid" : "1c8a23f9-d152-35a9-8d7b-e1e5582632ac",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/grp.cpython-39-darwin.so",
    "name" : "grp.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4337729536,
    "size" : 49152,
    "uuid" : "8e9c0437-ae12-3d89-8222-ac85ff6f2050",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/math.cpython-39-darwin.so",
    "name" : "math.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4337844224,
    "size" : 16384,
    "uuid" : "9628500f-d3ad-3c77-a8cf-4670c10c510c",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_bisect.cpython-39-darwin.so",
    "name" : "_bisect.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4418224128,
    "size" : 16384,
    "uuid" : "4bbfa841-1a4a-37b6-a25d-c980c28e7680",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_random.cpython-39-darwin.so",
    "name" : "_random.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4418076672,
    "size" : 32768,
    "uuid" : "beb14a7b-b3de-3aa1-b17e-39f34b441f4e",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_sha512.cpython-39-darwin.so",
    "name" : "_sha512.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4418715648,
    "size" : 16384,
    "uuid" : "a9f5f2a6-4ac2-3195-9e4b-ebe07c0f769d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_queue.cpython-39-darwin.so",
    "name" : "_queue.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4418568192,
    "size" : 32768,
    "uuid" : "49ae3103-4e55-3f3b-89a3-6ed59d03a908",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_struct.cpython-39-darwin.so",
    "name" : "_struct.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4419764224,
    "size" : 32768,
    "uuid" : "b3b0aed3-f8cb-37a4-ae0b-23e469841bea",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/binascii.cpython-39-darwin.so",
    "name" : "binascii.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4419862528,
    "size" : 32768,
    "uuid" : "0e923671-4fb5-3cf1-b25b-62823af87f90",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_hashlib.cpython-39-darwin.so",
    "name" : "_hashlib.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4419584000,
    "size" : 49152,
    "uuid" : "e0f957a1-bee3-3e36-8c74-31e2adefe2bb",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_blake2.cpython-39-darwin.so",
    "name" : "_blake2.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420222976,
    "size" : 65536,
    "uuid" : "0eb51e69-389e-3de8-bad1-1d5ab698a265",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_sha3.cpython-39-darwin.so",
    "name" : "_sha3.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420763648,
    "size" : 16384,
    "uuid" : "cf8e29c4-8f70-34bf-9792-644a7d06316e",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_opcode.cpython-39-darwin.so",
    "name" : "_opcode.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4421107712,
    "size" : 16384,
    "uuid" : "53de3c57-b242-399b-a604-24715f8b6c5d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_posixsubprocess.cpython-39-darwin.so",
    "name" : "_posixsubprocess.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4420616192,
    "size" : 32768,
    "uuid" : "ec97e380-290c-31c0-bc27-516cf02fc85a",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/select.cpython-39-darwin.so",
    "name" : "select.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4421992448,
    "size" : 81920,
    "uuid" : "6db62488-f4b5-37a5-935a-83567e6d83ab",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_datetime.cpython-39-darwin.so",
    "name" : "_datetime.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4422320128,
    "size" : 32768,
    "uuid" : "de17005f-a5be-3a2e-9691-0c1b1873c1fd",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_csv.cpython-39-darwin.so",
    "name" : "_csv.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4422139904,
    "size" : 65536,
    "uuid" : "35ca3347-d6a5-35e3-9477-6a3ccb283d23",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_socket.cpython-39-darwin.so",
    "name" : "_socket.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4423155712,
    "size" : 49152,
    "uuid" : "ff860554-95bd-339d-96aa-e2846057a0d2",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/array.cpython-39-darwin.so",
    "name" : "array.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4423794688,
    "size" : 16384,
    "uuid" : "49034e2f-bb91-3f9e-96fe-9f7606a1d9c2",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_contextvars.cpython-39-darwin.so",
    "name" : "_contextvars.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4424531968,
    "size" : 229376,
    "uuid" : "efc9bb47-4ab7-37e1-ac93-f1c928b2fb91",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/google\/_upb\/_message.abi3.so",
    "name" : "_message.abi3.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4422942720,
    "size" : 98304,
    "uuid" : "2bde962c-7928-359c-aa25-ac85a8b926c9",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_pickle.cpython-39-darwin.so",
    "name" : "_pickle.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4426563584,
    "size" : 98304,
    "uuid" : "b6b6cf56-cf37-3842-b979-1a70fd5b10dd",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_ssl.cpython-39-darwin.so",
    "name" : "_ssl.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4424400896,
    "size" : 49152,
    "uuid" : "5f18ee52-c95b-352e-b19d-5b09e63be3a1",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_asyncio.cpython-39-darwin.so",
    "name" : "_asyncio.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4426448896,
    "size" : 32768,
    "uuid" : "d6ec7673-c6b2-3cd0-aa68-0af178167af5",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_json.cpython-39-darwin.so",
    "name" : "_json.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4428218368,
    "size" : 16384,
    "uuid" : "6c7beb54-585b-3582-80b3-8425443e993d",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_uuid.cpython-39-darwin.so",
    "name" : "_uuid.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4431855616,
    "size" : 278528,
    "uuid" : "74560b51-827c-3636-bbb9-d0c73b90fec2",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_decimal.cpython-39-darwin.so",
    "name" : "_decimal.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4453531648,
    "size" : 3751936,
    "uuid" : "8a370734-3093-332f-8582-b45fd9efee3f",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/pydantic_core\/_pydantic_core.cpython-39-darwin.so",
    "name" : "_pydantic_core.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4428070912,
    "size" : 32768,
    "uuid" : "56a26b83-6e8e-3d80-b3fa-9e48be682dac",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_zoneinfo.cpython-39-darwin.so",
    "name" : "_zoneinfo.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4419698688,
    "size" : 16384,
    "uuid" : "c6c0ba3a-867b-3d25-804c-427cd0223ba6",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/charset_normalizer\/md.cpython-39-darwin.so",
    "name" : "md.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4457578496,
    "size" : 163840,
    "uuid" : "a0a8f051-3e84-34d3-9804-42911ae70d3c",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/charset_normalizer\/md__mypyc.cpython-39-darwin.so",
    "name" : "md__mypyc.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4461756416,
    "size" : 1114112,
    "uuid" : "d13600ad-15f6-3df0-9366-b00b8e51fbe7",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/unicodedata.cpython-39-darwin.so",
    "name" : "unicodedata.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4431708160,
    "size" : 32768,
    "uuid" : "2ee10d7f-142f-3679-9461-3f8ac5cbb6d6",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_multibytecodec.cpython-39-darwin.so",
    "name" : "_multibytecodec.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4453433344,
    "size" : 16384,
    "uuid" : "acb15f58-f305-35c9-aeba-ca4a2fdbf959",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_scproxy.cpython-39-darwin.so",
    "name" : "_scproxy.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4460560384,
    "size" : 262144,
    "uuid" : "28d7d63e-0ac7-3dd0-b8fa-ca45281fac44",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/yaml\/_yaml.cpython-39-darwin.so",
    "name" : "_yaml.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4460462080,
    "size" : 32768,
    "uuid" : "69d1a887-f91d-395a-9f3c-1038698321da",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/mmap.cpython-39-darwin.so",
    "name" : "mmap.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4463345664,
    "size" : 16384,
    "uuid" : "e8d33c43-c414-32f1-bb90-2afea3c8e6ef",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/resource.cpython-39-darwin.so",
    "name" : "resource.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4463951872,
    "size" : 163840,
    "uuid" : "e967e075-c022-38e0-b8ae-9f708eea9307",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/sqlalchemy\/cyextension\/collections.cpython-39-darwin.so",
    "name" : "collections.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4463689728,
    "size" : 65536,
    "uuid" : "020c57e8-f97a-35ce-ae1f-58c4d26dac92",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/sqlalchemy\/cyextension\/immutabledict.cpython-39-darwin.so",
    "name" : "immutabledict.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4463820800,
    "size" : 49152,
    "uuid" : "f641a2b0-5739-337f-a0d3-2ad757c7879e",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/sqlalchemy\/cyextension\/processors.cpython-39-darwin.so",
    "name" : "processors.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4464214016,
    "size" : 49152,
    "uuid" : "99470441-19dc-3f03-9b47-67ad20481b03",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/sqlalchemy\/cyextension\/resultproxy.cpython-39-darwin.so",
    "name" : "resultproxy.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4464328704,
    "size" : 65536,
    "uuid" : "ab97462c-1da2-3010-a82d-26105078c95b",
    "path" : "\/Users\/USER\/Library\/Python\/3.9\/lib\/python\/site-packages\/sqlalchemy\/cyextension\/util.cpython-39-darwin.so",
    "name" : "util.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64",
    "base" : 4463198208,
    "size" : 49152,
    "uuid" : "2a4818bb-3251-3d4d-a31a-dad940ff8659",
    "path" : "\/Library\/Developer\/CommandLineTools\/Library\/Frameworks\/Python3.framework\/Versions\/3.9\/lib\/python3.9\/lib-dynload\/_sqlite3.cpython-39-darwin.so",
    "name" : "_sqlite3.cpython-39-darwin.so"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6931722240,
    "size" : 246880,
    "uuid" : "2eb73bf1-8c71-3e1f-a160-6da83dc82606",
    "path" : "\/usr\/lib\/system\/libsystem_kernel.dylib",
    "name" : "libsystem_kernel.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6931972096,
    "size" : 51816,
    "uuid" : "6f3be508-fbaf-31d0-868b-fc5b5c9bc54c",
    "path" : "\/usr\/lib\/system\/libsystem_pthread.dylib",
    "name" : "libsystem_pthread.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6928044032,
    "size" : 648924,
    "uuid" : "0c2c14a0-a9e6-3a10-b39e-68d30d14e66c",
    "path" : "\/usr\/lib\/dyld",
    "name" : "dyld"
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
    "base" : 7064571904,
    "size" : 1995684,
    "uuid" : "a21dba03-168f-3a84-a03e-23c7d401b562",
    "path" : "\/usr\/lib\/libsqlite3.dylib",
    "name" : "libsqlite3.dylib"
  },
  {
    "source" : "P",
    "arch" : "arm64e",
    "base" : 6932025344,
    "size" : 32864,
    "uuid" : "aac0cf6e-b9cd-3367-a544-a9ac62716721",
    "path" : "\/usr\/lib\/system\/libsystem_platform.dylib",
    "name" : "libsystem_platform.dylib"
  }
],
  "sharedCache" : {
  "base" : 6926974976,
  "size" : 5553274880,
  "uuid" : "45dbada1-d88a-360f-bdc3-e64049d11e71"
},
  "vmSummary" : "ReadOnly portion of Libraries: Total=888.6M resident=0K(0%) swapped_out_or_unallocated=888.6M(100%)\nWritable regions: Total=296.8M written=320K(0%) resident=320K(0%) swapped_out=0K(0%) unallocated=296.5M(100%)\n\n                                VIRTUAL   REGION \nREGION TYPE                        SIZE    COUNT (non-coalesced) \n===========                     =======  ======= \nActivity Tracing                   256K        1 \nColorSync                           32K        2 \nKernel Alloc Once                   32K        1 \nMALLOC                           124.0M       22 \nMALLOC guard page                 3744K        4 \nSQLite page cache                  128K        1 \nSTACK GUARD                        112K        7 \nStack                            128.2M        8 \nStack Guard                         16K        1 \nVM_ALLOCATE                       44.3M      177 \n__AUTH                            1311K      148 \n__AUTH_CONST                      17.6M      347 \n__CTF                               824        1 \n__DATA                            5121K      352 \n__DATA_CONST                      16.1M      395 \n__DATA_DIRTY                      1314K      290 \n__FONT_DATA                        2352        1 \n__LINKEDIT                       594.8M       49 \n__OBJC_RO                         78.1M        1 \n__OBJC_RW                         2560K        1 \n__TEXT                           293.7M      404 \n__TPRO_CONST                       128K        2 \ndyld private memory                160K        2 \nmapped file                         80K        1 \npage table in kernel               320K        1 \nshared memory                       96K        4 \n===========                     =======  ======= \nTOTAL                              1.3G     2223 \n",
  "legacyInfo" : {
  "threadTriggered" : {

  }
},
  "logWritingSignature" : "c49d3924ebf37a4f10ba7244ece079127e94a2bb",
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
      "rolloutId" : "648cada15dbc71671bb3aa1b",
      "factorPackIds" : [
        "65a81173096f6a1f1ba46525"
      ],
      "deploymentId" : 250000113
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
IO80211_driverkit-1525.88 "IO80211_driverkit-1525.88" Aug 27 2025 20:25:46
AirPort: 
Bluetooth: Version (null), 0 services, 0 devices, 0 incoming serial ports
Network Service: Ethernet Adapter (en3), Ethernet, en3
Network Service: Ethernet Adapter (en4), Ethernet, en4
Network Service: Wi-Fi, AirPort, en0
Thunderbolt Bus: MacBook Air, Apple Inc.
Thunderbolt Bus: MacBook Air, Apple Inc.
