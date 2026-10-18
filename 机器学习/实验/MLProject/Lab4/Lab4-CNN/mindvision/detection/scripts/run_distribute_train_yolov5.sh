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

if [ $# != 1 ]
then
    echo "Usage: sh run_distribute_train.sh [RANK_TABLE_FILE]"
exit 1
fi

get_real_path(){
  if [ "${1:0:1}" == "/" ]; then
    echo "$1"
  else
    echo "$(realpath -m $PWD/$1)"
  fi
}

RANK_TABLE_FILE=$(get_real_path $1)
echo $RANK_TABLE_FILE

if [ ! -f $RANK_TABLE_FILE ]
then
    echo "error: RANK_TABLE_FILE=$RANK_TABLE_FILE is not a file"
exit 1
fi

export DEVICE_NUM=8
export RANK_SIZE=8
export RANK_TABLE_FILE=$RANK_TABLE_FILE

cpus=`cat /proc/cpuinfo| grep "processor"| wc -l`
avg=`expr $cpus \/ $RANK_SIZE`
gap=`expr $avg \- 1`
if [ -d "dist_train" ];
then
    rm -rf ./eval
fi
mkdir ./dist_train
for((i=0;i<${RANK_SIZE};i++));
do
    start=`expr $i \* $avg`
    end=`expr $start \+ $gap`
    cmdopt=$start"-"$end
    export DEVICE_ID=$i
    export RANK_ID=$i
    mkdir ./dist_train/train_parallel$i
    cd ./dist_train/train_parallel$i || exit
    echo "start training for rank $RANK_ID, device $DEVICE_ID"
    env > env.log
    taskset -c $cmdopt python ../../tools/train.py \
        --device_id=${DEVICE_ID} \
        --config=../../configs/yolo/yolov5_coco.yaml \
        --work_dir=./dist_train > log.txt 2>&1 &
    cd ../..
done

