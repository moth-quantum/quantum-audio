import utils
import qiskit
import numpy as np

class QPAM:
	def __init__(self):
		self.name 		 = 'Quantum Probability Amplitude Modulation'
		self.qubit_depth = 0
		self.labels      = ('t','a')

	def encode(self,data):
		# x-axis
		num_samples      = data.shape[0]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels     = data.shape[1]
		num_value_qubits = self.qubit_depth*num_channels

		# prepare data
		data   = utils.apply_padding(data.squeeze(),num_index_qubits)
		norm,values = utils.convert_to_probability_amplitudes(data)

		# prepare circuit
		index_register  = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register  = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register)
		
		# encode values
		circuit.initialize(values)

		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples, 'norm_factor':norm}

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
		
		return data.reshape(-1,1)