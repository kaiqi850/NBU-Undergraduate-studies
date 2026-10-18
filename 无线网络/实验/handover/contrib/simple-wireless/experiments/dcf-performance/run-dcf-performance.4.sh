#!/bin/bash
#
# Copyright (c) 2015-19 University of Washington
# Copyright (c) 2015 Centre Tecnologic de Telecomunicacions de Catalunya (CTTC)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation;
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# This script runs the wifi-dcf experiment, for the 'Experiment 4 Fairness'
# case.  It is very similar to the first question regarding throughput vs.
# number of nodes, but the data being plotted is different.
# 
# The number of stations is suffixed to the file name; e.g. the 
# 'wifi-dcf-state-trace.10.dat' is the trace file corresponding to the 
# n=10 case.  
#
# Results are stored in a timestamped 'results' directory.  There are a few
# key files that you will want for the solution:
# 1) wifi-dcf-tx-times.dat (transmission times per node)
# 2) wifi-dcf-idle-time-vs-num-nodes.pdf (plot)
# 3) wifi-dcf-success-collision.10.dat (count of successes and collisions for 
#    the 10-node scenario)
# 4) wifi-dcf-success-probability-vs-number-of-nodes.pdf (plot)
# 

set -e
set -o errexit

control_c()
{
  echo "exiting"
  exit $?
}

# Utility function to help with arithmetic below
calc()
{
  awk "BEGIN { print "$*" }" 
}

trap control_c SIGINT

dirname=dcf-performance-expt4

if test ! -f ../../../../waf ; then
    echo "please run this program from within the directory `dirname $0`, like this:"
    echo "cd `dirname $0`"
    echo "./`basename $0`"
    exit 1
fi

resultsDir=`pwd`/results/$dirname-`date +%Y%m%d-%H%M%S`
experimentDir=`pwd`

# need this as otherwise waf won't find the executables
cd ../../../../

# Avoid accidentally overwriting existing trace files; confirm deletion first
if [ -e wifi-dcf-ap-rx-trace.dat ]; then
    echo "Overwrite existing wifi-dcf trace files from top-level directory?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) echo "Overwriting..."; break;;
            No ) echo "Exiting..."; exit;;
        esac
    done
fi

# Avoid accidentally overwriting existing data files; confirm deletion first
if [ -e wifi-dcf-expt4.dat ]; then
    echo "Remove existing wifi-dcf-expt4.dat output file from top-level directory?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) echo "Removing..."; rm -rf wifi-dcf-expt4.dat; break;;
            No ) echo "Exiting..."; exit;;
        esac
    done
fi

# Random number generator run number
# For this experiment, you will not need to change this
RngRun=1

mkdir -p ${resultsDir}

# Echo remaining commands to standard output, to track progress
for numStas in 10 20 30 40
do
  arrivalRate=$(calc 4000/$numStas)
  set -x
  ./waf --run "wifi-dcf --numStas=${numStas} --packetArrivalRate=${arrivalRate}"
  { set +x; } 2>/dev/null
  packets=$(wc -l wifi-dcf-ap-rx-trace.dat | awk '{ print $1 }' )
  if [ -f wifi-dcf-0-0.pcap ]; then
    mv wifi-dcf-0-0.pcap ${resultsDir}/wifi-dcf-0-0.${numStas}.pcap
  fi
  if [ -f wifi-dcf-animation.xml ]; then
    mv wifi-dcf-animation.xml ${resultsDir}/wifi-dcf-animation.${numStas}.xml
  fi
  if [ -f wifi-dcf-ap-rx-trace.dat ]; then
    mv wifi-dcf-ap-rx-trace.dat ${resultsDir}/wifi-dcf-ap-rx-trace.${numStas}.dat
  fi
  if [ -f wifi-dcf-rx-error-trace.dat ]; then
    mv wifi-dcf-rx-error-trace.dat ${resultsDir}/wifi-dcf-rx-error-trace.${numStas}.dat
  fi
  if [ -f wifi-dcf-rx-ok-trace.dat ]; then
    mv wifi-dcf-rx-ok-trace.dat ${resultsDir}/wifi-dcf-rx-ok-trace.${numStas}.dat
  fi
  if [ -f wifi-dcf-state-trace.dat ]; then
    mv wifi-dcf-state-trace.dat ${resultsDir}/wifi-dcf-state-trace.${numStas}.dat
  fi
  if [ -f wifi-dcf-sta-tx-trace.dat ]; then
    mv wifi-dcf-sta-tx-trace.dat ${resultsDir}/wifi-dcf-sta-tx-trace.${numStas}.dat
  fi
  if [ -f wifi-dcf.tr ]; then
    mv wifi-dcf.tr ${resultsDir}/wifi-dcf.${numStas}.tr
  fi
  # Compute the throughput and append it to the data file that will be plotted
  throughput=$(bc -l <<< "$packets * 1900 * 8 / 10")
  throughputMbps=$(bc -l <<< "$throughput / 1000000")
  echo "$numStas $throughputMbps" >> wifi-dcf-expt4.dat
done

# Move plot data file to the results directory
mv wifi-dcf-expt4.dat ${resultsDir}

cd $experimentDir
# Move and copy files to the results directory
cp $0 ${resultsDir}
git show --name-only > ${resultsDir}/git-commit.txt
cp plot-idle-times.py ${resultsDir}
cp sum-transmit-times.py ${resultsDir}
cp process-success-collision.py ${resultsDir}
cd ${resultsDir}

# Call the plot-idle-times.py program to generate a plot of idle time vs
# number of nodes:
/usr/bin/python plot-idle-times.py

# Call the sum-transmit-times.py program to generate table data for the 
# transmit times
/usr/bin/python sum-transmit-times.py

# Call the success-collision.py program to generate table data and plot
# for success and collision questions
/usr/bin/python process-success-collision.py

