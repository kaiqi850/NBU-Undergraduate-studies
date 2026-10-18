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
"""The chart API of paper experiment part."""

from typing import Optional, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import ImageGrid

from mindvision.check_param import Validator

font_format = {
    'family': 'Arial',
    'size': 12
}

# color offers 20 types
color = [
    'darkred',
    'darkgrey',
    'royalblue',
    'pink',
    'forestgreen',
    'steelblue',
    'orange',
    'black',
    'darkorange',
    'slategrey',
    'lightpink',
    'rosybrown',
    'goldenrod',
    'mediumturquoise',
    'mediumpurple',
    'slategray',
    'saddlebrown',
    'lawngreen',
    'purple',
    'teal']

# marker offers 20 types
marker = ['s', '*', 'o', '8', 'v',
          '<', '>', 'h', 'x', '^',
          's', 'P', 'd', 'P', 'D',
          '1', '2', '3', '4', '.']


def topn_accuracy_chart(accuracy_data: Dict,
                        save_path: str = './',
                        ylim: Optional[List] = None,
                        figsize: Optional[Tuple] = None,
                        title: Optional[str] = None,
                        xlabel: Optional[str] = None,
                        ylabel: Optional[str] = None
                        ):
    """
    Accuracy charts, xlabel can be network models or iteration numbers, ylabel is the accuracy.

    Args:
        accuracy_data(dict): The accuracy data of models on different AI frame.
        save_path(str): The save path of line chart.
        ylim (list, optional): The range of y coordinate. Default: None.
        figsize (tuple, optional): The size of figure. Default: None.
        title(str): The title of graph. Default:None.
        xlabel(str): The Label of x coordinate. Default: None.
        ylabel(str): The Label of y coordinate. Default: None.

    Examples:
        >>> accuracy_data = {'MindSpore': {'Resnet18': 70.078, 'Resnet34': 73.72, 'Resnet50': 76.6},
                             'Pytorch': {'Resnet18': 69.758, 'Resnet34': 73.31, 'Resnet50': 76.13}}
        >>> topn_accuracy_chart(accuracy_data=accuracy_data)
    """

    plt.figure(figsize=figsize)

    for index, (label, data) in enumerate(accuracy_data.items()):
        if index >= len(color):
            raise ValueError(f'The number of labels exceeds {len(color)}.')
        x, y = [], []
        for key, value in data.items():
            x.append(key)
            y.append(value)
        plt.plot(x, y, color=color[index], marker=marker[index], label=label)

    rotation = 90 if len(x[0]) > 8 else None

    plt.legend(fontsize=font_format['size'])
    plt.xlabel(xlabel, fontdict=font_format)
    plt.ylabel(ylabel, fontdict=font_format)
    plt.xticks(fontsize=font_format['size'] - 2, rotation=rotation)
    plt.yticks(fontsize=font_format['size'] - 2, rotation=rotation)
    plt.title(title, fontdict=font_format)
    plt.grid(linestyle='--')
    plt.ylim(ylim)
    plt.savefig(save_path, bbox_inches="tight")


