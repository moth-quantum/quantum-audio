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

from quantumaudio.backends.core.types import GateType
from quantumaudio.backends.core.circuit import CircuitSpec, GateOp
from quantumaudio.backends.core.result import UnifiedResult
from quantumaudio.backends.core.backend import (
    Backend,
    BackendRegistry,
    registry,
)

__all__ = [
    "Backend",
    "BackendRegistry",
    "CircuitSpec",
    "GateOp",
    "GateType",
    "UnifiedResult",
    "registry",
]
