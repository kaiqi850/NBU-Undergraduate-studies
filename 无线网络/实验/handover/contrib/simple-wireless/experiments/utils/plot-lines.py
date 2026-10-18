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
parser.add_argument("--ymax", help="y maximum value")
parser.add_argument("--xlabel", help="xlabel")
parser.add_argument("--ylabel", help="ylabel")
args = parser.parse_args()

f = open(args.fileName)
x = []
y = []
for line in f:
    columns = line.split()
    x.append (float(columns[int(args.xcol)]))
    y.append (float(columns[int(args.ycol)]))
f.close()
plt.figure()
plt.plot(x, y, marker='o')
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.ylim([0,float(args.ymax)])
plt.title(args.title)
plt.savefig(args.plotName, format='pdf')
