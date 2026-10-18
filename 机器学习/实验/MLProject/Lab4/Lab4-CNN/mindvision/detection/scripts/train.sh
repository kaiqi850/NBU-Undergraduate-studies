#!/bin/bash
# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

if [ $# != 3 ]
then
    echo "Usage: bash train_distribute_gpu.sh [DEVICE_NUM] [rank_table_file] [yaml_file]"
    exit 1
fi

current_exec_path=$(pwd)
echo ${current_exec_path}

rm -rf ${current_exec_path}/device*

ulimit -c unlimited

root=${current_exec_path}
rank_table=$root/$2

dirname_path=$root/tools
echo ${dirname_path}

#export PYTHONPATH=${dirname_path}:$PYTHONPATH

echo $rank_table
export RANK_TABLE_FILE=$rank_table
export RANK_SIZE=$1

cpus=`cat /proc/cpuinfo | grep "processor" | wc -l`
task_set_core=`expr $cpus \/ $RANK_SIZE` # for taskset, task_set_core=total cpu number/RANK_SIZE
echo 'start training'
for((i=0;i<=$RANK_SIZE-1;i++));
do
    echo 'start rank '$i
    export RANK_ID=$i
    dev=`expr $i + 0`
    export DEVICE_ID=$dev
    taskset -c $(((i)*task_set_core))-$(((i+1)*task_set_core-1)) python ${dirname_path}/train.py --config $root/$3 --device_id $dev --work_dir outputs >train.log 2>&1 &
done

echo 'running'
