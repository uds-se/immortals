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
            num += 1
            print(i, s)
            if i not in seen:
                seen[i] = 0
            else:
                seen[i] += 1
            if seen[i] > 10:
                os.kill(i, signal.SIGALRM)
    time.sleep(10)
    print()
