#/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import argparse

# This script takes the set of four state traces:
# 1. wifi-dcf-state-trace.10.dat
# 2. wifi-dcf-state-trace.20.dat
# 3. wifi-dcf-state-trace.30.dat
# 4. wifi-dcf-state-trace.40.dat
#
# with lines such as:
#
# 0.014941 0 state: IDLE start: 0.000000 duration 0.014941
# 0.014941 0 state: TX start: 0.014941 duration 0.000104
# etc.
#
# and it does the following:
# 1) disregard events that occur before time 1 second (our warmup time)
# 2) sum all of the idle times as observed on node 0 (after simulation time 1s)
# 3) plot the combination of 'network size, idle time' for n=10,20,30.40

parser = argparse.ArgumentParser()
# Optional arguments
parser.add_argument("--plotName", help="general output pdf filename", default='wifi-dcf-idle-time-vs-num-nodes.pdf')
parser.add_argument("--title", help="title", default='Idle time vs. number of stations')
parser.add_argument("--xlabel", help="xlabel", default='number of stations')
parser.add_argument("--ylabel", help="ylabel", default='Idle time (s)')
args = parser.parse_args()

x = []
y = []
idle_time = 0
f = open('wifi-dcf-state-trace.10.dat')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[1] == '0' and columns[3] == 'IDLE':
        if idle_time == 0:
            # The first idle time may span the start time for data logging
            idle_time = float(columns[0]) - 1
        else:
            idle_time += float(columns[7])
x.append(10)
y.append(idle_time)

idle_time = 0
f = open('wifi-dcf-state-trace.20.dat')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[1] == '0' and columns[3] == 'IDLE':
        if idle_time == 0:
            # The first idle time may span the start time for data logging
            idle_time = float(columns[0]) - 1
        else:
            idle_time += float(columns[7])
x.append(20)
y.append(idle_time)
f.close()

idle_time = 0
f = open('wifi-dcf-state-trace.30.dat')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[1] == '0' and columns[3] == 'IDLE':
        if idle_time == 0:
            # The first idle time may span the start time for data logging
            idle_time = float(columns[0]) - 1
        else:
            idle_time += float(columns[7])
x.append(30)
y.append(idle_time)
f.close()

idle_time = 0
f = open('wifi-dcf-state-trace.40.dat')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[1] == '0' and columns[3] == 'IDLE':
        if idle_time == 0:
            # The first idle time may span the start time for data logging
            idle_time = float(columns[0]) - 1
        else:
            idle_time += float(columns[7])
x.append(40)
y.append(idle_time)
f.close()

plt.figure()
plt.plot(x, y, marker='o')
plt.xlabel(args.xlabel)
plt.ylabel(args.ylabel)
plt.ylim([0,10])
plt.title(args.title)
plt.savefig(args.plotName, format='pdf')
