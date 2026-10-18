import torch
import torch.nn as nn


class VGG(nn.Module):
    def __init__(self):
        super(VGG, self).__init__()

        self.features = self.make_features()

        self.classifier = nn.Sequential(
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(p=0.5),
            nn.Linear(4096, 1000)
        )

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, start_dim=1)
        x = self.classifier(x)

        return x

    def make_features(self):
        cfgs = [64, 64, 'MaxPool', 128, 128, 'MaxPool', 256, 256, 256, 'MaxPool', 512, 512, 512, 'MaxPool', 512, 512,
                512, 'MaxPool']

        layers = []
        in_channel = 3

        for cfg in cfgs:
            if cfg == "MaxPool":  # 池化层
                layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
            else:
                layers += [nn.Conv2d(in_channels=in_channel, out_channels=cfg, kernel_size=3, padding=1)]
                layers += [nn.ReLU(True)]
                in_channel = cfg
        return nn.Sequential(*layers)


net = VGG()
print(net)


