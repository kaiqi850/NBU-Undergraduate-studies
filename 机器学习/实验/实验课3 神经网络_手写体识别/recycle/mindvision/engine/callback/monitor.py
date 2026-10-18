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
""" Init for base architecture engine monitor register. """

import time
import os
import stat
import numpy as np

import mindspore as ms
from mindspore import save_checkpoint
from mindspore.train.callback import Callback
from mindvision.check_param import Rel, Validator as validator


class LossMonitor(Callback):
    """
    Loss Monitor for classification.

    Usage:
        >>> monitor = LossMonitor(lr_init=lr.asnumpy())
    """

    def __init__(self, lr_init=None, per_print_times=1):
        super(LossMonitor, self).__init__()
        self.lr_init = lr_init
        self.per_print_times = per_print_times
        self.last_print_time = 0

    # pylint: disable=unused-argument
    def epoch_begin(self, run_context):
        self.losses = []
        self.epoch_time = time.time()

    def epoch_end(self, run_context):
        callback_params = run_context.original_args()
        epoch_mseconds = (time.time() - self.epoch_time) * 1000
        per_step_mseconds = epoch_mseconds / callback_params.batch_num
        print(f"Epoch time: {epoch_mseconds:5.3f} ms, "
              f"per step time: {per_step_mseconds:5.3f} ms, "
              f"avg loss: {np.mean(self.losses):5.3f}", flush=True)

    # pylint: disable=unused-argument
    def step_begin(self, run_context):
        self.step_time = time.time()

    def step_end(self, run_context):
        """After step end print training info."""
        callback_params = run_context.original_args()
        step_mseconds = (time.time() - self.step_time) * 1000
        loss = callback_params.net_outputs

        if isinstance(loss, (tuple, list)):
            if isinstance(loss[0], ms.Tensor) and isinstance(loss[0].asnumpy(), np.ndarry):
                loss = loss[0]

        if isinstance(loss, ms.Tensor) and isinstance(loss.asnumpy(), np.ndarray):
            loss = np.mean(loss.asnumpy())

        self.losses.append(loss)
        cur_step_in_epoch = (callback_params.cur_step_num - 1) % callback_params.batch_num + 1

        # Boundary check.
        if isinstance(loss, float) and (np.isnan(loss) or np.isinf(loss)):
            raise ValueError(f"Invalid loss, terminate training.")

        def print_info():
            lr_output = self.lr_init[callback_params.cur_step_num - 1] if isinstance(self.lr_init,
                                                                                     list) else self.lr_init
            print(f"Epoch:[{(callback_params.cur_epoch_num - 1):3d}/{callback_params.epoch_num:3d}], "
                  f"step:[{cur_step_in_epoch:5d}/{callback_params.batch_num:5d}], "
                  f"loss:[{loss:5.3f}/{np.mean(self.losses):5.3f}], "
                  f"time:{step_mseconds:5.3f} ms, "
                  f"lr:{lr_output:5.5f}", flush=True)

        if (callback_params.cur_step_num - self.last_print_time) >= self.per_print_times:
            self.last_print_time = callback_params.cur_step_num
            print_info()


class ValAccMonitor(Callback):
    """
    Train loss and validation accuracy monitor, after each epoch save the
    best checkpoint file with highest validation accuracy.

    Usage:
        >>> monitor = TrainLossAndValAccMonitor(model, dataset_val, num_epochs=10)
    """

    def __init__(self,
                 model,
                 dataset_val,
                 num_epochs,
                 interval=1,
                 eval_start_epoch=1,
                 save_best_ckpt=True,
                 ckpt_directory="./",
                 best_ckpt_name="best.ckpt",
                 metric_name="Accuracy",
                 dataset_sink_mode=True):
        super(ValAccMonitor, self).__init__()
        self.model = model
        self.dataset_val = dataset_val
        self.num_epochs = num_epochs
        self.eval_start_epoch = eval_start_epoch
        self.save_best_ckpt = save_best_ckpt
        self.metric_name = metric_name
        self.interval = validator.check_int(interval, 1, Rel.GE, "interval")
        self.best_res = 0
        self.dataset_sink_mode = dataset_sink_mode

        if not os.path.isdir(ckpt_directory):
            os.makedirs(ckpt_directory)
        self.best_ckpt_path = os.path.join(ckpt_directory, best_ckpt_name)

    def apply_eval(self):
        """Model evaluation, return validation accuracy."""
        return self.model.eval(self.dataset_val, dataset_sink_mode=self.dataset_sink_mode)[self.metric_name]

    def epoch_end(self, run_context):
        """
        After epoch, print train loss and val accuracy,
        save the best ckpt file with highest validation accuracy.
        """
        callback_params = run_context.original_args()
        cur_epoch = callback_params.cur_epoch_num

        if cur_epoch >= self.eval_start_epoch and (cur_epoch - self.eval_start_epoch) % self.interval == 0:
            # Validation result
            res = self.apply_eval()

            print("-" * 20)
            print(f"Epoch: [{cur_epoch: 3d} / {self.num_epochs: 3d}], "
                  f"Train Loss: [{callback_params.net_outputs.asnumpy() :5.3f}], "
                  f"{self.metric_name}: {res: 5.3f}")

            def remove_ckpt_file(file_name):
                os.chmod(file_name, stat.S_IWRITE)
                os.remove(file_name)

            # Save the best ckpt file
            if res >= self.best_res:
                self.best_res = res
                if self.save_best_ckpt:
                    if os.path.exists(self.best_ckpt_path):
                        remove_ckpt_file(self.best_ckpt_path)
                    save_checkpoint(callback_params.train_network, self.best_ckpt_path)

    # pylint: disable=unused-argument
    def end(self, run_context):
        print("=" * 80)
        print(f"End of validation the best {self.metric_name} is: {self.best_res: 5.3f}, "
              f"save the best ckpt file in {self.best_ckpt_path}", flush=True)
