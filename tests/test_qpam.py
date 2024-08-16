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

from quantumaudio.schemes import QPAM
import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.result.counts import Counts
from qiskit.result.result import Result


@pytest.fixture
def qpam():
    return QPAM()

def test_qpam_fixed_attributes(qpam):
    assert qpam.name == 'Quantum Probability Amplitude Modulation'
    assert qpam.n_fold == 0
    assert qpam.labels == ("time", "amplitude")


def test_init_attributes(qpam):
    assert qpam.qubit_depth == 0
    assert qpam.positions ==(0,)



@pytest.fixture
def input_audio():
    return np.array([0., -0.25, 0.5 , 0.75,  -0.75  ,  -1.,  0.25])

@pytest.fixture
def input_audio_stereo():
    return np.array([[0., -0.25, 0.5 , 0.75,  -0.75  ,  -1.,  0.25],[0., 0.25, -0.5 , -0.75,   0.75  ,   1., -0.25]])


def test_multi_channel_error(qpam, input_audio_stereo):
    with pytest.raises(AssertionError):
        qpam.calculate(input_audio_stereo)

def test_calculate(qpam, input_audio):
    allocated_qubits = qpam.calculate(input_audio)
    assert allocated_qubits == (7, (3, 0))

@pytest.fixture
def num_samples():
    return 7

@pytest.fixture
def num_index_qubits():
    return 3

@pytest.fixture
def num_value_qubits():
    return 0

def test_prepare_data(qpam, input_audio, num_index_qubits):
    data = qpam.prepare_data(input_audio, num_index_qubits)
    assert data.tolist() == [0., -0.25, 0.5 , 0.75,  -0.75  ,  -1.,  0.25, 0.]


def test_convert(qpam, input_audio, num_index_qubits):
    data = qpam.prepare_data(input_audio, num_index_qubits)
    converted_data = qpam.convert(data)
    print(converted_data)
    assert converted_data != None
    assert converted_data[1].tolist() == (((data+1)/2)/np.linalg.norm((data+1)/2)).tolist()

@pytest.fixture
def prepared_data(qpam, input_audio, num_index_qubits):
    return qpam.prepare_data(input_audio, num_index_qubits)

@pytest.fixture
def converted_data(qpam, input_audio, num_index_qubits):
    data = qpam.prepare_data(input_audio, num_index_qubits)
    return qpam.convert(data)

def test_initialize_circuit(qpam, num_index_qubits, num_value_qubits):
    circuit = qpam.initialize_circuit(num_index_qubits, num_value_qubits)
    assert circuit != None
    assert type(circuit) == QuantumCircuit

@pytest.fixture
def circuit(qpam, num_index_qubits, num_value_qubits):
    return qpam.initialize_circuit(num_index_qubits, num_value_qubits)


def test_value_setting(qpam, circuit, converted_data):
    qpam.value_setting(circuit, converted_data[1])

def test_measure(qpam, circuit):
    qpam.measure(circuit)

@pytest.fixture
def prepared_circuit(qpam, circuit, converted_data):
    qpam.value_setting(circuit, converted_data[1])
    qpam.measure(circuit)
    return circuit

def test_circuit_registers(qpam, prepared_circuit, num_index_qubits, num_value_qubits):
    assert prepared_circuit.num_qubits == num_index_qubits + num_value_qubits
    assert prepared_circuit.num_clbits == num_index_qubits + num_value_qubits

    for i, qubit in enumerate(prepared_circuit.qubits):
        if i < num_value_qubits:
            assert qubit.register.name == 'amplitude'
        elif i < num_index_qubits + num_value_qubits:
            assert qubit.register.name == 'time'

def test_encode(qpam, input_audio, prepared_circuit, num_samples, converted_data):
    encoded_circuit = qpam.encode(input_audio)
    assert encoded_circuit == prepared_circuit

@pytest.fixture
def encoded_circuit(qpam, input_audio):
    return qpam.encode(input_audio)

def test_circuit_metadata(qpam, encoded_circuit, num_samples, converted_data):
    assert encoded_circuit.metadata['num_samples'] == num_samples
    assert encoded_circuit.metadata['norm_factor'] == converted_data[0]

@pytest.fixture
def counts():
    return Counts({'100': 5, '001': 60, '110': 174, '111': 106, '011': 313, '000': 116, '010': 226})

@pytest.fixture
def shots():
    return 1000

@pytest.fixture
def norm_factor(converted_data):
    return converted_data[0]

def test_decode_components(qpam, counts):
    components = qpam.decode_components(counts)
    assert components.all() != None
    assert components.tolist() == [116, 60, 226, 313, 5, 0, 174, 106]

def test_reconstruct_data(qpam, counts, shots, norm_factor, prepared_data):
    data = qpam.reconstruct_data(counts, shots, norm_factor)
    assert data.all() != None
    assert np.sum((data - prepared_data)**2) < 0.05


@pytest.fixture
def result(counts, shots, norm_factor, num_samples):
    return Result.from_dict({'results': [{'shots': shots, 'success': True, 'data': {'counts': counts}, 'header': {'metadata': {'num_samples': num_samples, 'norm_factor': norm_factor}}}], 'backend_name': 'qasm_simulator', 'backend_version': '0.14.2', 'qobj_id': 'b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1', 'job_id': 'b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1', 'success': True})

def test_decode_result(qpam, result, input_audio):
    data = qpam.decode_result(result)
    assert data.all() != None
    assert np.sum((data - input_audio)**2) < 0.05

@pytest.fixture
def decoded_data(qpam, result):
    return qpam.decode_result(result)

def test_decode(qpam, encoded_circuit, shots, decoded_data):
    errors = []
    for i in range(10):
        data = qpam.decode(encoded_circuit, shots=shots)
        assert data.all() != None
        errors.append(np.sum((data - decoded_data)**2))
    assert np.mean(errors) < 0.05
