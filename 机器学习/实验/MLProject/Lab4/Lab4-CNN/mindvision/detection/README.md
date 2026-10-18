# 简介

MindDetection 是 mindvision 视觉检测项目下重要的组成部分之一，整套代码基于华为自主研发的开源AI框架 MindSpore 开发，旨在为广大用户提供一套易学、易懂、易用和更快、更准、更泛化的图像检测算法箱，降低AI图像检测门槛。

主分支代码目前支持 MindSpore 1.2 版本

# 主要特色

* Ascend 计算特性

  MindDetection 基于MindSpore开源AI框架，不仅支持华为自研的NPU计算方式，还支持目前主流的CPU\GPU计算，并且具有异构加速的张量可微编程能力。

* 模块化设计

  MindDetection 将检测框架解耦成不同的模块组件，为用户提供多种模块组合方式，通过组合不同的模块组件，用户可以快速便捷的搭建一个属于自己的目标检测模型。

* 模块注册机制

  MindDetection 将检测所用的模块通过注册机制，将模块地址方式注册到字典中，用户可通过配置config文件，便捷实现各模块的注册。

* 速度快

  /testing

* 性能高

  /testing

# 更新日志

pass

# 模型库

## 已支持的BackBone网络：

-[x] ResNet
-[x] DarkNet

## 已支持的算法：

-[x] Faster-R-CNN
-[x] YOLOv3

# 快速入门

以使用项目中的Faster-R-CNN为例，使用MindDetection中相关接口函数，可快速完成模型训练、评估及推理过程。

进入mindvision/detection目录下，执行以下操作：

## Train

```python
python tools/train.py --config configs/faster_rcnn/faster_rcnn_r50_fpn.yaml \
                      --work_dir outputs
```

## Eval

```python
python tools/eval.py --config configs/faster_rcnn/faster_rcnn_r50_fpn.yaml \
                     --ann_file /home/ma-user/work/dataset/annotations/instances_val2017.json \
                     --checkpoint_path best_faster_rcnn.ckpt \
                     --work_dir outputs
```

## Infer

```python
python tools/predict.py --config configs/faster_rcnn/faster_rcnn_r50_fpn.yaml \
                        --img_file ./pictures  \
                        --checkpoint_path best_faster_rcnn.ckpt \
                        --work_dir outputs \
                        --save_dir det_results
```

本项目为众智开发者提供了Detection套件众智一站式导航，方便开发者快速了解套件信息和使用方案：[Detection套件众智一站式导航界面](https://gitee.com/mindspore/vision/wikis/Detection%E5%A5%97%E4%BB%B6%E4%BC%97%E6%99%BA%E4%B8%80%E7%AB%99%E5%BC%8F%E5%AF%BC%E8%88%AA?sort_id=4279805)

