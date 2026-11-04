import numpy as np
from quantumaudio.utils import convert


def test_quantize_clips_to_signed_range():
    values = convert.quantize(np.array([1.0, -1.0, 0.0]), 3)
    assert values.tolist() == [3, -4, 0]
