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
from qiskit import QuantumCircuit
from qiskit.result.counts import Counts
from qiskit.result.result import Result

from quantumaudio.schemes import MQSM
from quantumaudio.utils import interleave_channels


@pytest.fixture
def mqsm():
    return MQSM(qubit_depth=3)


def test_mqsm_fixed_attributes(mqsm):
    assert mqsm.name == "Multi-channel Quantum State Modulation"
    assert mqsm.n_fold == 2
    assert mqsm.labels == ("time", "channel", "amplitude")


def test_init_attributes(mqsm):
    assert mqsm.qubit_depth == 3
    assert mqsm.positions == (2, 1, 0)


# Mono and Stereo Audios for testing
test_inputs = [
    np.array([0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25]),
    np.array(
        [
            [0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25],
            [0.0, 0.25, -0.5, -0.75, 0.75, 0.75, -0.25],
        ]
    ),
]

test_prepared_data = [
    np.array(
        [
            0.0,
            0.0,
            -0.25,
            0.0,
            0.5,
            0.0,
            0.75,
            0.0,
            -0.75,
            0.0,
            -1.0,
            0.0,
            0.25,
            0.0,
            0.0,
            0.0,
        ]
    ),
    np.array(
        [
            0.0,
            0.0,
            -0.25,
            0.25,
            0.5,
            -0.5,
            0.75,
            -0.75,
            -0.75,
            0.75,
            -1.0,
            0.75,
            0.25,
            -0.25,
            0.0,
            0.0,
        ]
    ),
]

test_num_channels = (1, 2)

test_input_channels = list(zip(test_inputs, test_num_channels))


@pytest.mark.parametrize("input_audio, num_channels", test_input_channels)
def test_calculate(mqsm, input_audio, num_channels):
    allocated_qubits = mqsm.calculate(input_audio)
    print(f"num_channels: {num_channels}")
    assert allocated_qubits == ((num_channels, 7), (3, 1, 3))


@pytest.fixture
def num_channels(request):
    return request.param


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
def num_channels_qubits():
    return 1


@pytest.fixture
def qubit_depth():
    return 3


test_inputs_prepared = list(zip(test_inputs, test_prepared_data))


@pytest.mark.parametrize("input_audio, prepared_data", test_inputs_prepared)
def test_prepare_data(
    mqsm, input_audio, num_index_qubits, num_channels_qubits, prepared_data
):
    data = mqsm.prepare_data(
        input_audio, num_index_qubits, num_channels_qubits
    )
    # print(f'input shape: {input_audio.shape}')
    # print(f'input: {input_audio}')
    # print(f'prepared data shape: {data.shape}')
    # print(f'data: {data}')


@pytest.mark.parametrize("prepared_input", test_prepared_data)
def test_convert(mqsm, prepared_input, num_index_qubits, qubit_depth):
    converted_data = mqsm.convert(prepared_input, qubit_depth)
    assert converted_data.any() != None
    assert (
        converted_data.tolist()
        == (prepared_input * float(2 ** (qubit_depth - 1))).tolist()
    )


@pytest.fixture
def converted_data(mqsm, request, qubit_depth):
    return mqsm.convert(request.param, qubit_depth)  # prepared_data


@pytest.mark.parametrize(
    "converted_data", tuple(test_prepared_data), indirect=True
)
def test_format(mqsm, converted_data):
    print(f"converted data: {converted_data}")


def test_initialize_circuit(
    mqsm, num_index_qubits, num_channels_qubits, num_value_qubits
):
    circuit = mqsm.initialize_circuit(
        num_index_qubits, num_channels_qubits, num_value_qubits
    )
    assert circuit != None
    assert type(circuit) == QuantumCircuit


@pytest.fixture
def circuit(mqsm, num_index_qubits, num_channels_qubits, num_value_qubits):
    return mqsm.initialize_circuit(
        num_index_qubits, num_channels_qubits, num_value_qubits
    )


@pytest.mark.parametrize(
    "converted_data", tuple(test_prepared_data), indirect=True
)
def test_value_setting(mqsm, circuit, converted_data):
    for i, value in enumerate(converted_data):
        mqsm.value_setting(circuit=circuit, index=i, value=value)


def test_measure(mqsm, circuit):
    mqsm.measure(circuit)


@pytest.fixture
def prepared_circuit(mqsm, circuit, request, qubit_depth):
    converted = mqsm.convert(request.param, qubit_depth)  # prepared_data
    for i, value in enumerate(converted):
        mqsm.value_setting(circuit=circuit, index=i, value=value)
    mqsm.measure(circuit)
    return circuit


@pytest.mark.parametrize(
    "prepared_circuit",
    tuple(test_prepared_data),
    indirect=["prepared_circuit"],
)
def test_circuit_registers(
    mqsm,
    prepared_circuit,
    num_index_qubits,
    num_value_qubits,
    num_channels_qubits,
):
    assert (
        prepared_circuit.num_qubits
        == num_index_qubits + num_value_qubits + num_channels_qubits
    )
    assert (
        prepared_circuit.num_clbits
        == num_index_qubits + num_value_qubits + num_channels_qubits
    )
    print(prepared_circuit.qubits)

    for i, qubit in enumerate(prepared_circuit.qubits):
        if i < num_value_qubits:
            assert prepared_circuit.find_bit(qubit).registers[0][0].name == "amplitude"
        elif i < num_channels_qubits + num_value_qubits:
            assert prepared_circuit.find_bit(qubit).registers[0][0].name == "channel"
        elif i < num_index_qubits + num_value_qubits + num_channels_qubits:
            assert prepared_circuit.find_bit(qubit).registers[0][0].name == "time"


