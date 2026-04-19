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

"""Shared test helpers."""

from qiskit.result.counts import Counts


def counts_from_spaced(d: dict) -> Counts:
    """Build a Qiskit ``Counts`` from a dict whose keys may include spaces
    between register segments.

    The backend layer's ``UnifiedResult.counts`` uses flat bitstrings, but
    spaces in fixture literals make the register boundaries visible at a
    glance (e.g. ``"101 100"`` for amplitude/time). This helper strips
    those spaces so the fixture reads naturally while still producing the
    flat-string format the schemes expect.
    """
    return Counts({k.replace(" ", ""): v for k, v in d.items()})
