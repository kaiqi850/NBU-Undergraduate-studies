## Introduction

MindSpore Vision Classification is an open source image classification toolbox based on MindSpore.

## Major features

- Modular Design

We decompose the classification framework into different components and one can easily construct a customized object classification framework by combining different modules.

![](../../resource/classification/classification.architecture.png)

### Supported models

- [x] [LeNet](../../classification/lenet)
- [x] [ResNet](../../classification/resnet)
- [x] [MobileNetV2](../../classification/mobilenetv2)
- [ ] MobileNetV3
- [ ] ResNeXt
- [ ] SE-ResNet
- [ ] SE-ResNeXt
- [ ] RegNet
- [ ] ShuffleNetV1
- [ ] ShuffleNetV2

### Supported datasets

- [x] [MNIST](http://yann.lecun.com/exdb/mnist/)
- [x] [ImageNet2012](https://image-net.org/challenges/LSVRC/index.php)

Please see [getting_dataset_started.ipynb](docs/getting_dataset_started.ipynb) for the basic usage of the interface of datasets.

## Getting Started

Please see [getting_started.ipynb](docs/getting_started.ipynb) for the basic usage of MindSpore Vision classification.

## Feedbacks and Contact

The dynamic version is still under development, if you find any issue or have an idea on new features, please don't hesitate to contact us via [MindSpore Vision Issues](https://gitee.com/mindspore/vision/issues).

## Contributing

We appreciate all contributions to improve MindSpore Vison classification. Please refer to [CONTRIBUTING.md](../../CONTRIBUTING.md) for the contributing guideline.

## Acknowledgement

MindSpore Vison classification is an open source project that welcome any contribution and feedback.

We wish that the toolbox and benchmark could serve the growing research
community by providing a flexible as well as standardized toolkit to reimplement existing methods
and develop their own new classification methods.

## License

This project is released under the [Apache 2.0 license](LICENSE).