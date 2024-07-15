from quantumaudio.schemes import QPAM
import pytest
import numpy as np


@pytest.fixture
def qpam():
    return QPAM()

def test_qpam_fixed_attributes(qpam):
    assert qpam.name == 'Quantum Probability Amplitude Modulation'
    assert qpam.n_fold == 1
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

def test_initialize_circuit(qpam):
    pass

def test_value_setting(qpam):
    pass

def test_measure(qpam):
    pass

def test_circuit_metadata(qpam):
    pass

def test_decode_components(qpam):
    pass

def test_reconstruct_data(qpam):
    pass

def test_decode_result(qpam):
    pass

def test_encode(qpam):
    pass

def test_decode(qpam):
    pass



