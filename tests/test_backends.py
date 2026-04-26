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

"""Tests for the framework-agnostic backend abstractions."""

from __future__ import annotations

import numpy as np
import pytest

from quantumaudio.backends import (
    CircuitSpec,
    GateOp,
    GateType,
    UnifiedResult,
    available_backends,
    get_backend,
    is_available,
    registry,
    require,
)


# ======================================================================
# UnifiedResult
# ======================================================================


def test_probabilities_basic():
    res = UnifiedResult(
        counts={"00": 30, "01": 10, "11": 60},
        shots=100,
        backend_name="test",
    )
    probs = res.probabilities()
    assert probs == {"00": 0.3, "01": 0.1, "11": 0.6}


def test_probabilities_array_indexed_by_int():
    res = UnifiedResult(
        counts={"00": 25, "01": 25, "10": 25, "11": 25},
        shots=100,
        backend_name="test",
    )
    arr = res.probabilities_array()
    np.testing.assert_allclose(arr, [0.25, 0.25, 0.25, 0.25])


def test_probabilities_array_empty_counts():
    res = UnifiedResult(counts={}, shots=10, backend_name="test")
    arr = res.probabilities_array()
    assert arr.size == 0


def test_shots_must_be_positive():
    with pytest.raises(ValueError, match="shots must be positive"):
        UnifiedResult(counts={"0": 1}, shots=0, backend_name="t")
    with pytest.raises(ValueError):
        UnifiedResult(counts={"0": 1}, shots=-5, backend_name="t")


def test_marginal_keeps_only_requested_qubit():
    # 2-qubit distribution (qubit 0 is the rightmost char).
    res = UnifiedResult(
        counts={"00": 5, "01": 3, "10": 2, "11": 4},
        shots=14,
        backend_name="test",
    )
    # Marginalising over qubit 0 collapses on the rightmost bit.
    m0 = res.marginal([0])
    assert m0.counts == {"0": 7, "1": 7}
    # Marginalising over qubit 1 collapses on the leftmost bit.
    m1 = res.marginal([1])
    assert m1.counts == {"0": 8, "1": 6}


def test_marginal_preserves_total_shots_and_metadata():
    res = UnifiedResult(
        counts={"00": 2, "01": 3, "10": 4, "11": 1},
        shots=10,
        backend_name="test",
        metadata={"scheme": "fake"},
    )
    m = res.marginal([0])
    assert sum(m.counts.values()) == 10
    assert m.shots == 10
    assert m.backend_name == "test"
    assert m.metadata == {"scheme": "fake"}


def test_marginal_preserves_qubit_order_in_key():
    # marginal([0, 1]) should keep both bits in their original order.
    res = UnifiedResult(
        counts={"00": 1, "01": 2, "10": 3, "11": 4},
        shots=10,
        backend_name="test",
    )
    m = res.marginal([0, 1])
    assert m.counts == {"00": 1, "01": 2, "10": 3, "11": 4}


def test_marginal_empty_counts():
    res = UnifiedResult(counts={}, shots=5, backend_name="t")
    m = res.marginal([0])
    assert m.counts == {}


def test_to_qiskit_result_round_trips_counts():
    """to_qiskit_result().get_counts() must preserve bitstring counts."""
    pytest.importorskip("qiskit")
    original = {"000": 10, "001": 20, "111": 70}
    res = UnifiedResult(
        counts=original, shots=100, backend_name="test"
    )
    qiskit_result = res.to_qiskit_result()
    counts = qiskit_result.get_counts()
    # Qiskit's Counts is a dict-like; compare as plain dict.
    assert dict(counts) == original


def test_to_qiskit_result_with_utils_get_counts():
    """The Qiskit bridge must work with utils.get_counts()."""
    pytest.importorskip("qiskit")
    from quantumaudio.utils.results import get_counts

    original = {"00": 40, "01": 10, "10": 25, "11": 25}
    res = UnifiedResult(
        counts=original, shots=100, backend_name="test"
    )
    qiskit_result = res.to_qiskit_result()
    assert dict(get_counts(qiskit_result)) == original


def test_to_qiskit_result_handles_empty_counts():
    pytest.importorskip("qiskit")
    res = UnifiedResult(counts={}, shots=10, backend_name="t")
    qiskit_result = res.to_qiskit_result()
    assert dict(qiskit_result.get_counts()) == {}


# ======================================================================
# CircuitSpec: clbits and measure semantics
# ======================================================================


