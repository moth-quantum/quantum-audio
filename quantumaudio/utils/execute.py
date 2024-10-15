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

import qiskit_aer
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from typing import Type, Any
import importlib

# Optional Import if exists
_Sampler = (
    getattr(importlib.import_module("qiskit_ibm_runtime"), "SamplerV2", None)
    if importlib.util.find_spec("qiskit_ibm_runtime")
    else None
)

# Default Backend
_default_backend = qiskit_aer.AerSimulator()

# ---- Default Execute Function ----


def execute(
    circuit: "qiskit.QuantumCircuit",
    shots: int = 8000,
    backend: Any = None,
    keep_memory: bool = False,
    optimization_level: int = 3,
):
    """
    Executes a quantum circuit on a given backend and return the results.

    Args:
        circuit: The quantum circuit to be executed.
        backend: The backend on which to run the circuit. If None, the default backend `qiskit_aer.AerSimulator()` is used.
        shots: Total number of times the quantum circuit is measured.
        keep_memory: Whether to return the memory (quantum state) of each shot.
        optimization_level: Optimization level for transpiling the circuit.

    Returns:
        Result: The result of the execution, containing the counts and other metadata.
    """
    assert shots > 0, "Number of shots cannot be 0"
    backend = _default_backend if not backend else backend

    transpiler = _load_instance(
        generate_preset_pass_manager,
        backend=backend,
        optimization_level=optimization_level,
    )
    transpiled_circuit = transpiler.run(circuit)

    job = backend.run(transpiled_circuit, shots=shots, memory=keep_memory)
    result = job.result()
    return result


# ---- Optional Execute Function ----


def execute_with_sampler(
    circuit: "qiskit.QuantumCircuit",
    backend: Any = None,
    shots: int = 8000,
    optimization_level: int = 3,
):
    """
    Executes a quantum circuit on a given backend using `Sampler Primitive` and return the results.

    Args:
        circuit: The quantum circuit to be executed.
        backend: The backend on which to run the circuit. If None, the default backend `qiskit_aer.AerSimulator()` is used.
        shots: Total number of times the quantum circuit is measured.
        optimization_level: Optimization level for transpiling the circuit.

    Returns:
        Result: The result of the execution, containing the counts and other metadata.
    """
    assert shots > 0, "Number of shots cannot be 0"
    assert _Sampler, "IBM runtime is not installed to use Sampler. It can be installed using `pip install qiskit-ibm-runtime`"
    if not isinstance(circuit, list):
        circuit = [circuit]

    backend = _default_backend if not backend else backend
    sampler = _load_instance(_Sampler, mode=backend)

    transpiler = _load_instance(
        generate_preset_pass_manager,
        backend=backend,
        optimization_level=optimization_level,
    )
    transpiled_circuit = transpiler.run(circuit)

    job = sampler.run(transpiled_circuit, shots=shots)
    result = job.result()

    # Manually pass circuit metadata for `decode_result` method to use when no metadata is passed explicity.
    if not result.metadata and hasattr(result, "_metadata"):
        result._metadata.update(circuit[0].metadata)
    return result


# ---- Helper Functions ----

_cache = {}


def _load_instance(cls: Type, **kwargs: Any) -> Any:
    """Load a instance with specified keyword arguments, caching the result to
    avoid repeated loading for the same parameters especially during `stream` operation.

    Args:
        class (Type): Can be Sampler or Preset Pass Manager object.
        kwargs (dict): Dictionary containing keyword arguments.

    Returns:
        The loaded or cached object.
    """
    cache_key = (cls, frozenset(kwargs.items()))
    if cache_key not in _cache:
        _cache[cache_key] = cls(**kwargs)
    return _cache[cache_key]
