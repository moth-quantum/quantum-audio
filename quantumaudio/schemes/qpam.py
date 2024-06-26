import quantumaudio.utils as utils
import qiskit
import numpy as np

class QPAM:
	"""Quantum Probability Amplitude Modulation (QPAM).
			
		Class that implements QPAM ciruit preparation
		"""
	def __init__(self):
		self.name = 'Quantum Probability Amplitude Modulation'
		self.labels = ('time','amplitude')
		self.qubit_depth = 0

	def encode(self, data: np.ndarray, measure: bool = True, verbose: int = 2):
		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		assert data.ndim == 1 or data.shape[0] == 1, "Multi-channel not supported in QPAM"
		num_value_qubits  = self.qubit_depth

		# print
		if verbose:
			print(f'Number of qubits required: {num_index_qubits+num_value_qubits}\n')
			print(f'{num_index_qubits} for {self.labels[0]}')
			print(f'{num_value_qubits} for {self.labels[1]}\n')

		# prepare data
		data = utils.apply_index_padding(data,num_index_qubits)
		data = data.squeeze()
		norm,values = utils.convert_to_probability_amplitudes(data)

		# prepare circuit
		index_register  = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register  = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register)
		
		# encode values
		circuit.initialize(values)

		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples, 'norm_factor':norm}

		# measure, print and return
		if measure: self.measure(circuit)
		if verbose == 2: utils.draw_circuit(circuit)
		return circuit

	def measure(self,circuit):
		if not circuit.cregs: circuit.measure_all()

	def decode_result(self,result,keep_padding=False):
		counts = result.get_counts()
		shots  = result.results[0].shots
		header = result.results[0].header

		# reconstruct
		counts = utils.pad_counts(counts)
		probabilities = np.array(list(counts.values()))
		norm = header.metadata['norm_factor']
		data = (2*norm*np.sqrt(probabilities/shots)-1)

		# undo padding
		if not keep_padding:
			data = data[:header.metadata['num_samples']]
		
		return data

	def decode(self,circuit,backend=None,shots=4000,keep_padding=False):
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,keep_padding=keep_padding)
		return data