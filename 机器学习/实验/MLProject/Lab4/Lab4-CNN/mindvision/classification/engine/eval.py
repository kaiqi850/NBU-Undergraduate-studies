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
""" MindSpore Vision Classification evaluation script. """

from mindspore import context, nn, load_checkpoint, load_param_into_net
from mindspore.train import Model

from mindvision.check_param import Validator, Rel
from mindvision.classification.models.builder import build_classifier
from mindvision.engine.dataset.dataloader import build_dataloader
from mindvision.engine.loss.builder import build_loss


def eval_config(config):
    """Use yaml file for eval."""
    context.set_context(**config.context)

    # Data Pipeline.
    dataset_eval = build_dataloader(config.data_loader, types='eval')
    Validator.check_int(dataset_eval.get_dataset_size(), 0, Rel.GT)

    # Create model.
    network = build_classifier(config.model)

    # Define loss function.
    network_loss = build_loss(config.loss)

    # Load pretrained model.
    param_dict = load_checkpoint(config.eval.pretrained_model)
    load_param_into_net(network, param_dict)

    # Define eval_metrics.
    eval_metrics = {'Top_1_Accuracy': nn.Top1CategoricalAccuracy(),
                    'Top_5_Accuracy': nn.Top5CategoricalAccuracy()}

    # Init the model.
    model = Model(network,
                  network_loss,
                  metrics=eval_metrics)

    # Begin to eval.
    result = model.eval(dataset_eval)

    return result
