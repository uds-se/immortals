#!/usr/bin/env python3
import sys, os, subprocess, time, re, signal
num = 2
seen = {}
while num > 0:
    #snum = subprocess.check_output("pgrep -u rahul.gopinath python3 -c", shell=True)
    result = b''
    try:
        result = subprocess.check_output("pgrep -u rahul.gopinath python3 -la", shell=True)
    except:
        pass
    num = 0
    for i,s in enumerate(result.decode('utf-8').split("\n")):
        if sys.argv[1] in s and 'wait.py' not in s:
            pid, python3, testname = s.split(' ') # "13716 python3 tests/microjson_gfuzz.py"
            num += 1
            print(i, pid, testname)
            if pid not in seen:
                seen[pid] = 0
            else:
                seen[pid] += 1
            if seen[pid] > 10:
                print(">", pid)
                os.kill(int(pid), signal.SIGALRM)
            if seen[pid] > 20:
                os.kill(int(pid), signal.SIGKILL)
                print("X", pid)
    time.sleep(10)
    print()
