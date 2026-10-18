#/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import argparse

# This script takes the trace: wifi-dcf-state-trace.10.dat
#
# with lines such as:
#
# 0.014941 0 state: IDLE start: 0.000000 duration 0.014941
# 0.014941 0 state: TX start: 0.014941 duration 0.000104
# etc.
#
# and it sums the total TX time for each node, disregarding events that 
# occur before time 1 second (our warmup time)
#
# Data is output into a file 'wifi-dcf-tx-times.dat'

tx_times = [0]*11
total_tx_time = 0
idle_time = 0
f = open('wifi-dcf-state-trace.10.dat', 'r')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[3] == 'TX':
        node = int(columns[1])
        tx_times[node] += float(columns[7])
        total_tx_time += float(columns[7])
f.close()
output_f = open('wifi-dcf-tx-times.dat', 'w')
for i in range(11):
    output_f.write("%d %f\n" % (i, tx_times[i])) 
output_f.close()
