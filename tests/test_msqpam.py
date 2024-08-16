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

from quantumaudio.schemes import MSQPAM
import pytest
import numpy as np
from qiskit import QuantumCircuit
from qiskit.result.counts import Counts
from qiskit.result.result import Result
from quantumaudio.utils import interleave_channels


@pytest.fixture
def msqpam():
    return MSQPAM()


def test_msqpam_fixed_attributes(msqpam):
    assert (
        msqpam.name
        == "Multi-channel Single-Qubit Probability Amplitude Modulation"
    )
    assert msqpam.n_fold == 2
    assert msqpam.labels == ("time", "channel", "amplitude")


def test_init_attributes(msqpam):
    assert msqpam.qubit_depth == 1
    assert msqpam.positions == (2, 1, 0)


# Mono and Stereo Audios for testing
test_inputs = [
    np.array([0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25]),
    np.array(
        [
            [0.0, -0.25, 0.5, 0.75, -0.75, -1.0, 0.25],
            [0.0, 0.25, -0.5, -0.75, 0.75, 1.0, -0.25],
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
            1.0,
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
def test_calculate(msqpam, input_audio, num_channels):
    allocated_qubits = msqpam.calculate(input_audio)
    print(f"num_channels: {num_channels}")
    assert allocated_qubits == ((num_channels, 7), (3, 1, 1))


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
    return 1


@pytest.fixture
def num_channels_qubits():
    return 1


test_inputs_prepared = list(zip(test_inputs, test_prepared_data))


@pytest.mark.parametrize("input_audio, prepared_data", test_inputs_prepared)
def test_prepare_data(
    msqpam, input_audio, num_index_qubits, num_channels_qubits, prepared_data
):
    data = msqpam.prepare_data(
        input_audio, num_index_qubits, num_channels_qubits
    )
    # print(f'input shape: {input_audio.shape}')
    # print(f'input: {input_audio}')
    # print(f'prepared data shape: {data.shape}')
    # print(f'data: {data}')


@pytest.mark.parametrize("prepared_input", test_prepared_data)
def test_convert(msqpam, prepared_input, num_index_qubits):
    converted_data = msqpam.convert(prepared_input)
    assert converted_data.any() != None
    assert (
        converted_data.tolist()
        == np.arcsin(np.sqrt((prepared_input + 1) / 2)).tolist()
    )


@pytest.fixture
def converted_data(msqpam, request):
    return msqpam.convert(request.param)  # prepared_data


@pytest.mark.parametrize(
    "converted_data", tuple(test_prepared_data), indirect=True
)
def test_format(msqpam, converted_data):
    print(f"converted data: {converted_data}")


def test_initialize_circuit(
    msqpam, num_index_qubits, num_channels_qubits, num_value_qubits
):
    circuit = msqpam.initialize_circuit(
        num_index_qubits, num_channels_qubits, num_value_qubits
    )
    assert circuit != None
    assert type(circuit) == QuantumCircuit


@pytest.fixture
def circuit(msqpam, num_index_qubits, num_channels_qubits, num_value_qubits):
    return msqpam.initialize_circuit(
        num_index_qubits, num_channels_qubits, num_value_qubits
    )


@pytest.mark.parametrize(
    "converted_data", tuple(test_prepared_data), indirect=True
)
def test_value_setting(msqpam, circuit, converted_data):
    for i, value in enumerate(converted_data):
        msqpam.value_setting(circuit=circuit, index=i, value=value)


def test_measure(msqpam, circuit):
    msqpam.measure(circuit)


@pytest.fixture
def prepared_circuit(msqpam, circuit, request):
    converted = msqpam.convert(request.param)  # prepared_data
    for i, value in enumerate(converted):
        msqpam.value_setting(circuit=circuit, index=i, value=value)
    msqpam.measure(circuit)
    return circuit


@pytest.mark.parametrize(
    "prepared_circuit",
    tuple(test_prepared_data),
    indirect=["prepared_circuit"],
)
def test_circuit_registers(
    msqpam,
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
            assert qubit.register.name == "amplitude"
        elif i < num_channels_qubits + num_value_qubits:
            assert qubit.register.name == "channel"
        elif i < num_index_qubits + num_value_qubits + num_channels_qubits:
            assert qubit.register.name == "time"


@pytest.mark.parametrize(
    "input_audio, prepared_circuit",
    test_inputs_prepared,
    indirect=["prepared_circuit"],
)
def test_encode(msqpam, input_audio, prepared_circuit, num_samples):
    encoded_circuit = msqpam.encode(input_audio)
    assert encoded_circuit == prepared_circuit


@pytest.fixture
def encoded_circuit(msqpam, request):
    return msqpam.encode(request.param)


@pytest.mark.parametrize(
    "encoded_circuit, num_channels",
    list(zip(test_inputs, test_num_channels)),
    indirect=True,
)
def test_circuit_metadata(msqpam, encoded_circuit, num_samples, num_channels):
    print(f"encoded_circuit.metadata: {encoded_circuit.metadata}")
    assert encoded_circuit.metadata["num_samples"] == num_samples
    assert encoded_circuit.metadata["num_channels"] == num_channels


test_counts = [
    {
        "001 0 1": 122,
        "010 0 1": 238,
        "110 1 0": 172,
        "100 0 1": 46,
        "100 0 0": 269,
        "110 1 1": 145,
        "111 1 1": 156,
        "110 0 0": 118,
        "011 1 0": 138,
        "100 1 1": 147,
        "100 1 0": 161,
        "111 0 0": 174,
        "000 0 1": 147,
        "001 1 0": 164,
        "011 0 1": 245,
        "010 1 1": 156,
        "101 1 1": 146,
        "101 0 0": 327,
        "111 0 1": 145,
        "111 1 0": 162,
        "000 1 0": 150,
        "011 1 1": 173,
        "101 1 0": 144,
        "001 1 1": 140,
        "000 1 1": 164,
        "010 1 0": 173,
        "001 0 0": 204,
        "110 0 1": 199,
        "000 0 0": 148,
        "010 0 0": 84,
        "011 0 0": 43,
    },
    {
        "110 0 0": 128,
        "100 0 0": 272,
        "111 0 0": 167,
        "100 1 0": 42,
        "001 0 0": 189,
        "011 1 0": 280,
        "001 0 1": 122,
        "110 1 0": 205,
        "010 0 1": 250,
        "100 0 1": 36,
        "100 1 1": 270,
        "001 1 1": 175,
        "000 1 1": 144,
        "010 1 1": 93,
        "101 1 1": 314,
        "101 0 0": 310,
        "110 1 1": 131,
        "111 1 1": 142,
        "111 1 0": 147,
        "111 0 1": 164,
        "011 0 1": 280,
        "000 0 0": 142,
        "110 0 1": 205,
        "011 0 0": 35,
        "010 0 0": 85,
        "000 0 1": 133,
        "001 1 0": 102,
        "010 1 0": 233,
        "000 1 0": 158,
        "011 1 1": 46,
    },
]


@pytest.fixture
def counts(request):
    return Counts(request.param)


@pytest.fixture
def shots():
    return 5000


@pytest.fixture
def num_components(num_index_qubits, num_channels_qubits):
    return (2**num_channels_qubits, 2**num_index_qubits)


test_components = [
    (
        [
            [148.0, 204.0, 84.0, 43.0, 269.0, 327.0, 118.0, 174.0],
            [150.0, 164.0, 173.0, 138.0, 161.0, 144.0, 172.0, 162.0],
        ],
        [
            [147.0, 122.0, 238.0, 245.0, 46.0, 0.0, 199.0, 145.0],
            [164.0, 140.0, 156.0, 173.0, 147.0, 146.0, 145.0, 156.0],
        ],
    ),
    (
        [
            [142.0, 189.0, 85.0, 35.0, 272.0, 310.0, 128.0, 167.0],
            [158.0, 102.0, 233.0, 280.0, 42.0, 0.0, 205.0, 147.0],
        ],
        [
            [133.0, 122.0, 250.0, 280.0, 36.0, 0.0, 205.0, 164.0],
            [144.0, 175.0, 93.0, 46.0, 270.0, 314.0, 131.0, 142.0],
        ],
    ),
]

parameters = [(a, *b) for a, b in zip(test_counts, test_components)]


@pytest.mark.parametrize(
    "counts, cos_components, sin_components", parameters, indirect=["counts"]
)
def test_decode_components(
    msqpam, counts, num_components, cos_components, sin_components
):
    components = msqpam.decode_components(counts, num_components)
    print(f"components: {components}")
    assert components[0].all() != None
    print(f"components[0]: {components[0]}")
    assert components[0].tolist() == cos_components
    assert components[1].all() != None
    assert components[1].tolist() == sin_components


@pytest.mark.parametrize(
    "counts, prepared_data",
    list(zip(test_counts, test_prepared_data)),
    indirect=["counts"],
)
def test_reconstruct_data(msqpam, counts, num_components, prepared_data):
    data = msqpam.reconstruct_data(counts, num_components)
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
    msqpam, counts, shots, num_samples, num_channels, input_audio
):
    result = get_result(counts, shots, num_samples, num_channels)
    data = msqpam.decode_result(result)
    assert data.all() != None
    assert np.sum((data - input_audio) ** 2) < 0.05


@pytest.fixture
def decoded_data(msqpam, result):
    return msqpam.decode_result(result)


parameters = list(zip(test_counts, test_num_channels, test_inputs))


@pytest.mark.parametrize(
    "counts, num_channels, encoded_circuit", parameters, indirect=True
)
def test_decode(
    msqpam, encoded_circuit, shots, counts, num_samples, num_channels
):
    result = get_result(counts, shots, num_samples, num_channels)
    decoded_data = msqpam.decode_result(result)
    errors = []
    for i in range(10):
        data = msqpam.decode(encoded_circuit, shots=shots)
        assert data.all() != None
        errors.append(np.sum((data - decoded_data) ** 2))

    print(f"errors: {errors}")
    assert np.mean(errors) < 0.1