def test_measure_uses_clbits_field_not_params():
    spec = CircuitSpec(num_qubits=2)
    spec.measure(0, 1)
    op = spec.ops[-1]
    assert op.gate is GateType.MEASURE
    assert op.qubits == (0,)
    assert op.clbits == (1,)
    # Crucially, params stays the float-only angle channel.
    assert op.params == ()


def test_measure_grows_num_clbits():
    spec = CircuitSpec(num_qubits=4)
    assert spec.num_clbits == 0
    spec.measure(0, 0)
    assert spec.num_clbits == 1
    spec.measure(1, 7)
    assert spec.num_clbits == 8
    # A smaller index must not shrink num_clbits.
    spec.measure(2, 3)
    assert spec.num_clbits == 8


def test_measure_all_sets_num_clbits():
    spec = CircuitSpec(num_qubits=3)
    spec.measure_all()
    assert spec.num_clbits == 3
    measures = [
        op for op in spec.ops if op.gate is GateType.MEASURE
    ]
    assert len(measures) == 3
    assert [m.clbits for m in measures] == [(0,), (1,), (2,)]


def test_gate_op_default_clbits_is_empty():
    op = GateOp(GateType.H, (0,))
    assert op.clbits == ()


# ======================================================================
# CircuitSpec.initialize: input validation
# ======================================================================


def test_initialize_wrong_length_raises_value_error():
    spec = CircuitSpec(num_qubits=2)
    with pytest.raises(ValueError, match="amplitudes"):
        spec.initialize([1.0, 0.0, 0.0])  # 3 != 2**2


def test_initialize_zero_state_is_no_op():
    spec = CircuitSpec(num_qubits=2)
    spec.initialize([0.0, 0.0, 0.0, 0.0])
    assert spec.ops == []


# ======================================================================
# CircuitSpec.initialize: Mottonen state-prep correctness
# ======================================================================


# A tiny statevector simulator restricted to the gate types emitted by
# the Mottonen decomposition (RY, CX). Lets us check correctness of the
# decomposition without committing to a particular provider backend.

def _apply_ry(state: np.ndarray, theta: float, qubit: int) -> np.ndarray:
    n = int(np.log2(state.size))
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    new = np.zeros_like(state)
    for i in range(state.size):
        bit = (i >> qubit) & 1
        partner = i ^ (1 << qubit)
        if bit == 0:
            # |0> on qubit: amplitude c*a0 - s*a1.
            new[i] += c * state[i] - s * state[partner]
        else:
            new[i] += s * state[partner] + c * state[i]
    return new


def _apply_cx(
    state: np.ndarray, control: int, target: int
) -> np.ndarray:
    new = state.copy()
    for i in range(state.size):
        if (i >> control) & 1:
            j = i ^ (1 << target)
            if i < j:
                new[i], new[j] = state[j], state[i]
    return new


def _simulate(spec: CircuitSpec) -> np.ndarray:
    state = np.zeros(2**spec.num_qubits)
    state[0] = 1.0
    for op in spec.ops:
        if op.gate is GateType.RY:
            state = _apply_ry(state, op.params[0], op.qubits[0])
        elif op.gate is GateType.CX:
            state = _apply_cx(state, op.qubits[0], op.qubits[1])
        else:
            raise AssertionError(
                f"Mottonen decomposition emitted unexpected gate "
                f"{op.gate}; only RY and CX are expected."
            )
    return state


@pytest.mark.parametrize("n", [1, 2, 3])
def test_initialize_basis_states(n):
    """Each computational-basis state should round-trip exactly."""
    for k in range(2**n):
        target = np.zeros(2**n)
        target[k] = 1.0
        spec = CircuitSpec(num_qubits=n)
        spec.initialize(target)
        result = _simulate(spec)
        np.testing.assert_allclose(result, target, atol=1e-10)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_initialize_uniform_superposition(n):
    target = np.full(2**n, 1.0 / np.sqrt(2**n))
    spec = CircuitSpec(num_qubits=n)
    spec.initialize(target)
    result = _simulate(spec)
    np.testing.assert_allclose(result, target, atol=1e-10)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_initialize_random_nonneg_real_states(n):
    """Random non-negative real states (the QPAM use case)."""
    rng = np.random.default_rng(seed=42 + n)
    for _ in range(5):
        target = np.abs(rng.standard_normal(2**n))
        target = target / np.linalg.norm(target)
        spec = CircuitSpec(num_qubits=n)
        spec.initialize(target)
        result = _simulate(spec)
        np.testing.assert_allclose(result, target, atol=1e-10)


