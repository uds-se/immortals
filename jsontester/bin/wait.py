#!/usr/bin/env python3
import sys, os, subprocess, time, re
num = 2
while num > 0:
    #snum = subprocess.check_output("pgrep -u rahul.gopinath python3 -c", shell=True)
    result = subprocess.check_output("pgrep -u rahul.gopinath python3 -la", shell=True)
    num = 0
    for i,s in enumerate(result.decode('utf-8').split("\n")):
        if sys.argv[1] in s and 'wait.py' not in s:
            num += 1
            print(i, s)
    time.sleep(10)
    print()