def accuracy_on_dataset_chart_v1(accuracy_data: Dict,
                                 save_path: str = './',
                                 ylim: Optional[List] = None,
                                 figsize: Optional[Tuple] = None,
                                 title: Optional[str] = None,
                                 xlabel: Optional[str] = None,
                                 ylabel: Optional[str] = None
                                 ):
    """
    The function is used to plot the accuracy range between models on different dataset.

    Args:
        accuracy_data (dict): The data of line chart models.
        save_path (str): Path to save the chart. Default: './'.
        ylim (list, optional): The range of y coordinate. Default: None.
        figsize (tuple, optional): The size of figure. Default: None.
        title (str): The title of chart. Default:None.
        xlabel (str): The Label of x coordinate. Default: None.
        ylabel (str): The Label of y coordinate. Default: None.

    Examples:
        >>> accuracy_data = {
                'ResNet50': {
                    'accuracy': {
                        'ImageNet': 76.8,
                        'ImageNet21K': 80.2,
                        'JFT-300M': 79.2,
                    },
                    'marker_size': 4
                },
                'ResNet152': {
                    'accuracy': {
                        'ImageNet': 81.2,
                        'ImageNet21K': 85.5,
                        'JFT-300M': 87.8,
                    },
                    'marker_size': 6
                }
            }
       >>> accuracy_on_dataset_chart_v1(accuracy_data=accuracy_data)
   """

    plt.figure(figsize=figsize)
    len_of_models = len(list(accuracy_data.keys()))
    Validator.check_equal_int(len_of_models, 2, 'The Number of line chart models')

    shade_x, shade_y = [], []
    for model, data in accuracy_data.items():
        line_chart_x = []
        line_chart_y = []
        for dataset, accuracy in data['accuracy'].items():
            line_chart_x.append(dataset)
            line_chart_y.append(accuracy)

        plt.plot(
            line_chart_x,
            line_chart_y,
            c='darkgrey',
            marker='s',
            markersize=data['marker_size'],
            label=model,
            alpha=0.5)
        shade_x.append(line_chart_x)
        shade_y.append(line_chart_y)

    assert shade_x[0] == shade_x[1]
    plt.fill_between(
        shade_x[0],
        shade_y[0],
        shade_y[1],
        facecolor='darkgrey',
        alpha=0.1)

    y_major_locator = plt.MultipleLocator(5)
    y_minor_locator = plt.MultipleLocator(1)

    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    ax.yaxis.set_minor_locator(y_minor_locator)

    plt.legend(fontsize=font_format['size'])
    plt.xlabel(xlabel, fontdict=font_format)
    plt.ylabel(ylabel, fontdict=font_format)
    plt.xticks(fontsize=font_format['size'] - 2)
    plt.yticks(fontsize=font_format['size'] - 2)
    plt.title(title, fontdict=font_format)
    plt.grid(which='minor', linestyle=':', alpha=0.3)
    plt.grid(which='major', linestyle='-', linewidth=1.0, alpha=0.5)
    plt.ylim(ylim)
    plt.savefig(save_path, bbox_inches="tight")


def accuracy_on_dataset_chart_v2(accuracy_data: Dict,
                                 save_path: str = './',
                                 ylim: Optional[List] = None,
                                 figsize: Optional[Tuple] = None,
                                 title: Optional[str] = None,
                                 xlabel: Optional[str] = None,
                                 ylabel: Optional[str] = None
                                 ):
    """
    The function is used to plot the accuracy comparison between models on different dataset.

    Args:
        accuracy_data (dict): The data of scatter models.
        save_path (str): Path to save the chart. Default: './'.
        ylim (list, optional): The range of y coordinate. Default: None.
        figsize (tuple, optional): The size of figure. Default: None.
        title (str): The title of chart. Default:None.
        xlabel (str): The Label of x coordinate. Default: None.
        ylabel (str): The Label of y coordinate. Default: None.

    Examples:
        >>> accuracy_data = {
                'ViT-B_32': {
                    'accuracy': {
                        'ImageNet': 73.38,
                        'ImageNet21K': 81.28,
                        'JFT-300M': 80.73,
                    },
                    'marker_size': 45
                }
            }
       >>> accuracy_on_dataset_chart_v2(accuracy_data=accuracy_data)
   """

    plt.figure(figsize=figsize)

    for index, (model, data) in enumerate(accuracy_data.items()):
        scatter_x, scatter_y = [], []
        for dataset, accuracy in data['accuracy'].items():
            scatter_x.append(dataset)
            scatter_y.append(accuracy)

        plt.scatter(scatter_x,
                    scatter_y,
                    c=color[index + 2],
                    s=data['marker_size'],
                    marker='o',
                    label=model,
                    alpha=0.5)

    y_major_locator = plt.MultipleLocator(5)
    y_minor_locator = plt.MultipleLocator(1)

    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    ax.yaxis.set_minor_locator(y_minor_locator)

    plt.legend(fontsize=font_format['size'])
    plt.xlabel(xlabel, fontdict=font_format)
    plt.ylabel(ylabel, fontdict=font_format)
    plt.xticks(fontsize=font_format['size'] - 2)
    plt.yticks(fontsize=font_format['size'] - 2)
    plt.title(title, fontdict=font_format)
    plt.grid(which='minor', linestyle=':', alpha=0.3)
    plt.grid(which='major', linestyle='-', linewidth=1.0, alpha=0.5)
    plt.ylim(ylim)
    plt.savefig(save_path, bbox_inches="tight")


