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
from qiskit.result.result import Result

from quantumaudio.backends import CircuitSpec

from quantumaudio.schemes import SQPAM

from _helpers import counts_from_spaced


@pytest.fixture
def sqpam():
    return SQPAM()


def test_sqpam_fixed_attributes(sqpam):
    assert sqpam.name == "Single-Qubit Probability Amplitude Modulation"
    assert sqpam.n_fold == 1
    assert sqpam.labels == ("time", "amplitude")


def test_init_attributes(sqpam):
    assert sqpam.qubit_depth == 1
    assert sqpam.positions == (1, 0)


@pytest.fixture
def input_audio():
    return np.array([0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25])


@pytest.fixture
def input_audio_stereo():
    return np.array(
        [
            [0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25],
            [0.0, 0.25, -0.5, -0.75, 0.75, 1.0, -0.25],
        ]
    )


def test_multi_channel_error(sqpam, input_audio_stereo):
    with pytest.raises(AssertionError):
        sqpam.calculate(input_audio_stereo)


def test_calculate(sqpam, input_audio):
    allocated_qubits = sqpam.calculate(input_audio)
    assert allocated_qubits == (7, (3, 1))


@pytest.fixture
def num_samples():
    return 7


@pytest.fixture
def num_index_qubits():
    return 3


@pytest.fixture
def num_value_qubits():
    return 1


def test_prepare_data(sqpam, input_audio, num_index_qubits):
    data = sqpam.prepare_data(input_audio, num_index_qubits)
    assert data.tolist() == [0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25, 0.0]


def test_convert(sqpam, input_audio, num_index_qubits):
    data = sqpam.prepare_data(input_audio, num_index_qubits)
    converted_data = sqpam.convert(data)
    assert converted_data.any() != None
    assert (
        converted_data.tolist() == np.arcsin(np.sqrt((data + 1) / 2)).tolist()
    )


@pytest.fixture
def prepared_data(sqpam, input_audio, num_index_qubits):
    return sqpam.prepare_data(input_audio, num_index_qubits)


@pytest.fixture
def converted_data(sqpam, input_audio, num_index_qubits):
    data = sqpam.prepare_data(input_audio, num_index_qubits)
    return sqpam.convert(data)


def test_initialize_circuit(sqpam, num_index_qubits, num_value_qubits):
    circuit = sqpam.initialize_circuit(num_index_qubits, num_value_qubits)
    assert circuit != None
    assert isinstance(circuit, CircuitSpec)


@pytest.fixture
def circuit(sqpam, num_index_qubits, num_value_qubits):
    return sqpam.initialize_circuit(num_index_qubits, num_value_qubits)


def test_value_setting(sqpam, circuit, converted_data):
    for i, value in enumerate(converted_data):
        sqpam.value_setting(circuit=circuit, index=i, value=value)


def test_measure(sqpam, circuit):
    sqpam.measure(circuit)


@pytest.fixture
def prepared_circuit(sqpam, circuit, converted_data):
    for i, value in enumerate(converted_data):
        sqpam.value_setting(circuit=circuit, index=i, value=value)
    sqpam.measure(circuit)
    return circuit


def test_circuit_registers(
    sqpam, prepared_circuit, num_index_qubits, num_value_qubits
):
    assert prepared_circuit.num_qubits == num_index_qubits + num_value_qubits
    assert prepared_circuit.num_clbits == num_index_qubits + num_value_qubits
    regs = prepared_circuit.metadata.get("registers", {})
    assert "amplitude" in regs
    assert "time" in regs


def test_encode(
    sqpam, input_audio, prepared_circuit, num_samples, converted_data
):
    encoded_circuit = sqpam.encode(input_audio)
    assert isinstance(encoded_circuit, CircuitSpec)
    assert encoded_circuit.num_qubits == prepared_circuit.num_qubits


@pytest.fixture
def encoded_circuit(sqpam, input_audio):
    return sqpam.encode(input_audio)


def test_circuit_metadata(sqpam, encoded_circuit, num_samples):
    assert encoded_circuit.metadata["num_samples"] == num_samples


@pytest.fixture
def counts():
    # Spaces separate the time and amplitude register segments (3+1) for
    # readability; the helper strips them.
    return counts_from_spaced(
        {
            "110 0": 50,
            "011 1": 114,
            "001 1": 51,
            "011 0": 8,
            "100 0": 106,
            "001 0": 76,
            "000 0": 57,
            "101 0": 114,
            "111 0": 67,
            "100 1": 13,
            "010 1": 100,
            "010 0": 44,
            "000 1": 58,
            "111 1": 60,
            "110 1": 82,
        }
    )


@pytest.fixture
def shots():
    return 1000


@pytest.fixture
def qubit_shape():
    return (3, 1)


def test_decode_components(sqpam, counts, qubit_shape):
    components = sqpam.decode_components(counts, qubit_shape)
    print(f"components: {components}")
    assert components[0].all() != None
    assert components[0].tolist() == [57, 76, 44, 8, 106, 114, 50, 67]
    assert components[1].all() != None
    assert components[1].tolist() == [58, 51, 100, 114, 13, 0, 82, 60]


def test_reconstruct_data(sqpam, counts, qubit_shape, prepared_data):
    data = sqpam.reconstruct_data(counts, qubit_shape)
    assert data.all() != None
    assert np.sum((data - prepared_data) ** 2) < 0.05


@pytest.fixture
def result(counts, shots, num_samples):
    return Result.from_dict(
        {
            "results": [
                {
                    "shots": shots,
                    "success": True,
                    "data": {"counts": counts},
                    "header": {
                        "qreg_sizes": [["amplitude", 1], ["time", 3]],
                        "metadata": {
                            "num_samples": num_samples,
                            "qubit_shape": (3, 1),
                            "scheme": "SQPAM",
                        },
                    },
                }
            ],
            "backend_name": "qasm_simulator",
            "backend_version": "0.14.2",
            "qobj_id": "b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1",
            "job_id": "b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1",
            "success": True,
        }
    )


def test_decode_result(sqpam, result, input_audio):
    data = sqpam.decode_result(result)
    assert data.all() != None
    assert np.sum((data - input_audio) ** 2) < 0.05


@pytest.fixture
def decoded_data(sqpam, result):
    return sqpam.decode_result(result)


def test_decode(sqpam, encoded_circuit, shots, decoded_data):
    errors = []
    for i in range(10):
        data = sqpam.decode(encoded_circuit, shots=shots)
        assert data.all() != None
        errors.append(np.sum((data - decoded_data) ** 2))

    print(f"errors: {errors}")
    assert np.mean(errors) < 0.1
