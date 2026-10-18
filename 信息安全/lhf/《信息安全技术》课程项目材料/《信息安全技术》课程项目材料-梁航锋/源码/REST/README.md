#### 一、项目描述

本次《信息安全技术》课程设计提出并实现了一种基于可逆信息嵌入的图像认证与自修复系统， 该系统集成了图像加密、 篡改检测与定位、 图像完整性认证、 图像自修复等功能， 实现了信息的可逆写入技术在图像加密与保护领域的深度应用。 通过可逆水印技术， 结合图像分块、 图像编码、 图像映射等方案， 使系统在加密过程中嵌入信息， 且图像在遭受篡改时能够准确定位篡改区域，并能够进行自恢复操作， 极大地增强了图像数据的完整性与可信度，为数字图像的安全防护提供了强有力的支持。

此外，本项目还聚焦于软件业务的设计与用户体验的优化。我们采用 PyQt 这一强大的图形用户界面框架，为用户构建了直观、美观且易于操作的应用界面。该界面不仅简化了图像加密、解密及篡改检测的操作流程，还通过清晰的提示与反馈机制，提升了用户的整体使用体验。 综上， 该系统为数字图像的安全保护提供了有效手段。

#### 二、运行环境说明

详见requirements文档。

```
imageio==2.34.2
matplotlib==3.8.3
numpy==1.22.4
opencv_python==4.6.0.66
pandas==2.2.2
PyQt5==5.15.10
PyQt5_sip==12.11.0
PyQt5_sip==12.13.0
scikit_learn==1.4.1.post1
```

使用以下命令安装项目所需环境。或者建立conda环境时以requirements作为模板。

```shell
pip install -r requirements.txt
```

#### 三、项目结构说明

**damage_picture**：为一张图像随机生成若干个噪声块，用于对篡改的模拟。

**hamming.py**：海明码的实现，在本项目中作为Hash的生成方式。

**kmeans.py**：图像索引库的训练，所用数据集见后续介绍，生成一个簇心文件，保存于csv文件中。

**login.py与login.ui**：登录界面的实现。

**loginCode.py**：程序的**主入口**。

**Model1.py**：篡改认证与定位的模型实现。

**Model2.py**：图像自修复的实现。

**picture_rc.py与pictures_rc.py**：界面图像的资源文件

**psnr_test.py**：图像峰值信噪比的测试。

**rest.py与rest.ui**：界面资源文件

**RemarkableWatermark.py**：功能模块的入口。

#### 四、运行方式

从**loginCode.py**程序启动即可，默认账号密码为admin与123456

图像索引库的训练执行**kmeans.py**即可，注意指定数据集来源。

图像篡改于**damage_picture.py**中指定源路径、目标路径、篡改块的数量。

#### 五、索引库所用数据集

Flink1024:https://hyper.ai/datasets/9411

![image-20240706170320573](C:\Users\26510\AppData\Roaming\Typora\typora-user-images\image-20240706170320573.png)

STL -10:https://cs.stanford.edu/~acoates/stl10/

![image-20240706170548656](C:\Users\26510\AppData\Roaming\Typora\typora-user-images\image-20240706170548656.png)
