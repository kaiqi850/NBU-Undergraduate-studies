#!/bin/bash

export RANK_ID=0
python tools/train.py --config configs/yolo/yolov5_coco.yaml --work_dir ./outputs
