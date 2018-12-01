#!/usr/bin/env python3
import sys, os, subprocess, time
num = 2
while num > 1:
    snum = subprocess.check_output("pgrep -u rahul.gopinath python3 -c", shell=True)
    result = subprocess.check_output("pgrep -u rahul.gopinath python3 -la", shell=True)
    num = int(snum)
    for i,s in enumerate(result.decode('utf-8').split("\n")):
        print(i, s)
    time.sleep(10)
