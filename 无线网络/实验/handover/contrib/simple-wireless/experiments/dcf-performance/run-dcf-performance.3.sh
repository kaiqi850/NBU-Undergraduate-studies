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

# This program runs the wifi-dcf experiment, for the 'Experiment 3 Network
# Saturation Throughput Versus Max. Retransmission Stage' case, 
# and generates a plot that can be used for answering question 3.
# 
# Results are stored in a timestamped 'results' directory
# 
# All trace files from each trial (for different limits) are stored in
# the results directory, so that you can consult them later.  The number of
# stations is suffixed to the file name; e.g. the 
# 'wifi-dcf-rx-error-trace.2.dat' is the trace file corresponding to the 
# K=2 case.
#
# The other main output is the PDF plot named 
# 'wifi-dcf-expt3-throughput-vs-max-retrans-stage.pdf'

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

dirname=dcf-performance-expt3

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
if [ -e wifi-dcf-expt3.dat ]; then
    echo "Remove existing wifi-dcf-expt3.dat output file from top-level directory?"
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

numStas=20
cwmin=15

mkdir -p ${resultsDir}

# Echo remaining commands to standard output, to track progress
for K in 2 4 6 8 10 12 14 16 18 20
do
  arrivalRate=$(calc 4000/$numStas)
  cwmax=$(bc -l <<< "($cwmin + 1) * (2^$K) -1")
  set -x
  ./waf --run "wifi-dcf --numStas=${numStas} --packetArrivalRate=${arrivalRate} --cwMin=${cwmin} --cwMax=${cwmax}"
  { set +x; } 2>/dev/null
  packets=$(wc -l wifi-dcf-ap-rx-trace.dat | awk '{ print $1 }' )
  if [ -f wifi-dcf-0-0.pcap ]; then
    mv wifi-dcf-0-0.pcap ${resultsDir}/wifi-dcf-0-0.${K}.pcap
  fi
  if [ -f wifi-dcf-animation.xml ]; then
    mv wifi-dcf-animation.xml ${resultsDir}/wifi-dcf-animation.${K}.xml
  fi
  if [ -f wifi-dcf-ap-rx-trace.dat ]; then
    mv wifi-dcf-ap-rx-trace.dat ${resultsDir}/wifi-dcf-ap-rx-trace.${K}.dat
  fi
  if [ -f wifi-dcf-rx-error-trace.dat ]; then
    mv wifi-dcf-rx-error-trace.dat ${resultsDir}/wifi-dcf-rx-error-trace.${K}.dat
  fi
  if [ -f wifi-dcf-rx-ok-trace.dat ]; then
    mv wifi-dcf-rx-ok-trace.dat ${resultsDir}/wifi-dcf-rx-ok-trace.${K}.dat
  fi
  if [ -f wifi-dcf-state-trace.dat ]; then
    mv wifi-dcf-state-trace.dat ${resultsDir}/wifi-dcf-state-trace.${K}.dat
  fi
  if [ -f wifi-dcf-sta-tx-trace.dat ]; then
    mv wifi-dcf-sta-tx-trace.dat ${resultsDir}/wifi-dcf-sta-tx-trace.${K}.dat
  fi
  if [ -f wifi-dcf.tr ]; then
    mv wifi-dcf.tr ${resultsDir}/wifi-dcf.${K}.tr
  fi
  # Compute the throughput and append it to the data file that will be plotted
  throughput=$(bc -l <<< "$packets * 1900 * 8 / 10")
  throughputMbps=$(bc -l <<< "$throughput / 1000000")
  echo "$K $throughputMbps" >> wifi-dcf-expt3.dat
done

# Move plot data file to the results directory
mv wifi-dcf-expt3.dat ${resultsDir}/wifi-dcf-expt3.${numStas}.dat

# Configure the matplotlib plotting program
fileName="wifi-dcf-expt3.${numStas}.dat"
plotName="wifi-dcf-expt3-throughput-vs-max-retrans-stage.${numStas}.pdf"
plotTitle="Throughput vs. max. retransmission stage (numStas=${numStas})"

cd ${resultsDir}
echo `pwd`

if [[ ! -f ../../../utils/plot-lines.py ]]; then
  echo 'plot file not found, exiting...'
  exit
fi

# Specify where the columns of data are to plot.  Here, the xcolumn data
# (K) is in column 0, the y column data in column 1
/usr/bin/python ../../../utils/plot-lines.py --title="${plotTitle}" --xlabel='Max. retransmission stage (K)' --ylabel='Throughput (Mb/s)' --xcol=0 --ycol=1 --ymax=40 --fileName=${fileName} --plotName=${plotName}

cd $experimentDir

# Move and copy files to the results directory
cp $0 ${resultsDir}
cp ../utils/plot-lines.py ${resultsDir}
git show --name-only > ${resultsDir}/git-commit.txt
