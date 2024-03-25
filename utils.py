import numpy as np
import matplotlib.pyplot as plt
import ipywidgets

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

# Create synthetic data
def simulate_data(num_samples,num_channels=1,seed=42):
	np.random.seed(seed)
	data = np.random.rand(num_samples,num_channels)
	if num_channels == 1: data = data.squeeze()
	return data

def tune(obj,function,max_value=2048,step=10,name='Shots',ref=None):
	def plot_function(shots):
		y = function(obj,shots)
		x = np.arange(0,len(y))
		plt.plot(x,y,label='Reconstruction')
		if isinstance(ref,np.ndarray): plt.plot(x,ref[:len(x)],label='Original')
		plt.xlabel('Shots')
		plt.ylabel('Values')
		#plt.legend()
		plt.grid(True)
		plt.show()
	variable_slider = ipywidgets.IntSlider(value=1, min=1, max=max_value, step=step, description=name)
	return ipywidgets.interact(plot_function, shots=variable_slider)