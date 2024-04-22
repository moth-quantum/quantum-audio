import utils
import qiskit
import numpy as np

class QPAM:
	def __init__(self):
		self.name = 'Quantum Probability Amplitude Modulation'

	def encode(self,array):
		# extract information
		time_resolution,pad_length = utils.get_time_resolution(array)
		if pad_length: array = np.pad(array,(0,pad_length))
		norm,amplitudes = utils.convert_to_probability_amplitudes(array)
		
		# prepare circuit
		time_register = qiskit.QuantumRegister(time_resolution,'t')
		qc = qiskit.QuantumCircuit(time_register,metadata={'norm_factor':norm,'pad_length':pad_length})
		
		# encode information
		qc.initialize(amplitudes)

		# measure
		qc.measure_all()
		return qc

	def decode(self,qc,backend=None,shots=4000):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots,pad=True)
		probabilities = np.array(list(counts.values()))
		norm = qc.metadata['norm_factor']
		return (2*norm*np.sqrt(probabilities/shots)-1)