@pytest.mark.parametrize(
    "input_audio, prepared_circuit",
    test_inputs_prepared,
    indirect=["prepared_circuit"],
)
def test_encode(mqsm, input_audio, prepared_circuit, num_samples):
    encoded_circuit = mqsm.encode(input_audio)
    assert encoded_circuit == prepared_circuit


@pytest.fixture
def encoded_circuit(mqsm, request):
    return mqsm.encode(request.param)


@pytest.mark.parametrize(
    "encoded_circuit, num_channels",
    list(zip(test_inputs, test_num_channels)),
    indirect=True,
)
def test_circuit_metadata(mqsm, encoded_circuit, num_samples, num_channels):
    print(f"encoded_circuit.metadata: {encoded_circuit.metadata}")
    assert encoded_circuit.metadata["num_samples"] == num_samples
    assert encoded_circuit.metadata["num_channels"] == num_channels


test_counts = [
    {
        "0011000": 290,
        "0111000": 311,
        "1101000": 315,
        "0000000": 306,
        "0010111": 317,
        "0100010": 313,
        "1010100": 334,
        "1110000": 278,
        "1100001": 318,
        "1111000": 314,
        "1001000": 350,
        "0001000": 330,
        "0110011": 319,
        "0101000": 315,
        "1000101": 305,
        "1011000": 285,
    },
    {
        "0000000": 241,
        "1111000": 257,
        "0010111": 249,
        "0100010": 253,
        "1101111": 236,
        "1011011": 255,
        "0011001": 253,
        "1001011": 258,
        "1010100": 266,
        "0101110": 281,
        "0110011": 252,
        "0001000": 247,
        "1110000": 222,
        "1100001": 237,
        "0111101": 265,
        "1000101": 228,
    },
]


@pytest.fixture
def counts(request):
    return Counts(request.param)


@pytest.fixture
def shots():
    return 5000


@pytest.fixture
def qubit_shape(num_index_qubits, num_channels_qubits, num_value_qubits):
    return (num_index_qubits, num_channels_qubits, num_value_qubits)


test_components = [
    [[0, -1, 2, 3, -3, -4, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0]],
    [[0, -1, 2, 3, -3, -4, 1, 0], [0, 1, -2, -3, 3, 3, -1, 0]],
]

parameters = list(zip(test_counts, test_components))


@pytest.mark.parametrize(
    "counts, exp_components", parameters, indirect=["counts"]
)
def test_decode_components(mqsm, counts, qubit_shape, exp_components):
    components = mqsm.decode_components(counts, qubit_shape)
    print(f"components: {components}")
    assert components.all() != None
    assert components.tolist() == exp_components


@pytest.mark.parametrize(
    "counts, prepared_data",
    list(zip(test_counts, test_prepared_data)),
    indirect=["counts"],
)
def test_reconstruct_data(
    mqsm, counts, qubit_shape, prepared_data
):
    data = mqsm.reconstruct_data(counts, qubit_shape)
    print(f"data: {data}")
    print(f"prepared_data: {prepared_data}")
    data = interleave_channels(data)
    assert data.all() != None
    assert np.sum((data - prepared_data) ** 2) < 0.05


def get_result(counts, shots, num_samples, num_channels, qubit_shape):
    return Result.from_dict(
        {
            "results": [
                {
                    "shots": shots,
                    "success": True,
                    "data": {"counts": counts},
                    "header": {
                        "qreg_sizes": [
                            ["amplitude", 1],
                            ["channel", 1],
                            ["time", 3],
                        ],
                        "metadata": {
                            "num_samples": num_samples,
                            "num_channels": num_channels,
                            "qubit_shape": qubit_shape,
                            "scheme": "MQSM",
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


parameters = list(zip(test_counts, test_num_channels, test_inputs))


@pytest.mark.parametrize(
    "counts, num_channels, input_audio",
    parameters,
    indirect=["counts", "num_channels"],
)
def test_decode_result(
    mqsm, counts, shots, num_samples, num_channels, qubit_shape, input_audio, qubit_depth
):
    result = get_result(counts, shots, num_samples, num_channels, qubit_shape)
    data = mqsm.decode_result(result)
    assert data.all() != None
    assert np.sum((data - input_audio) ** 2) == 0


@pytest.fixture
def decoded_data(mqsm, result):
    return mqsm.decode_result(result)


parameters = list(zip(test_counts, test_num_channels, test_inputs))


@pytest.mark.parametrize(
    "counts, num_channels, encoded_circuit", parameters, indirect=True
)
def test_decode(
    mqsm,
    encoded_circuit,
    shots,
    counts,
    num_samples,
    num_channels,
    qubit_shape,
    qubit_depth,
):
    result = get_result(counts, shots, num_samples, num_channels, qubit_shape)
    decoded_data = mqsm.decode_result(result)
    errors = []
    for i in range(10):
        data = mqsm.decode(encoded_circuit, shots=shots)
        assert data.all() != None
        errors.append(np.sum((data - decoded_data) ** 2))

    print(f"errors: {errors}")
    assert np.mean(errors) == 0