def accuracy_on_dataset_chart_v3(line_models_data: Dict,
                                 scatter_models_data: Dict,
                                 save_path: str = './',
                                 ylim: Optional[List] = None,
                                 figsize: Optional[Tuple] = None,
                                 title: Optional[str] = None,
                                 xlabel: Optional[str] = None,
                                 ylabel: Optional[str] = None
                                 ):
    """
    The function is used to plot the accuracy comparison between architectures on different dataset.

    Args:
        line_models_data (dict): The data of line chart models.
        scatter_models_data (dict): The data of scatter models.
        save_path (str): Path to save the chart. Default: './'.
        ylim (list, optional): The range of y coordinate. Default: None.
        figsize (tuple, optional): The size of figure. Default: None.
        title (str): The title of chart. Default:None.
        xlabel (str): The Label of x coordinate. Default: None.
        ylabel (str): The Label of y coordinate. Default: None.

    Examples:
        >>> line_models_data = {
                'ResNet50': {
                    'accuracy': {
                        'ImageNet': 76.8,
                        'ImageNet21K': 80.2,
                        'JFT-300M': 79.2,
                    },
                    'marker_size': 4
                },
                'ResNet152': {
                    'accuracy': {
                        'ImageNet': 81.2,
                        'ImageNet21K': 85.5,
                        'JFT-300M': 87.8,
                    },
                    'marker_size': 6
                }
            }
        >>> scatter_models_data = {
                'ViT-B_32': {
                    'accuracy': {
                        'ImageNet': 73.38,
                        'ImageNet21K': 81.28,
                        'JFT-300M': 80.73,
                    },
                    'marker_size': 45
                }
            }
       >>> accuracy_on_dataset_chart_v3(line_models_data=line_models_data,
                                        scatter_models_data=scatter_models_data)
   """

    plt.figure(figsize=figsize)
    len_of_models = len(list(line_models_data.keys()))
    Validator.check_equal_int(len_of_models, 2, 'The Number of line chart models')
    shade_x, shade_y = [], []

    for model, data in line_models_data.items():
        line_chart_x = []
        line_chart_y = []
        for dataset, accuracy in data['accuracy'].items():
            line_chart_x.append(dataset)
            line_chart_y.append(accuracy)

        plt.plot(
            line_chart_x,
            line_chart_y,
            c='darkgrey',
            marker='s',
            markersize=data['marker_size'],
            label=model,
            alpha=0.5)
        shade_x.append(line_chart_x)
        shade_y.append(line_chart_y)

    for index, (model, data) in enumerate(scatter_models_data.items()):
        scatter_x, scatter_y = [], []
        for dataset, accuracy in data['accuracy'].items():
            scatter_x.append(dataset)
            scatter_y.append(accuracy)

        plt.scatter(scatter_x,
                    scatter_y,
                    c=color[index + 2],
                    s=data['marker_size'],
                    marker='o',
                    label=model,
                    alpha=0.5)

    assert shade_x[0] == shade_x[1]
    plt.fill_between(
        shade_x[0],
        shade_y[0],
        shade_y[1],
        facecolor='darkgrey',
        alpha=0.1)

    y_major_locator = plt.MultipleLocator(5)
    y_minor_locator = plt.MultipleLocator(1)

    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    ax.yaxis.set_minor_locator(y_minor_locator)

    plt.legend(fontsize=font_format['size'], ncol=2)
    plt.xlabel(xlabel, fontdict=font_format)
    plt.ylabel(ylabel, fontdict=font_format)
    plt.xticks(fontsize=font_format['size'] - 2)
    plt.yticks(fontsize=font_format['size'] - 2)
    plt.title(title, fontdict=font_format)
    plt.grid(which='minor', linestyle=':', alpha=0.3)
    plt.grid(which='major', linestyle='-', linewidth=1.0, alpha=0.5)
    plt.ylim(ylim)
    plt.savefig(save_path, bbox_inches="tight")


