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

"""Gate types for framework-agnostic circuit descriptions."""

from enum import Enum, auto


class GateType(Enum):
    """Universal gate set for quantum audio circuits.

    Covers every operation used by the quantumaudio scheme
    implementations across all supported backends.
    """

    # Single-qubit gates.
    H = auto()
    X = auto()
    Y = auto()
    Z = auto()
    S = auto()
    T = auto()
    RX = auto()
    RY = auto()
    RZ = auto()

    # Two-qubit gates.
    CX = auto()
    CZ = auto()
    CRX = auto()
    CRY = auto()
    CRZ = auto()
    SWAP = auto()

    # Multi-controlled gates.
    MCX = auto()
    MCRY = auto()

    # Measurement.
    MEASURE = auto()

    # Visual separator (no-op for execution).
    BARRIER = auto()
