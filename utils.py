import numpy as np

# Create synthetic data
def simulate_data(num_samples,num_channels=1):
	data = np.random.rand(num_samples,num_channels)
	if num_channels == 1: data = data.squeeze()
	return data