def accuracy_model_size_chart(accuracy_data: Dict,
                              size_unit: str,
                              save_path: str = './',
                              ylim: Optional[List] = None,
                              figsize: Optional[Tuple] = None,
                              title: Optional[str] = None,
                              xlabel: Optional[str] = None,
                              ylabel: Optional[str] = None
                              ):
    """
    The function is used to plot the accuracy comparison between models on different pre-trained dataset size.

    Args:
        accuracy_data (dict): The accuracy of model on different pre-trained dataset size.
        size_unit: Units for dataset size.
        save_path (str): Path to save the chart. Default: './'.
        ylim (list, optional): The range of y coordinate. Default: None.
        figsize (tuple, optional): The size of figure. Default: None.
        title (str): The title of chart. Default:None.
        xlabel (str): The Label of x coordinate. Default: None.
        ylabel (str): The Label of y coordinate. Default: None.

    Examples:
        >>> accuracy_data = {
                'ViT-b_32': {
                    10: 37,
                    30: 41,
                    100: 41.5
                },
                'ViT-B_32': {
                    10: 38,
                    30: 53,
                    100: 54
                }
            }
        >>> accuracy_model_size_chart(accuracy_data=accuracy_data, size_unit='M')
    """

    plt.figure(figsize=figsize)

    for index, (model, data) in enumerate(accuracy_data.items()):
        x, y = [], []
        for size, accuracy in data.items():
            x.append(size)
            y.append(accuracy)
        plt.plot(x, y, c=color[index], marker='o', markersize=8, label=model)

    y_major_locator = plt.MultipleLocator(10)
    y_minor_locator = plt.MultipleLocator(2)

    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    ax.yaxis.set_minor_locator(y_minor_locator)
    ax.yaxis.grid(which='major', linestyle='-', linewidth=1.0, alpha=0.5)
    ax.yaxis.grid(which='minor', linestyle=':', alpha=0.3)

    plt.xscale('log')
    plt.legend(fontsize=font_format['size'], ncol=3, loc='lower right')
    plt.xlabel(xlabel, fontdict=font_format)
    plt.ylabel(ylabel, fontdict=font_format)

    x_ticks_label = []
    for i in x:
        i = str(i) + size_unit
        x_ticks_label.append(i)

    plt.xticks(x, x_ticks_label, fontsize=font_format['size'] - 2)
    plt.yticks(fontsize=font_format['size'] - 2)
    plt.title(title, fontdict=font_format)
    plt.ylim(ylim)
    plt.savefig(save_path, bbox_inches="tight")


