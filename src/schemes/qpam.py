import utils
import numpy as np

class QPAM:
	def __init__(self):
		self.name 		 = 'Quantum Probability Amplitude Modulation'
		self.qubit_depth = 0

	def encode(self,data):
		# x-axis
		num_samples 	 = data.shape[0]
		num_index_qubits = utils.get_qubit_count(num_samples)
		data 			 = utils.apply_padding(data,num_index_qubits)
		
		# y-axis
		num_channels	 = 1
		num_value_qubits = (self.qubit_depth,)*num_channels
		norm,values 	 = utils.convert_to_probability_amplitudes(data)
		
		# decoding info
		metadata = {'num_samples':num_samples, 'norm_factor':norm}
		
		# prepare circuit
		circuit  = utils.create_circuit(dimensions=(num_index_qubits,num_value_qubits),metadata=metadata)
		
		# encode information
		circuit.initialize(values)

		return circuit

	def decode(self,circuit,backend=None,shots=4000):
		# measure 
		circuit.measure_all()

		# execute
		counts = utils.get_counts(circuit=circuit,backend=backend,shots=shots,pad=True)

		# reconstruct
		probabilities = np.array(list(counts.values()))
		norm = circuit.metadata['norm_factor']
		data = (2*norm*np.sqrt(probabilities/shots)-1)

		# undo padding
		original_length = circuit.metadata['num_samples']
		data = data[:original_length]
		
		return data