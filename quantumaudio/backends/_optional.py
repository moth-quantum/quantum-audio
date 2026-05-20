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

"""Helpers for guarding optional backend dependencies."""

from __future__ import annotations

import importlib
import importlib.util
from types import ModuleType


def is_available(package: str) -> bool:
    """Check whether *package* can be imported without importing it."""
    return importlib.util.find_spec(package) is not None


def require(
    package: str, extras_name: str | None = None
) -> ModuleType:
    """Import and return *package*, raising a helpful error if missing.

    Only a missing top-level package is converted into the "install
    quantumaudio[<extra>]" hint. Import errors raised inside an
    installed dependency (e.g. due to a broken transitive dep) are
    re-raised unchanged so the original traceback is preserved.

    Args:
        package: Dotted module name, e.g. ``"cirq"`` or ``"qiskit"``.
        extras_name: Optional pip extras hint used in the error message.
    """
    top_level = package.split(".", 1)[0]
    try:
        return importlib.import_module(package)
    except ModuleNotFoundError as e:
        # Only convert "the requested package itself is missing" into
        # the install hint; let nested missing modules propagate.
        if e.name in (package, top_level):
            hint = extras_name or top_level
            raise ImportError(
                f"{package!r} is required but not installed. "
                f"Install it with:  pip install quantumaudio[{hint}]"
            ) from None
        raise
