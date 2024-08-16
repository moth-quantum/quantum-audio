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

from quantumaudio.schemes import QSM
import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.result.counts import Counts
from qiskit.result.result import Result


@pytest.fixture
def qsm():
    return QSM(qubit_depth=3)

def test_qsm_fixed_attributes(qsm):
    assert qsm.name == 'Quantum State Modulation'
    assert qsm.n_fold == 1
    assert qsm.labels == ("time", "amplitude")


def test_init_attributes(qsm):
    assert qsm.qubit_depth == 3
    assert qsm.positions ==(1, 0)



@pytest.fixture
def input_audio():
    return np.array([0., -0.25, 0.5 , 0.75,  -0.75  ,  -1.,  0.25])

@pytest.fixture
def input_audio_stereo():
    return np.array([[0., -0.25, 0.5 , 0.75,  -0.75  ,  -1.,  0.25],[0., 0.25, -0.5 , -0.75,   0.75  ,   1., -0.25]])


def test_multi_channel_error(qsm, input_audio_stereo):
    with pytest.raises(AssertionError):
        qsm.calculate(input_audio_stereo)

def test_calculate(qsm, input_audio):
    allocated_qubits = qsm.calculate(input_audio)
    assert allocated_qubits == (7, (3, 3))

@pytest.fixture
def num_samples():
    return 7

@pytest.fixture
def num_index_qubits():
    return 3

@pytest.fixture
def num_value_qubits():
    return 3

@pytest.fixture
def qubit_depth():
    return 3

def test_prepare_data(qsm, input_audio, num_index_qubits):
    data = qsm.prepare_data(input_audio, num_index_qubits)
    assert data.tolist() == [0., -0.25, 0.5 , 0.75,  -0.75  ,  -1.,  0.25, 0.]


def test_convert(qsm, input_audio, num_index_qubits, qubit_depth):
    data = qsm.prepare_data(input_audio, num_index_qubits)
    converted_data = qsm.convert(data, qubit_depth)
    print(f'data: {data}')
    print(f'factor: {float(2**(qubit_depth-1))}')
    print(f'converted_data: {converted_data}')
    assert converted_data.any() != None
    assert converted_data.tolist() == [0, -1, 2, 3, -3, -4, 1, 0]
    assert converted_data.tolist() == (data*float(2**(qubit_depth-1))).tolist()

@pytest.fixture
def prepared_data(qsm, input_audio, num_index_qubits):
    return qsm.prepare_data(input_audio, num_index_qubits)

@pytest.fixture
def converted_data(qsm, input_audio, num_index_qubits, qubit_depth):
    data = qsm.prepare_data(input_audio, num_index_qubits)
    return qsm.convert(data, qubit_depth)

def test_initialize_circuit(qsm, num_index_qubits, num_value_qubits):
    circuit = qsm.initialize_circuit(num_index_qubits, num_value_qubits)
    assert circuit != None
    assert type(circuit) == QuantumCircuit

@pytest.fixture
def circuit(qsm, num_index_qubits, num_value_qubits):
    return qsm.initialize_circuit(num_index_qubits, num_value_qubits)


def test_value_setting(qsm, circuit, converted_data):
    for i, value in enumerate(converted_data):
        qsm.value_setting(circuit=circuit, index=i, value=value)

def test_measure(qsm, circuit):
    qsm.measure(circuit)

@pytest.fixture
def prepared_circuit(qsm, circuit, converted_data):
    for i, value in enumerate(converted_data):
        qsm.value_setting(circuit=circuit, index=i, value=value)
    qsm.measure(circuit)
    return circuit

def test_circuit_registers(qsm, prepared_circuit, num_index_qubits, num_value_qubits):
    assert prepared_circuit.num_qubits == num_index_qubits + num_value_qubits
    assert prepared_circuit.num_clbits == num_index_qubits + num_value_qubits 
    print(prepared_circuit.qubits)

    for i, qubit in enumerate(prepared_circuit.qubits):
        if i < num_value_qubits:
            assert qubit.register.name == 'amplitude'
        elif i < num_index_qubits + num_value_qubits:
            assert qubit.register.name == 'time'

def test_encode(qsm, input_audio, prepared_circuit, num_samples, converted_data):
    encoded_circuit = qsm.encode(input_audio)
    assert encoded_circuit == prepared_circuit

@pytest.fixture
def encoded_circuit(qsm, input_audio):
    return qsm.encode(input_audio)

def test_circuit_metadata(qsm, encoded_circuit, num_samples):
    assert encoded_circuit.metadata['num_samples'] == num_samples

@pytest.fixture
def counts():
    return Counts({'101 100': 122, '111 000': 125, '011 011': 125, '110 001': 134, '010 010': 132, '001 111': 110, '100 101': 132, '000 000': 120})

@pytest.fixture
def shots():
    return 1000

@pytest.fixture
def num_components(num_index_qubits):
    return 2**num_index_qubits
    
def test_decode_components(qsm, counts, num_components):
    components = qsm.decode_components(counts, num_components)
    print(f'components: {components}')
    assert components.all() != None
    assert components.tolist() == [0, -1, 2, 3, -3, -4, 1, 0]

def test_reconstruct_data(qsm, counts, num_components, prepared_data, qubit_depth):
    data = qsm.reconstruct_data(counts, num_components, qubit_depth)
    assert data.all() != None
    assert np.sum((data - prepared_data)**2) < 0.05


@pytest.fixture
def result(counts, shots, num_samples):
    return Result.from_dict({'results': [{'shots': shots, 'success': True, 'data': {'counts': counts}, 'header': {'qreg_sizes': [['amplitude', 3], ['time', 3]],'metadata': {'num_samples': num_samples}}}], 'backend_name': 'qasm_simulator', 'backend_version': '0.14.2', 'qobj_id': 'b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1', 'job_id': 'b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1', 'success': True})

def test_decode_result(qsm, result, input_audio):
    data = qsm.decode_result(result)
    assert data.all() != None
    assert np.sum((data - input_audio)**2) == 0

@pytest.fixture
def decoded_data(qsm, result):
    return qsm.decode_result(result)

def test_decode(qsm, encoded_circuit, shots, decoded_data):
    errors = []
    for i in range(10):
        data = qsm.decode(encoded_circuit, shots=shots)
        assert data.all() != None
        errors.append(np.sum((data - decoded_data)**2))

    print(f'errors: {errors}')
    assert np.mean(errors) == 0
