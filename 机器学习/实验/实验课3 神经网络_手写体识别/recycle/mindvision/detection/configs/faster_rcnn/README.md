# Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks

## Faster R-CNN 描述

在Faster R-CNN之前，目标检测网络依靠区域候选算法来假设目标的位置，如SPPNet、Fast R-CNN等。研究结果表明，这些检测网络的运行时间缩短了，但区域方案的计算仍是瓶颈。

Faster R-CNN提出，基于区域检测器（如Fast R-CNN）的卷积特征映射也可以用于生成区域候选。在这些卷积特征的顶部构建区域候选网络（RPN）需要添加一些额外的卷积层（与检测网络共享整个图像的卷积特征，可以几乎无代价地进行区域候选），同时输出每个位置的区域边界和客观性得分。因此，RPN是一个全卷积网络，可以端到端训练，生成高质量的区域候选，然后送入Fast R-CNN检测。

[论文](https://arxiv.org/abs/1506.01497)：   Ren S , He K , Girshick R , et al. Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2015, 39(6).

## 模型性能(基于MindSpore1.3.0)

| Pre-trained Backbone |  Platform  | Lr schd | Training Time@单卡 | box AP@0.5 | Config | Download |
| :-------------: | :-----: | :-----: | :------------: | :----: | :------: | :--------: |
| R-50-FPN | Ascend 910 |   1x    | 20.7h@105 ms/step | 60.2 |        |          |
|     R-50-SE-FPN      | Ascend 910 |   1x    | 22.4h@114 ms/step  |    60.3    |        |          |
|       R-50-FPN       | Ascend 910 |   20e   | 34.5h@105 ms/step  |    61.7    |        |          |
|      R-101-FPN       | Ascend 910 |   1x    | 23.2h@118 ms/step  |    62.1    |        |          |
|      R-101-FPN       | Ascend 910 |   20e   | 38.6h@118 ms/step  |    63.3    |        |          |
|      R-152-FPN       | Ascend 910 |   1x    | 25.7h@131 ms/step  |    63.4    |        |          |
|      R-152-FPN       | Ascend 910 |   20e   | 42.8h@131 ms/step  |    64.5    |        |          |
|    X-50-32x4d-FPN    | Ascend 910 |   1x    | 24.8h@127 ms/step  |    61.5    |        |          |
|   X-101-64x4d-FPN    | Ascend 910 |   1x    | 40.9h@209 ms/step  |    65.3    |        |          |
|                      |            |         |                    |            |        |          |
|                      |            |         |                    |            |        |          |