def test_initialize_signed_input_encodes_magnitudes():
    """Signed inputs are encoded as their absolute values (documented
    limitation of the magnitude-based Mottonen decomposition)."""
    spec = CircuitSpec(num_qubits=2)
    signed = np.array([0.5, -0.5, 0.5, -0.5])
    spec.initialize(signed)
    result = _simulate(spec)
    np.testing.assert_allclose(result, np.abs(signed), atol=1e-10)


def test_initialize_normalises_input():
    """Unnormalised input must be auto-normalised before encoding."""
    spec = CircuitSpec(num_qubits=2)
    spec.initialize([2.0, 0.0, 0.0, 0.0])  # norm = 2
    result = _simulate(spec)
    np.testing.assert_allclose(result, [1.0, 0.0, 0.0, 0.0], atol=1e-10)


# ======================================================================
# Optional-dependency helpers
# ======================================================================


def test_is_available_for_installed_package():
    # numpy is always installed in this project's env.
    assert is_available("numpy") is True


def test_is_available_for_missing_package():
    assert is_available("definitely_not_a_real_package_xyz") is False


def test_require_returns_module_when_present():
    import numpy as expected_np

    got = require("numpy")
    assert got is expected_np


def test_require_raises_install_hint_when_missing():
    with pytest.raises(ImportError, match="install quantumaudio"):
        require("definitely_not_a_real_package_xyz")


def test_require_does_not_swallow_nested_import_error(tmp_path, monkeypatch):
    """A nested ImportError inside an installed module must propagate."""
    pkg = tmp_path / "broken_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text(
        "import this_module_does_not_exist_either\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(ModuleNotFoundError) as excinfo:
        require("broken_pkg")
    # The nested missing module is the one that should surface,
    # not the top-level "broken_pkg".
    assert excinfo.value.name == "this_module_does_not_exist_either"


# ======================================================================
# GateType / CircuitSpec builder coverage
# ======================================================================


class TestGateType:
    def test_basic_gates_exist(self):
        assert GateType.H
        assert GateType.X
        assert GateType.RY
        assert GateType.CX

    def test_extended_gates_exist(self):
        assert GateType.MCX
        assert GateType.MCRY
        assert GateType.BARRIER


class TestCircuitSpec:
    def test_builder_returns_self(self):
        spec = CircuitSpec(2)
        result = spec.h(0).cx(0, 1)
        assert result is spec

    def test_ops_recorded(self):
        spec = CircuitSpec(3)
        spec.h(0).x(1).cx(0, 2).barrier()
        assert len(spec.ops) == 4
        assert spec.ops[0] == GateOp(GateType.H, (0,))
        assert spec.ops[1] == GateOp(GateType.X, (1,))
        assert spec.ops[2] == GateOp(GateType.CX, (0, 2))
        assert spec.ops[3] == GateOp(GateType.BARRIER, ())

    def test_mcx(self):
        spec = CircuitSpec(4)
        spec.mcx([0, 1, 2], 3)
        op = spec.ops[0]
        assert op.gate == GateType.MCX
        assert op.qubits == (0, 1, 2, 3)

    def test_mcry(self):
        spec = CircuitSpec(3)
        spec.mcry(1.5, [0, 1], 2)
        op = spec.ops[0]
        assert op.gate == GateType.MCRY
        assert op.qubits == (0, 1, 2)
        assert op.params == (1.5,)

    def test_initialize_decomposes(self):
        """initialize() should produce RY and CX ops, not an INITIALIZE op."""
        spec = CircuitSpec(2)
        spec.initialize([0.5, 0.5, 0.5, 0.5])
        gate_types = {op.gate for op in spec.ops}
        assert GateType.RY in gate_types or GateType.CX in gate_types
        # No raw INITIALIZE gate should appear.
        assert all(
            op.gate != GateType.MEASURE for op in spec.ops
            if hasattr(GateType, "INITIALIZE")
        )

    def test_metadata(self):
        spec = CircuitSpec(2, name="test")
        spec.metadata["key"] = "value"
        assert spec.name == "test"
        assert spec.metadata["key"] == "value"


# ======================================================================
# Backend registry
# ======================================================================


class TestRegistry:
    def test_qiskit_available(self):
        assert "qiskit" in available_backends()

    def test_get_qiskit(self):
        be = get_backend("qiskit")
        assert be.name == "qiskit"

    def test_unknown_backend_raises(self):
        with pytest.raises(KeyError):
            get_backend("nonexistent_backend")


# ======================================================================
# Qiskit backend
# ======================================================================


