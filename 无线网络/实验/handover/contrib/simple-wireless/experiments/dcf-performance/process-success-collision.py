#/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

# This script takes the trace: wifi-dcf-state-trace.10.dat
#
# with lines such as:
#
# 0.014941 0 state: IDLE start: 0.000000 duration 0.014941
# 0.014941 0 state: TX start: 0.014941 duration 0.000104
# etc.
#
# and it looks for transmissions that have no other transmission at the same
# time, and counts those as a 'success'.  It looks for transmissions that
# coincide with another transmission, and counts all of those as 'collision'.
# 
# All output data is exported to a file 'success-collision.10.dat' which can
# be used for table input to answer the question
#
# The output column data format for 'success-collision.10.dat' is:
# 'nodeId' '#successes' '#failures' 'success probability' 
#
# This program also takes the last step to repeat the calculation for each
# of the other network sizes (20, 30, 40) and creates a plot entitled
# 'wifi-dcf-success-probability-vs-number-of-nodes.pdf'.

successes = [0]*11
collisions = [0]*11
num_successes = 0
num_collisions = 0
last_time = 0
transmissions = []
f = open('wifi-dcf-state-trace.10.dat', 'r')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[3] == 'TX':
        timestamp = float(columns[0])
        node = int(columns[1])
        if (timestamp > last_time):
            # Count the number of previous transmissions at the last observed
            # timestamp.  If only one, then that was successful. If multiple,
            # then all were collisions.
            if (len(transmissions) == 1):
                successes[transmissions[0]] += 1
                num_successes += 1
            elif (len(transmissions) > 1):
                for i in transmissions:
                    collisions[i] += 1
                    num_collisions += 1
            elif (last_time != 0):
                sys.exit (1)
            transmissions = []
            last_time = timestamp
        transmissions.append (node)
f.close()
output_f = open('wifi-dcf-success-collision.10.dat', 'w')
for i in range(11):
    output_f.write("%d %d %d %f\n" % (i, successes[i], collisions[i], (float(successes[i])/(successes[i] + collisions[i])))) 
output_f.close()

output_f2 = open('wifi-dcf-success-probability-vs-number-of-nodes.dat', 'w')
output_f2.write("%d %d %d %f\n" % (10, num_successes, num_collisions, float(num_successes)/(num_successes + num_collisions))) 
output_f2.close()

# Repeat overall success/collision count for 20 nodes
num_successes = 0
num_collisions = 0
last_time = 0
transmissions = []
f = open('wifi-dcf-state-trace.20.dat', 'r')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[3] == 'TX':
        timestamp = float(columns[0])
        node = int(columns[1])
        if (timestamp > last_time):
            # Count the number of previous transmissions at the last observed
            # timestamp.  If only one, then that was successful. If multiple,
            # then all were collisions.
            if (len(transmissions) == 1):
                num_successes += 1
            elif (len(transmissions) > 1):
                for i in transmissions:
                    num_collisions += 1
            elif (last_time != 0):
                sys.exit (1)
            transmissions = []
            last_time = timestamp
        transmissions.append (node)
f.close()

output_f2 = open('wifi-dcf-success-probability-vs-number-of-nodes.dat', 'a')
output_f2.write("%d %d %d %f\n" % (20, num_successes, num_collisions, float(num_successes)/(num_successes + num_collisions))) 
output_f2.close()

# Repeat overall success/collision count for 30 nodes
num_successes = 0
num_collisions = 0
last_time = 0
transmissions = []
f = open('wifi-dcf-state-trace.30.dat', 'r')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[3] == 'TX':
        timestamp = float(columns[0])
        node = int(columns[1])
        if (timestamp > last_time):
            # Count the number of previous transmissions at the last observed
            # timestamp.  If only one, then that was successful. If multiple,
            # then all were collisions.
            if (len(transmissions) == 1):
                num_successes += 1
            elif (len(transmissions) > 1):
                for i in transmissions:
                    num_collisions += 1
            elif (last_time != 0):
                sys.exit (1)
            transmissions = []
            last_time = timestamp
        transmissions.append (node)
f.close()

output_f2 = open('wifi-dcf-success-probability-vs-number-of-nodes.dat', 'a')
output_f2.write("%d %d %d %f\n" % (30, num_successes, num_collisions, float(num_successes)/(num_successes + num_collisions))) 
output_f2.close()

# Repeat overall success/collision count for 40 nodes
num_successes = 0
num_collisions = 0
last_time = 0
transmissions = []
f = open('wifi-dcf-state-trace.40.dat', 'r')
for line in f:
    columns = line.split()
    if float(columns[0]) < 1:
        continue
    elif columns[3] == 'TX':
        timestamp = float(columns[0])
        node = int(columns[1])
        if (timestamp > last_time):
            # Count the number of previous transmissions at the last observed
            # timestamp.  If only one, then that was successful. If multiple,
            # then all were collisions.
            if (len(transmissions) == 1):
                num_successes += 1
            elif (len(transmissions) > 1):
                for i in transmissions:
                    num_collisions += 1
            elif (last_time != 0):
                sys.exit (1)
            transmissions = []
            last_time = timestamp
        transmissions.append (node)
f.close()

output_f2 = open('wifi-dcf-success-probability-vs-number-of-nodes.dat', 'a')
output_f2.write("%d %d %d %f\n" % (40, num_successes, num_collisions, float(num_successes)/(num_successes + num_collisions))) 
output_f2.close()

# create 'wifi-dcf-success-probability-vs-number-of-nodes.pdf'.
x = []
y = []
f = open('wifi-dcf-success-probability-vs-number-of-nodes.dat', 'r')
for line in f:
    columns = line.split()
    x.append(int(columns[0]))    
    y.append(float(columns[3]))    
f.close()

plt.figure()
plt.plot(x, y, marker='o')
plt.xlabel('Number of nodes')
plt.ylabel('Success probability')
plt.ylim([0,1])
plt.title('Success probability vs. number of nodes')
plt.savefig('wifi-dcf-success-probability-vs-number-of-nodes.pdf', format='pdf')

