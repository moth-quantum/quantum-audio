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

from quantumaudio.schemes import MQSM
from quantumaudio.utils import interleave_channels

from _helpers import counts_from_spaced


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
    assert isinstance(circuit, CircuitSpec)


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
    regs = prepared_circuit.metadata.get("registers", {})
    assert "amplitude" in regs
    assert "channel" in regs
    assert "time" in regs


@pytest.mark.parametrize(
    "input_audio, prepared_circuit",
    test_inputs_prepared,
    indirect=["prepared_circuit"],
)
def test_encode(mqsm, input_audio, prepared_circuit, num_samples):
    encoded_circuit = mqsm.encode(input_audio)
    assert isinstance(encoded_circuit, CircuitSpec)
    assert encoded_circuit.num_qubits == prepared_circuit.num_qubits


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


# Spaces separate the time, channel, and amplitude register segments
# (3+1+3) for readability; the helper strips them.
test_counts = [
    {
        "001 1 000": 290,
        "011 1 000": 311,
        "110 1 000": 315,
        "000 0 000": 306,
        "001 0 111": 317,
        "010 0 010": 313,
        "101 0 100": 334,
        "111 0 000": 278,
        "110 0 001": 318,
        "111 1 000": 314,
        "100 1 000": 350,
        "000 1 000": 330,
        "011 0 011": 319,
        "010 1 000": 315,
        "100 0 101": 305,
        "101 1 000": 285,
    },
    {
        "000 0 000": 241,
        "111 1 000": 257,
        "001 0 111": 249,
        "010 0 010": 253,
        "110 1 111": 236,
        "101 1 011": 255,
        "001 1 001": 253,
        "100 1 011": 258,
        "101 0 100": 266,
        "010 1 110": 281,
        "011 0 011": 252,
        "000 1 000": 247,
        "111 0 000": 222,
        "110 0 001": 237,
        "011 1 101": 265,
        "100 0 101": 228,
    },
]


@pytest.fixture
def counts(request):
    return counts_from_spaced(request.param)


@pytest.fixture
def shots():
    return 5000


@pytest.fixture
def qubit_shape(num_index_qubits, num_channels_qubits, qubit_depth):
    return (num_index_qubits, num_channels_qubits, qubit_depth)


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
def test_reconstruct_data(mqsm, counts, qubit_shape, prepared_data):
    data = mqsm.reconstruct_data(counts, qubit_shape)
    print(f"data: {data}")
    print(f"prepared_data: {prepared_data}")
    data = interleave_channels(data)
    assert data.all() != None
    assert np.sum((data - prepared_data) ** 2) < 0.05


def get_result(counts, shots, num_samples, num_channels):
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
                            "qubit_shape": (3, 1, 3),
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
    mqsm, counts, shots, num_samples, num_channels, input_audio
):
    result = get_result(counts, shots, num_samples, num_channels)
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
):
    result = get_result(counts, shots, num_samples, num_channels)
    decoded_data = mqsm.decode_result(result)
    errors = []
    for i in range(10):
        data = mqsm.decode(encoded_circuit, shots=shots)
        assert data.all() != None
        errors.append(np.sum((data - decoded_data) ** 2))

    print(f"errors: {errors}")
    assert np.mean(errors) == 0
