import numpy as np
import matplotlib.pyplot as plt
import ipywidgets
import scipy
import qiskit_aer
import qiskit
from PIL import Image
from IPython.display import display, Audio, clear_output
import pyaudio

# Data processing utils

# Create synthetic data
def simulate_data(num_samples,num_channels=1,seed=42):
	np.random.seed(seed)
	data = np.random.rand(num_samples,num_channels)
	if num_channels == 1: data = data.squeeze()
	return data

def apply_padding(array,num_index_qubits):
	pad_length = (2**num_index_qubits)-array.shape[-1]
	if pad_length: 
		padding = [(0, 0) for _ in range(array.ndim)]
		padding[-1] = (0, pad_length)
		array = np.pad(array, padding, mode='constant')
	return array

def get_bit_depth(signal):
    unique_values = np.unique(signal)
    num_levels = len(unique_values)
    bit_depth = np.ceil(np.log2(num_levels))
    if not bit_depth: bit_depth = 1
    return int(bit_depth)

def is_within_range(arr, min_val, max_val):
    return np.all((arr >= min_val) & (arr <= max_val))

# Conversions

def convert_to_probability_amplitudes(array):
	array = array.squeeze().astype(float)
	array = (array + 1) / 2
	norm = np.linalg.norm(array)
	if not norm: norm = 1
	probability_amplitudes = array/norm
	return norm, probability_amplitudes

def convert_to_angles(array):
	assert is_within_range(array,min_val=-1,max_val=1), 'Data not in range'
	return np.arcsin(np.sqrt((array.astype(float)+1)/2))

# Quantum Utils

def get_qubit_count(data_length):
	num_qubits = int(np.ceil(np.log2(data_length)))
	return num_qubits

def pad_counts(counts):
	num_qubits = len(next(iter(counts)))
	all_states = [format(i, '0' + str(num_qubits) + 'b') for i in range(2**num_qubits)]
	complete_counts = {state: counts.get(state, 0) for state in all_states}
	return complete_counts

def get_counts(circuit,backend,shots,pad=False):
	if not backend: backend = qiskit_aer.AerSimulator()
	job = qiskit.execute(circuit,backend=backend,shots=shots)
	result = job.result()
	counts = pad_counts(result.get_counts()) if pad else result.get_counts()
	return counts

def apply_x_at_index(qc,i):
	t_bitstring = []
	_,treg = qc.qregs
	for treg_index, treg_qubit in enumerate(treg):
		t_bit = (i >> treg_index) & 1
		t_bitstring.append(t_bit)
		if not t_bit:
			qc.x(treg_qubit)

def with_indexing(func):
    def wrapper(*args, **kwargs):
        qc = kwargs.get('circuit')
        i = kwargs.get('index')
        apply_x_at_index(qc,i)
        func(*args, **kwargs)
        apply_x_at_index(qc,i)
    return wrapper

def channels_first(func):
    def wrapper(*args, **kwargs):
        data = kwargs.get('data')
        if not isinstance(data) == np.ndarray:
        	data = np.array(data).reshape(1,-1)
        elif data.ndim == 1: 
        	data = data.reshape(1,-1)
        func(*args, **kwargs)
    return wrapper

def measure(qc,treg_pos = 1,areg_pos = 0,labels=('ca','ct')):
	areg = qc.qregs[areg_pos]
	treg = qc.qregs[treg_pos]

	careg = qiskit.ClassicalRegister(areg.size, labels[0]) 
	ctreg = qiskit.ClassicalRegister(treg.size, labels[1])
	       
	qc.add_register(careg)
	qc.add_register(ctreg)
        
	qc.measure(treg, ctreg)
	qc.measure(areg, careg)

# Plotting utils

def plot(samples):
	if type(samples) != list: samples = [samples]
	
	num_samples = len(samples[0])
	x_axis = np.arange(0,num_samples)

	for i, y_axis in enumerate(samples):
		plt.plot(x_axis, y_axis, label=None) 

	plt.xlabel("Index")
	plt.ylabel("Values")
	plt.show()

def tune(obj,function,max_value=2048,step=10,name='Shots',ref=None,limit=None):
	def plot_function(shots):
		y = function(qc=obj,backend=None,shots=shots)
		x = np.arange(0,len(y))
		if isinstance(limit,int): x = x[:limit]
		plt.plot(x,y[:len(x)],label=f'Shots = {shots}')
		if isinstance(ref,np.ndarray): plt.plot(x,ref[:len(x)],label='Original')
		plt.xlabel('Shots')
		plt.ylabel('Values')
		plt.ylim(0,1.5)
		plt.legend()
		plt.grid(True)
		plt.show()
	variable_slider = ipywidgets.IntSlider(value=1, min=1, max=max_value, step=step, description=name)
	return ipywidgets.interact(plot_function, shots=variable_slider)

def interpolate(samples,step_size=0.025,kind='linear'):
    num_samples = len(samples)
    x = np.arange(0,num_samples)
    y = samples
    f = scipy.interpolate.interp1d(x,y,kind=kind)
    x_new = np.arange(0,num_samples-1,step_size)
    y_new = f(x_new)
    print(f'Interpolated number of samples from: {num_samples} to {len(y_new)}')
    return y_new/2

def play(array,rate=44100,autoplay=False):
	audio = Audio(data=array,rate=rate,autoplay=autoplay)
	display(audio)
