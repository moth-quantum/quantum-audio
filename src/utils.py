import numpy as np
import matplotlib.pyplot as plt
import ipywidgets
import scipy
import qiskit_aer
import qiskit
from PIL import Image
from IPython.display import display, Audio, clear_output
import pyaudio
import librosa
from tqdm import tqdm

# ======================
# Data processing utils
# ======================

def simulate_data(num_samples,num_channels=1,seed=42):
	np.random.seed(seed)
	data = np.random.rand(num_samples,num_channels)
	if num_channels == 1: data = data.squeeze()
	return data

def apply_index_padding(array,num_index_qubits):
	pad_length = (2**num_index_qubits)-array.shape[-1]
	if pad_length: 
		padding = [(0, 0) for _ in range(array.ndim)]
		padding[-1] = (0, pad_length)
		array = np.pad(array, padding, mode='constant')
	return array

def apply_padding(array, num_bits):
    padding = []
    array_shape = array.shape
    for i in range(len(array_shape)):
        n_bits = num_bits[i] if len(num_bits) > i else num_bits[0]
        pad_length = (2 ** n_bits) - array_shape[i]
        if pad_length > 0:
            padding.append((0, pad_length))
        else:
            padding.append((0, 0))
    while len(padding) < array.ndim:
        padding.append((0, 0))
    array = np.pad(array, padding, mode='constant')
    return array

def get_bit_depth(signal):
    unique_values = np.unique(signal)
    num_levels = len(unique_values)
    bit_depth = get_qubit_count(num_levels)
    if not bit_depth: bit_depth = 1
    return bit_depth

def get_qubit_count(data_length):
	num_qubits = int(np.ceil(np.log2(data_length)))
	return num_qubits

def is_within_range(arr, min_val, max_val):
    return np.all((arr >= min_val) & (arr <= max_val))

def interleave_channels(array):
	return np.dstack(array).flatten()

def restore_channels(array,num_channels):
	return np.vstack([array[i::num_channels] for i in range(num_channels)])

# ======================
# Conversions
# ======================

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

def quantize(array,qubit_depth):
	values = array * (2**(qubit_depth-1))
	return values.astype(int)

# ======================
# Quantum Computing Utils
# ======================

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
	if len(qc.qregs) != 2:
		_,creg,treg = qc.qregs
	else:
		_,treg = qc.qregs
		creg = []
	bitstring = []
	for reg_index, reg_qubit in enumerate(creg[:] + treg[:]):
		bit = (i >> reg_index) & 1
		bitstring.append(bit)
		if not bit:
			qc.x(reg_qubit)

def with_indexing(func):
    def wrapper(*args, **kwargs):
        qc = kwargs.get('circuit')
        i = kwargs.get('index')
        qc.barrier()
        apply_x_at_index(qc,i)
        func(*args, **kwargs)
        apply_x_at_index(qc,i)
    return wrapper

def measure(qc,labels=('ca','cc','ct'),positions=None):
    qc.barrier()
    positions = range(len(qc.qregs)) if not positions else positions
    for pos, label in zip(positions, labels):
        qreg = qc.qregs[pos]
        creg = qiskit.ClassicalRegister(qreg.size, label)
        qc.add_register(creg)
        qc.measure(qreg, creg)

# ======================
# Plotting Utils
# ======================

def plot_1d(samples,title=None,label=('original','reconstructed')):
	if type(samples) != list: samples = [samples]
	if label and type(label) != tuple: label = (label,)
	
	num_samples = samples[0].shape[-1]
	x_axis = np.arange(0,num_samples)

	for i, y_axis in enumerate(samples):
		plt.plot(x_axis, y_axis.squeeze(), label=None if not label else label[i])

	plt.xlabel("Index")
	plt.ylabel("Values")
	if label: plt.legend()
	if title: plt.title(title)
	plt.show()

def plot(samples,title=None,label=('original','reconstructed')):
	if type(samples) != list: samples = [samples]
	if label and type(label) != tuple: label = (label,)
	
	num_samples = samples[0].shape[-1]
	num_channels = 1 if samples[0].ndim == 1 else samples[0].shape[-2]
	x_axis = np.arange(0,num_samples)
	
	if num_channels > 1:
		fig, axs = plt.subplots(num_channels, 1, figsize=(8, 8))
		for i, y_axis in enumerate(samples):
			for c in range(num_channels):
				axs[c].plot(x_axis, y_axis[c][:num_samples], label=None if not label else label[i])
				axs[c].set_xlabel("Index")
				axs[c].set_ylabel("Values")
				axs[c].set_title(f"channel {c+1}")
				if label: axs[c].legend(loc='upper right')
				axs[c].grid(True)
		plt.tight_layout()
	
	else:
		for i, y_axis in enumerate(samples):
			plt.plot(x_axis, y_axis.squeeze(), label=None if not label else label[i])
			plt.xlabel("Index")
			plt.ylabel("Values")
			if label: plt.legend()
	
	if title: plt.title(title)
	plt.show()

def tune(obj,function,max_value=2048,step=10,name='Shots',ref=None,limit=None):
	def plot_function(shots):
		y = function(circuit=obj,backend=None,shots=shots)
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
	
def tune_audio(obj,scheme,function,max_value=8000,step=10,name='Shots',limit=None,sr=22050,offset=0):
	def plot_function(shots):
		y = function(chunks=obj[offset:limit],scheme=scheme,shots=shots)
		if y: y = np.concatenate(y)
		clear_output(wait=True)
		play(y,rate=sr,autoplay=True)
	variable_slider = ipywidgets.IntSlider(value=1, min=1, max=max_value, step=step, description=name, continuous_update=False)
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

# ======================
# Audio
# ======================

def get_chunks(file_path,sr=22050,chunk_size=256,mono=True,preview=False):
    y,sr = librosa.load(file_path,sr=sr,mono=mono)
    if preview:
    	play(array=y,rate=sr)
    print(f'Shape: {y.shape}')
    if y.ndim == 1: y = y.reshape(1,-1) 
    print(f'Num samples: {y.shape[-1]}, Num channels: {y.shape[0]}, Sample rate: {sr}, Buffer size: {chunk_size}')
    y_chunks = []
    for i in range(0, y.shape[-1], chunk_size):
        chunk = y[:,i : i+chunk_size]
        y_chunks.append(chunk)
    print(f'Number of chunks: {len(y_chunks)}')
    print(f'Shape per buffer: {y_chunks[0].shape}')
    return y_chunks,sr

def process(chunk,scheme,shots):
    chunk = scheme.decode(scheme.encode(chunk),shots=shots)
    return chunk

def process_chunks(chunks,scheme,shots):
    processed_chunks = []
    for chunk in chunks:
        processed_chunk = process(chunk,scheme,shots)
        processed_chunks.append(processed_chunk)
    return processed_chunks