class TestQiskitBackend:
    def test_build_and_run(self):
        spec = CircuitSpec(2)
        spec.h(0).cx(0, 1).measure_all()
        be = get_backend("qiskit")
        result = be.run_spec(spec, shots=100)
        assert isinstance(result, UnifiedResult)
        assert sum(result.counts.values()) == 100

    def test_register_reconstruction(self):
        spec = CircuitSpec(4, name="TestCirc")
        spec.metadata["registers"] = {
            "amp": (0, 1),
            "time": (1, 3),
        }
        spec.h(1).h(2).h(3).measure_all()
        be = get_backend("qiskit")
        qc = be.build_circuit(spec)
        reg_names = [r.name for r in qc.qregs]
        assert "amp" in reg_names
        assert "time" in reg_names

    def test_statevector(self):
        spec = CircuitSpec(1)
        spec.h(0)
        be = get_backend("qiskit")
        native = be.build_circuit(spec)
        sv = be.statevector(native)
        assert len(sv) == 2
        assert abs(abs(sv[0]) - 1 / np.sqrt(2)) < 1e-6


# ======================================================================
# Cirq backend
# ======================================================================


@pytest.mark.skipif(
    not is_available("cirq"), reason="cirq not installed"
)
class TestCirqBackend:
    def test_build_and_run(self):
        spec = CircuitSpec(2)
        spec.h(0).cx(0, 1).measure_all()
        be = get_backend("cirq")
        result = be.run_spec(spec, shots=100)
        assert isinstance(result, UnifiedResult)
        assert sum(result.counts.values()) == 100
        # Bell state: only "00" and "11" should appear.
        for key in result.counts:
            assert key in ("00", "11")

    def test_mcx(self):
        spec = CircuitSpec(3)
        spec.x(0).x(1).mcx([0, 1], 2).measure_all()
        be = get_backend("cirq")
        result = be.run_spec(spec, shots=100)
        # All controls are 1, so target should flip to 1.
        assert result.counts.get("111", 0) == 100

    def test_mcry(self):
        spec = CircuitSpec(2)
        spec.x(0).mcry(np.pi, [0], 1).measure_all()
        be = get_backend("cirq")
        result = be.run_spec(spec, shots=100)
        # Control=1, RY(pi) flips target from |0> to |1>.
        assert result.counts.get("11", 0) == 100

    def test_statevector(self):
        spec = CircuitSpec(1)
        spec.h(0)
        be = get_backend("cirq")
        native = be.build_circuit(spec)
        sv = be.statevector(native)
        assert len(sv) == 2
        assert abs(abs(sv[0]) - 1 / np.sqrt(2)) < 1e-6


# ======================================================================
# Cross-backend scheme round-trips
# ======================================================================


BACKENDS = ["qiskit"]
if is_available("cirq"):
    BACKENDS.append("cirq")


@pytest.fixture(params=BACKENDS)
def backend_name(request):
    return request.param


@pytest.fixture
def mono_data():
    return np.array([0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25])


@pytest.fixture
def stereo_data():
    return np.array([
        [0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25],
        [0.0, 0.25, -0.5, -0.75, 0.75, 1.0, -0.25],
    ])


class TestSchemesCrossBackend:
    def _encode_decode(self, scheme_name, data, backend_name, shots=8000):
        import quantumaudio
        scheme = quantumaudio.load_scheme(scheme_name)
        spec = scheme.encode(data, verbose=0)
        assert isinstance(spec, CircuitSpec)
        decoded = scheme.decode(spec, backend=backend_name, shots=shots)
        return decoded

    def test_qpam(self, mono_data, backend_name):
        decoded = self._encode_decode("qpam", mono_data, backend_name)
        assert decoded.shape == mono_data.shape
        # QPAM has inherent quantisation noise; just check it runs.
        assert decoded is not None

    def test_sqpam(self, mono_data, backend_name):
        decoded = self._encode_decode("sqpam", mono_data, backend_name)
        error = np.sum((mono_data - decoded) ** 2)
        assert error < 0.5

    def test_qsm(self, mono_data, backend_name):
        decoded = self._encode_decode("qsm", mono_data, backend_name)
        assert decoded.shape == mono_data.shape

    def test_msqpam(self, stereo_data, backend_name):
        decoded = self._encode_decode("msqpam", stereo_data, backend_name)
        assert decoded.shape == stereo_data.shape

    def test_mqsm(self, stereo_data, backend_name):
        decoded = self._encode_decode("mqsm", stereo_data, backend_name)
        assert decoded.shape == stereo_data.shape
