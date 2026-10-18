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

# This program runs the link-performance example for different configurations
# and produces a plot of PER vs. the parameter under test.  The current
# version steps through the distance between two devices, but other parameters
# can be substituted for distance.

# Results are stored in a timestamped 'results' directory

set -e
set -o errexit

control_c()
{
  echo "exiting"
  exit $?
}

trap control_c SIGINT

dirname=link-performance
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
if [ -e link-performance-rssi.dat ]; then
    echo "Remove existing file link-performance-rssi.dat from top-level directory?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) echo "Removing..."; rm -rf link-performance-rssi.dat; break;;
            No ) echo "Exiting..."; exit;;
        esac
    done
fi

if [ -e link-performance-summary.dat ]; then
    echo "Removing existing file link-performance-summary.dat from top-level directory?"
    select yn in "Yes" "No"; do
        case $yn in
            Yes ) echo "Removing..."; rm -rf link-performance-summary.dat; break;;
            No ) echo "Exiting..."; exit;;
        esac
    done
fi

# Random number generator run number
RngRun=1

plotName='link-performance-per-vs-distance.pdf'
plotTitle='PER vs. distance'

# Vary the number of packets per trial here
maxPackets=1000
# Transmit power is specified in units of dBm (decibles relative to 1 mW)
# A value of 0 equals 1 mW
transmitPower=0
# Noise power is specified in units of dBm (decibels relative to 1 mW)
noisePower=-90

# If stepping regularly through a distance range, configure here
minDistance=30
maxDistance=80
stepSize=5
# Alternatively, the following kind of for loop can be used to specify 
# the specific values to step through (varying step size)
# for distance in 45 50 55 60 65 70 75 80; do

# Echo remaining commands to standard output, to track progress
set -x
for distance in `seq $minDistance $stepSize $maxDistance`; do
  ./waf --run "link-performance --maxPackets=${maxPackets} --transmitPower=${transmitPower} --noisePower=${noisePower} --distance=${distance} --metadata=${distance} --RngRun=${RngRun}"
done

# Move files from top level directory to the experiments directory
mv link-performance-summary.dat ${experimentDir} 
mv link-performance-rssi.dat ${experimentDir}

cd ${experimentDir}

if [[ ! -f ../utils/plot-lines-with-error-bars.py ]]; then
  echo 'plot file not found, exiting...'
  exit
fi

# Specify where the columns of data are to plot.  Here, the xcolumn data
# (distance) is in column 5, the y column data (PER) in column 3, and the
# length of the error bar is in column 4 
/usr/bin/python ../utils/plot-lines-with-error-bars.py --title="${plotTitle}" --xlabel='distance (m)' --ylabel='Packet Error Ratio (PER)' --xcol=5 --ycol=3 --yerror=4 --fileName=link-performance-summary.dat --plotName=${plotName}

# If script has succeeded to this point, create the results directory
mkdir -p ${resultsDir}
# Move and copy files to the results directory
mv $plotName ${resultsDir} 
mv link-performance-summary.dat ${resultsDir} 
mv link-performance-rssi.dat ${resultsDir} 
cp $0 ${resultsDir}
cp ../utils/plot-lines-with-error-bars.py ${resultsDir}
git show --name-only > ${resultsDir}/git-commit.txt
