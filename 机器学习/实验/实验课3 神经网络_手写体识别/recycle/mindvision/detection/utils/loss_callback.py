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
"""FasterRcnn training network wrapper."""

import os
import time

from mindspore.train.callback import Callback


class LossCallBack(Callback):
    """Monitor the loss in training.

    If the loss is NAN or INF terminating training.

    Note:
        If per_print_times is 0 do not print loss.

    Args:
        per_print_times (int): Print loss every times. Default: 1.
    """

    def __init__(self, save_path, per_print_times=1, rank_id=0):
        super(LossCallBack, self).__init__()
        if not isinstance(per_print_times, int) or per_print_times < 0:
            raise ValueError("Print step must be int and >= 0.")
        self.save_path = save_path
        self._per_print_times = per_print_times
        self.count = 0
        self.loss_sum = 0
        self.rank_id = rank_id
        self.time_stamp_init = False
        self.time_stamp_first = 0

        if not self.time_stamp_init:
            self.time_stamp_first = time.time()
            self.time_stamp_init = True

    def step_end(self, run_context):
        """Callback of step end."""
        cb_params = run_context.original_args()
        loss = cb_params.net_outputs.asnumpy()
        cur_step_in_epoch = (cb_params.cur_step_num - 1) % cb_params.batch_num + 1

        self.count += 1
        self.loss_sum += float(loss)

        if self.count >= 1:
            time_stamp_current = time.time()
            total_loss = self.loss_sum / self.count

            with open(os.path.join(self.save_path, "loss_rank_{}".format(self.rank_id)), "a+") as loss_file:
                loss_file.write("%lu epoch: %s step: %s total_loss: %.5f" %
                                (time_stamp_current - self.time_stamp_first, cb_params.cur_epoch_num, cur_step_in_epoch,
                                 total_loss))
                loss_file.write("\n")

            self.count = 0
            self.loss_sum = 0
