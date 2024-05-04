import numpy as np
import matplotlib.pyplot as plt
import ipywidgets
import scipy
import qiskit_aer
import qiskit
from PIL import Image
from IPython.display import display, Audio, clear_output
import pyaudio

# Create synthetic data
def simulate_data(num_samples,num_channels=1,seed=42):
	np.random.seed(seed)
	data = np.random.rand(num_samples,num_channels)
	if num_channels == 1: data = data.squeeze()
	return data

def create_circuit(dimensions,metadata,name=('t','a')): #adapt to L and R
	index_register = qiskit.QuantumRegister(dimensions[0],name[0])
	value_registers = []
	for channel in dimensions[1]:
		value_registers.append(qiskit.QuantumRegister(channel,name[1]))
	qc = qiskit.QuantumCircuit(*value_registers,index_register,metadata=metadata)
	return qc

def convert_to_probability_amplitudes(array):
	array = (array.astype(float)+1)/2
	norm = np.linalg.norm(array)
	probability_amplitudes = array/norm
	return norm, probability_amplitudes

def convert_to_angles(array):
	return np.arcsin(np.sqrt((array.astype(float)+1)/2))

def get_qubit_count(data_length):
	num_qubits = int(np.ceil(np.log2(data_length)))
	return num_qubits

def apply_padding(array,time_resolution):
	pad_length = 2**time_resolution-len(array)
	if pad_length: array = np.pad(array,(0,pad_length))
	return array  

def get_bit_depth(signal):
    unique_values = set(signal)
    num_levels = len(unique_values)
    bit_depth = np.ceil(np.log2(num_levels))
    if not bit_depth: bit_depth = 1
    return int(bit_depth)

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

def with_time_indexing(func):
    def wrapper(*args, **kwargs):
        qc = kwargs.get('qc')
        i = kwargs.get('index')
        apply_x_at_index(qc,i)
        func(*args, **kwargs)
        apply_x_at_index(qc,i)
    return wrapper

def measure(qc,treg_pos = 1,areg_pos = 0):
	treg = qc.qregs[treg_pos]
	areg = qc.qregs[areg_pos]

	ctreg = qiskit.ClassicalRegister(treg.size, 'ct')
	careg = qiskit.ClassicalRegister(areg.size, 'ca')        
	qc.add_register(careg)
	qc.add_register(ctreg)
        
	qc.measure(treg, ctreg)
	qc.measure(areg, careg)

def plot(samples):
	if type(samples) != list: samples = [samples]
	
	num_samples = len(samples[0])
	x_axis = np.arange(0,num_samples)

	for i, y_axis in enumerate(samples):
		plt.plot(x_axis, y_axis, label=None) 

	plt.xlabel("Index")
	plt.ylabel("Values")
	#plt.legend()
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

def tune_img(obj,function,max_value=2048,step=10,name='Shots',size=25,upscale=2,limit=None):
	def plot_function(shots):
		y = function(qc=obj,backend=None,shots=shots)
		y = y[:int(size*size)]
		clear_output(wait=True)
		display(array_to_image(y,size=size,upscale=upscale))
		play(interpolate(y),autoplay=True)
	variable_slider = ipywidgets.IntSlider(value=1, min=1, max=max_value, step=step, description=name)
	return ipywidgets.interact(plot_function, shots=variable_slider)

def interpolate(samples,step_size=0.025,kind='linear'):
    num_samples = len(samples)
    x = np.arange(0,num_samples)
    y = samples
    f = scipy.interpolate.interp1d(x,y,kind=kind)
    x_new = np.arange(0,num_samples-1,step_size)
    y_new = f(x_new)
    #print(f'Interpolated number of samples from: {num_samples} to {len(y_new)}')
    return y_new/2

def image_to_array(image_path,size=100,mode='L'):
	img = Image.open(image_path).resize((size, size))
	img_gray = img.convert(mode)
	img_array = np.array(img_gray)
	img_1d = img_array.flatten()
	return img_1d

def array_to_image(array,size=100,mode='L',upscale=None):
	array = array.reshape((size, size))
	dtype = 'bool' if mode == '1' else 'uint8' 
	img = Image.fromarray(array.astype(dtype), mode)
	if upscale:
		img = img.resize((size*upscale,size*upscale), Image.LANCZOS)
	return img

def play(array,rate=44100,autoplay=False):
	audio = Audio(data=array,rate=rate,autoplay=autoplay)
	display(audio)
