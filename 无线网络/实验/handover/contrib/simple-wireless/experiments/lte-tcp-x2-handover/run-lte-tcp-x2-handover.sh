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

# This program runs the lte-tcp-x2-handover experiment, and generates five
# plots from the data files.
# 
# Results and all traces are stored in a timestamped 'results' directory,
# as well as the PDFs generated.

set -e
set -o errexit

control_c()
{
  echo "exiting"
  exit $?
}

trap control_c SIGINT

dirname=lte-tcp-x2-handover

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

# Random number generator run number
RngRun=1

mkdir -p ${resultsDir}
cp ${experimentDir}/*-plot.py ${resultsDir}

speed=20
x2Distance=500
yDistanceForUe=1000
useRlcUm=0
handoverType="A2A4"

set -x
./waf --run "lte-tcp-x2-handover --speed=${speed} --x2Distance=${x2Distance} --yDistanceForUe=${yDistanceForUe} --useRlcUm=${useRlcUm} --handoverType=${handoverType}"
{ set +x; } 2>/dev/null

# Move and copy files to the results directory
if [ -f lte-tcp-x2-handover-0-2.pcap ]; then
  mv lte-tcp-x2-handover*.pcap ${resultsDir}
fi
mv lte-tcp-x2-handover.*.dat ${resultsDir}
mv DlMacStats.txt ${resultsDir}

git show --name-only > ${resultsDir}/git-commit.txt

cd ${experimentDir}
cp $0 ${resultsDir}

cd ${resultsDir}

echo "Creating plots"

/usr/bin/python tcp-throughput-plot.py
/usr/bin/python mcs-plot.py
/usr/bin/python cqi-plot.py
/usr/bin/python rsrp-plot.py
/usr/bin/python rsrq-plot.py

