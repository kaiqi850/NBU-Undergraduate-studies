#/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import argparse

parser = argparse.ArgumentParser()
# Optional arguments
parser.add_argument("--fileName", help="general input filename")
parser.add_argument("--plotName", help="general output pdf filename")
parser.add_argument("--title", help="title")
parser.add_argument("--xcol", help="x column of data")
parser.add_argument("--ycol", help="y column of data")
parser.add_argument("--yerror", help="y error column of data")
parser.add_argument("--xlabel", help="xlabel")
parser.add_argument("--ylabel", help="ylabel")
args = parser.parse_args()

f = open(args.fileName)
x = []
y = []
yerror = []
for line in f:
    columns = line.split()
    x.append (float(columns[int(args.xcol)]))
    y.append (float(columns[int(args.ycol)]))
    yerror.append (float(columns[int(args.yerror)]))
f.close()
plt.figure()
plt.errorbar(x, y, yerr=yerror)
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.title(args.title)
plt.savefig(args.plotName, format='pdf')