def accuracy_model_flops_chart(accuracy_data: Dict,
                               save_path: str = './',
                               ylim: Optional[List] = None,
                               figsize: Optional[Tuple] = None,
                               title: Optional[str] = None,
                               xlabel: Optional[str] = None,
                               ylabel: Optional[str] = None
                               ):
    """
    The function is used to plot the accuracy comparison between architectures on different pre-trained compute.

    Args:
        accuracy_data (dict): The accuracy of model on different pre-trained compute.
        save_path (str): Path to save the chart. Default: './'.
        ylim (list, optional): The range of y coordinate. Default: None.
        figsize (tuple, optional): The size of figure. Default: None.
        title (str): The title of chart. Default:None.
        xlabel (str): The Label of x coordinate. Default: None.
        ylabel (str): The Label of y coordinate. Default: None.

    Examples:
        >>> accuracy_data = {
                'Transform(ViT)': {
                    "vit-B_32_7": {55: 80.73},
                    "ViT-B_16_7": {224: 84.15},
                    "ViT-L_32_7": {196: 84.37},
                    "ViT-L_16_7": {783: 86.30}
                }
            }
        >>> accuracy_model_flops_chart(accuracy_data=accuracy_data, ylim=[75, 90])
    """

    plt.figure(figsize=figsize)

    for index, (architecture, model_data) in enumerate(accuracy_data.items()):
        x, y = [], []
        for _, data in model_data.items():
            for flops, accuracy in data.items():
                x.append(flops)
                y.append(accuracy)
        plt.scatter(x, y, c=color[index], s=80, marker=marker[index], label=architecture)

    y_major_locator = plt.MultipleLocator(5)
    y_minor_locator = plt.MultipleLocator(1)

    ax = plt.gca()
    ax.yaxis.set_major_locator(y_major_locator)
    ax.yaxis.set_minor_locator(y_minor_locator)

    plt.xscale('log')
    plt.legend(fontsize=font_format['size'], loc='lower right')
    plt.xlabel(xlabel, fontdict=font_format)
    plt.ylabel(ylabel, fontdict=font_format)
    plt.xticks(fontsize=font_format['size'] - 2)
    plt.yticks(fontsize=font_format['size'] - 2)
    plt.grid(which='minor', linestyle=':', alpha=0.3)
    plt.grid(which='major', linestyle='-', linewidth=1.0, alpha=0.5)
    plt.title(title, fontdict=font_format)
    plt.ylim(ylim)
    plt.savefig(save_path, bbox_inches="tight")


def pos_embedding_cosine_chart(pos_embedding: np.ndarray,
                               save_path: str = './',
                               title: Optional[str] = None,
                               xlabel: Optional[str] = None,
                               ylabel: Optional[str] = None,
                               colorbar_label: Optional[str] = None
                               ):
    """
    The function is used to plot the cosine similarity of position embedding.

    Args:
        pos_embedding (ndarray): The data of position embedding.
        save_path (str): Path to save the chart. Default: './'.
        title (str): The title of chart. Default:None.
        xlabel (str): The Label of x coordinate. Default: None.
        ylabel (str): The Label of y coordinate. Default: None.
        colorbar_label: The Label of colorbar. Default: None.

    Examples:
        >>> pos_embedding = np.random.randn(1, 50, 768)
        >>> pos_embedding_cosine_chart(pos_embedding=pos_embedding)
    """

    def cosine_similarity(x, y):
        x_dot_y = x.dot(y)
        l2_norm = np.linalg.norm(x, ord=2) * np.linalg.norm(x, ord=2)
        sim = x_dot_y / l2_norm
        return sim

    pos_embedding = pos_embedding.squeeze()
    rm_cls_pos_embedding = pos_embedding[1:, :]
    num_pos = rm_cls_pos_embedding.shape[0]
    len_side = int(np.sqrt(rm_cls_pos_embedding.shape[0]))
    cos = np.zeros((num_pos, num_pos))

    for i in range(num_pos):
        for j in range(num_pos):
            cos[i, j] = cosine_similarity(rm_cls_pos_embedding[i, :], rm_cls_pos_embedding[j, :])

    cos = cos.reshape((num_pos, len_side, len_side))
    fig = plt.figure(figsize=(len_side, len_side))
    grid = ImageGrid(fig,
                     111,
                     nrows_ncols=(len_side, len_side),
                     share_all=True,
                     axes_pad=0.2,
                     cbar_location="right",
                     cbar_mode="single",
                     cbar_pad=0.2,
                     )

    i = 0
    for ax in grid:
        image = ax.imshow(cos[i, :, :], vmin=-1, vmax=1)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlabel(int(i % len_side + 1), fontsize='xx-large')
        ax.set_ylabel(int(i / len_side + 1), fontsize='xx-large')
        i += 1
        cb = plt.colorbar(image, cax=ax.cax, ticks=[-1, 1])
        cb.set_label(colorbar_label, fontsize='xx-large')

    fig.suptitle(title, fontsize='xx-large')
    fig.supxlabel(xlabel, fontsize='xx-large')
    fig.supylabel(ylabel, fontsize='xx-large')
    plt.savefig(save_path, bbox_inches="tight")
