import qiskit_aer
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from typing import Type, Any

_default_backend = qiskit_aer.AerSimulator()

# ---- Default Execute Function ----

def execute(circuit, shots=4000, backend=None, keep_memory=False, optimization_level=3):
    """
    Executes a quantum circuit on a given backend and return the results.

    Args:
        circuit: The quantum circuit to be executed.
        backend: The backend on which to run the circuit. If None, the default backend `qiskit_aer.AerSimulator()` is used.
        shots: Total number of times the quantum circuit is measured.
        memory: Whether to return the memory (quantum state) of each shot.

    Returns:
        Result: The result of the execution, containing the counts and other metadata.
    """
    backend = _default_backend if not backend else backend
    
    transpiler = _load_instance(generate_preset_pass_manager,backend=backend,optimization_level=optimization_level)
    transpiled_circuit = transpiler.run(circuit)
    
    job = backend.run(transpiled_circuit, shots=shots, memory=keep_memory)
    result = job.result()
    return result


# ---- Helper Functions ----

_cache = {}

def _load_instance(cls: Type, **kwargs: Any) -> Any:
    cache_key = (cls, frozenset(kwargs.items()))
    if cache_key not in _cache:
        print('loading first time')
        _cache[cache_key] = cls(**kwargs)
    return _cache[cache_key]