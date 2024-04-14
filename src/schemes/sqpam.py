import utils
import qiskit
import numpy as np

class QPAM:
	def __init__(self):
		self.name = 'Quantum Probability Amplitude Modulation'

	def encode(self,array):
		time_resolution,pad_length = utils.get_time_resolution(array)
		if pad_length: array = np.pad(array,(0,pad_length))
		return qc