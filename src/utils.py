import numpy as np
import matplotlib.pyplot as plt
import ipywidgets
import scipy

# Create synthetic data
def simulate_data(num_samples,num_channels=1,seed=42):
	np.random.seed(seed)
	data = np.random.rand(num_samples,num_channels)
	if num_channels == 1: data = data.squeeze()
	return data

def convert_to_probability_amplitudes(array):
	array = (array+1)/2
	norm = np.linalg.norm(array)
	probability_amplitudes = array/norm
	return norm, probability_amplitudes

def pad_counts(counts):
	num_qubits = len(next(iter(counts)))
	all_states = [format(i, '0' + str(num_qubits) + 'b') for i in range(2**num_qubits)]
	complete_counts = {state: counts.get(state, 0) for state in all_states}
	return complete_counts

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

def tune(obj,function,max_value=2048,step=10,name='Shots',ref=None):
	def plot_function(shots):
		y = function(obj,shots)
		x = np.arange(0,len(y))
		plt.plot(x,y,label=f'Shots = {shots}')
		if isinstance(ref,np.ndarray): plt.plot(x,ref[:len(x)],label='Original')
		plt.xlabel('Shots')
		plt.ylabel('Values')
		plt.ylim(0,1.5)
		plt.legend()
		plt.grid(True)
		plt.show()
	variable_slider = ipywidgets.IntSlider(value=1, min=1, max=max_value, step=step, description=name)
	return ipywidgets.interact(plot_function, shots=variable_slider)

def interpolate(samples,step_size=0.01,kind='linear'):
    num_samples = len(samples)
    x = np.arange(0,num_samples)
    y = samples
    f = scipy.interpolate.interp1d(x,y,kind=kind)
    print(num_samples)
    x_new = np.arange(0,num_samples-1,step_size)
    y_new = f(x_new)
    print(f'Interpolated number of samples from: {num_samples} to {len(y_new)}')
    return y_new