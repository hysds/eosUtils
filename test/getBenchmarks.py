import os, sys, re, pprint

f = open(sys.argv[1])
lines = f.readlines()
f.close()

d = {}
totals = {}
for l in lines:
    tokens = l.split()
    if len(tokens) == 0: continue
    d[tokens[0]] = d.setdefault(tokens[0], 0) + float(tokens[2])
    totals[tokens[0]] = totals.setdefault(tokens[0], 0) + 1

for k in sorted(d):
    print k, d[k]/totals[k]
