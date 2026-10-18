import sys
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
# Positional arguments
parser.add_argument("--fileName", help="file name", default="lte-tcp-x2-handover.ue-measurements.dat")
parser.add_argument("--plotName", help="plot name", default="lte-tcp-x2-handover.rsrp.pdf")
# Optional timestep argument
parser.add_argument("--title", help="title string", default="LTE handover RSRP")
args = parser.parse_args()

times1=[]
times2=[]
values1=[]
values2=[]
fd = open(args.fileName, 'r')
for line in fd:
    l = line.split()
    if line.startswith("#"):
        continue
    if l[1] == "1":
        times1.append(float(l[0]))
        values1.append(float(l[3]))
    elif l[1] == "2":
        times2.append(float(l[0]))
        values2.append(float(l[3]))
fd.close()

if len(times1) == 0:
    print("No data points found, exiting...")
    sys.exit(1)

plt.scatter(times1, values1, marker='.', label='cell 1', color='red')
if len(times2) != 0:
    plt.scatter(times2, values2, marker='.', label='cell 2', color='blue')
plt.xlabel('Time (s)')
plt.ylabel('RSRP (dBm)')
plt.title(args.title)
#plt.show()
plotname = args.plotName
plt.savefig(plotname, format='pdf')
plt.close()

sys.exit (0)
