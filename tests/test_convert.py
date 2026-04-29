# Copyright 2024 Moth Quantum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==========================================================================

import numpy as np
import pytest

from quantumaudio.utils.convert import quantize


def test_quantize_in_range_unchanged():
    array = np.array([0.0, -0.25, 0.5, 0.75, -0.75, -1.0])
    out = quantize(array, qubit_depth=3)
    # qubit_depth=3 -> integer range [-4, 3]; all values map cleanly.
    assert out.tolist() == [0, -1, 2, 3, -3, -4]


def test_quantize_saturates_positive_overflow():
    # Regression for MQSM/QSM wraparound: input +1.0 at qubit_depth=3
    # used to produce integer +4, which wrote bit pattern 100 into a
    # 3-bit signed register and decoded back as -1.0 (sign flip on
    # every peak sample). Saturate to the max representable value
    # instead.
    array = np.array([1.0, 1.5, 2.0])
    out = quantize(array, qubit_depth=3)
    assert out.tolist() == [3, 3, 3]


def test_quantize_saturates_negative_overflow():
    array = np.array([-1.5, -2.0])
    out = quantize(array, qubit_depth=3)
    # qubit_depth=3 -> min representable integer is -4.
    assert out.tolist() == [-4, -4]


def test_quantize_minus_one_is_representable():
    # -1.0 is the symmetric-looking endpoint but corresponds to the
    # most-negative integer; it must round-trip without saturation.
    array = np.array([-1.0])
    for depth in (3, 4, 8):
        out = quantize(array, qubit_depth=depth)
        assert out.tolist() == [-(2 ** (depth - 1))]


@pytest.mark.parametrize(
    "bad_depth", [0, -1, 1.5, "3", None, True, False, np.int64(0)]
)
def test_quantize_rejects_invalid_qubit_depth(bad_depth):
    array = np.array([0.0, 0.5])
    with pytest.raises(ValueError):
        quantize(array, qubit_depth=bad_depth)


@pytest.mark.parametrize("good_depth", [np.int64(3), np.int32(4), np.uint8(5)])
def test_quantize_accepts_numpy_integer_depth(good_depth):
    # NumPy integer scalars are common when depths come from array
    # metadata; they should be accepted alongside built-in ``int``.
    array = np.array([0.0, -1.0, 0.5])
    out = quantize(array, qubit_depth=good_depth)
    expected = quantize(array, qubit_depth=int(good_depth))
    assert out.tolist() == expected.tolist()