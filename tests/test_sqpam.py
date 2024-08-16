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

from quantumaudio.schemes import SQPAM
import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.result.counts import Counts
from qiskit.result.result import Result


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
    assert type(circuit) == QuantumCircuit


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
    print(prepared_circuit.qubits)

    for i, qubit in enumerate(prepared_circuit.qubits):
        if i < num_value_qubits:
            assert qubit.register.name == "amplitude"
        elif i < num_index_qubits + num_value_qubits:
            assert qubit.register.name == "time"


def test_encode(
    sqpam, input_audio, prepared_circuit, num_samples, converted_data
):
    encoded_circuit = sqpam.encode(input_audio)
    assert encoded_circuit == prepared_circuit


@pytest.fixture
def encoded_circuit(sqpam, input_audio):
    return sqpam.encode(input_audio)


def test_circuit_metadata(sqpam, encoded_circuit, num_samples):
    assert encoded_circuit.metadata["num_samples"] == num_samples


@pytest.fixture
def counts():
    return Counts(
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
    # return Counts({'0 110': 50, '1 011': 114, '1 001': 51, '0 011': 8, '0 100': 106, '0 001': 76, '0 000': 57, '0 101': 114, '0 111': 67, '1 100': 13, '1 010': 100, '0 010': 44, '1 000': 58, '1 111': 60, '1 110': 82})


@pytest.fixture
def shots():
    return 1000


@pytest.fixture
def num_components(num_index_qubits):
    return 2**num_index_qubits


def test_decode_components(sqpam, counts, num_components):
    components = sqpam.decode_components(counts, num_components)
    print(f"components: {components}")
    assert components[0].all() != None
    assert components[0].tolist() == [57, 76, 44, 8, 106, 114, 50, 67]
    assert components[1].all() != None
    assert components[1].tolist() == [58, 51, 100, 114, 13, 0, 82, 60]


def test_reconstruct_data(sqpam, counts, num_components, prepared_data):
    data = sqpam.reconstruct_data(counts, num_components)
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
                        "metadata": {"num_samples": num_samples},
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
