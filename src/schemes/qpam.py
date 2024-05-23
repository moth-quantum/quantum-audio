import utils
import qiskit
import numpy as np

class QPAM:
	def __init__(self):
		self.name = 'Quantum Probability Amplitude Modulation'
		self.qubit_depth = 0
		self.labels      = ('t','a')

	def encode(self,data):
		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		assert data.ndim == 1 or data.shape[0] == 1, "Multi-channel not supported in QPAM"
		num_value_qubits  = self.qubit_depth

		# prepare data
		data = utils.apply_index_padding(data,num_index_qubits)
		norm,values = utils.convert_to_probability_amplitudes(data)

		# prepare circuit
		index_register  = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register  = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register)
		
		# encode values
		circuit.initialize(values)

		# additional information for decoding
		circuit.metadata = {'original_length':num_samples, 'norm_factor':norm}

		circuit.measure_all()
		return circuit

	def decode(self,circuit,backend=None,shots=4000):
		# execute
		counts = utils.get_counts(circuit=circuit,backend=backend,shots=shots,pad=True)

		# reconstruct
		probabilities = np.array(list(counts.values()))
		norm = circuit.metadata['norm_factor']
		data = (2*norm*np.sqrt(probabilities/shots)-1)

		# undo padding
		data = data[:circuit.metadata['original_length']]
		
		return data