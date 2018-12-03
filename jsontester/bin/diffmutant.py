#!/usr/bin/env python3
import sys, os.path, subprocess
mutant = sys.argv[1]
mutant_dir = os.path.dirname(mutant)
orig_dir = os.path.dirname(mutant_dir)
original = "%s/%s" % (orig_dir, 'original.py')
status, output = subprocess.getstatusoutput("diff -u %s %s" % (original, mutant))
print(output)
