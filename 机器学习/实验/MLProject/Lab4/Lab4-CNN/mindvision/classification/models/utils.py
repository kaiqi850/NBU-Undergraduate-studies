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
"""Utils."""

from typing import Optional


def make_divisible(v: float,
                   divisor: int,
                   min_value: Optional[int] = None
                   ) -> int:
    """
    It ensures that all layers have a channel number that is divisible by 8.

    Args:
        v (int): original channel of kernel.
        divisor (int): Divisor of the original channel.
        min_value (int, optional): Minimum number of channels.

    Returns:
        Number of channel.

    Examples:
        >>> _make_divisible(32, 8)
    """

    if not min_value:
        min_value = divisor
    new_v = max(min_value, int(v + divisor / 2) // divisor * divisor)
    # Make sure that round down does not go down by more than 10%.
    if new_v < 0.9 * v:
        new_v += divisor
    return new_v
