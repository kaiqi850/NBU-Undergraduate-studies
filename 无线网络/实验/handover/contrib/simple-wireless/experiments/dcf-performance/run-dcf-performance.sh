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

# This program runs the wifi-dcf experiment, for the 'Experiment 1 Network
# Saturation Throughput Versus Number Of Nodes' case, and generates a plot
# that can be used for answering question 1.
# 
# Results are stored in a timestamped 'results' directory
# 
# All trace files from each trial (for n=5, 10, 15, etc.) are stored in
# the results directory, so that you can consult them later.  The number of
# stations is suffixed to the file name; e.g. the 
# 'wifi-dcf-rx-error-trace.5.dat' is the trace file corresponding to the 
# n=5 case.  These can be used to answer question 3.
#
# The other main output is the PDF plot named 
# 'wifi-dcf-expt1-throughput-vs-numStas.pdf'

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

dirname=dcf-performance-expt1

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
if [ -e wifi-dcf-expt1.dat ]; then
    echo "Remove existing wifi-dcf-expt1.dat output file from top-level directory?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) echo "Removing..."; rm -rf wifi-dcf-expt1.dat; break;;
            No ) echo "Exiting..."; exit;;
        esac
    done
fi

# Random number generator run number
# For this experiment, you will not need to change this
RngRun=1

mkdir -p ${resultsDir}

# Echo remaining commands to standard output, to track progress
for numStas in 5 10 15 20 25 30 35 40
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
  echo "$numStas $throughputMbps" >> wifi-dcf-expt1.dat
done

# Move plot data file to the results directory
mv wifi-dcf-expt1.dat ${resultsDir}

# Configure the matplotlib plotting program
fileName='wifi-dcf-expt1.dat'
plotName='wifi-dcf-expt1-throughput-vs-numStas.pdf'
plotTitle='Throughput vs. number of nodes'

cd ${resultsDir}
echo `pwd`

if [[ ! -f ../../../utils/plot-lines.py ]]; then
  echo 'plot file not found, exiting...'
  exit
fi

# Specify where the columns of data are to plot.  Here, the xcolumn data
# (numStas) is in column 0, the y column data in column 1
/usr/bin/python ../../../utils/plot-lines.py --title="${plotTitle}" --xlabel='number of STAs' --ylabel='Throughput (Mb/s)' --xcol=0 --ycol=1 --ymax=40 --fileName=${fileName} --plotName=${plotName}

cd $experimentDir

# Move and copy files to the results directory
cp $0 ${resultsDir}
cp ../utils/plot-lines.py ${resultsDir}
git show --name-only > ${resultsDir}/git-commit.txt
