import quantumaudio.utils as utils
import qiskit
import numpy as np

class QPAM:
	"""Quantum Probability Amplitude Modulation (QPAM).
			
		Class that implements QPAM ciruit preparation
		"""
	def __init__(self):
		self.name = 'Quantum Probability Amplitude Modulation'
		self.qubit_depth = 0
		
		self.n_fold = 1
		self.labels = ('time','amplitude')
		self.positions = tuple(range(self.n_fold-1,-1,-1))
		
		self.convert = utils.convert_to_probability_amplitudes

	def get_num_qubits(self, data, verbose=True):
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

		return num_samples,(num_index_qubits,num_value_qubits)

	def prepare_data(self, data, num_index_qubits):
		data = utils.apply_index_padding(data,num_index_qubits)
		data = data.squeeze()
		return data

	def initialize_circuit(self, num_index_qubits, num_value_qubits):
		# prepare circuit
		index_register  = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register  = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register)
		circuit.name = self.name
		return circuit

	def value_setting(self,circuit,values):
		circuit.initialize(values)

	def add_metadata(self,circuit,num_samples,norm_factor):
		circuit.metadata = {'num_samples':num_samples, 'norm_factor':norm_factor}

	def encode(self, data, measure = True, verbose=2):
		num_samples,(num_index_qubits,num_value_qubits) = self.get_num_qubits(data,verbose=bool(verbose))
		# prepare data
		data = self.prepare_data(data, num_index_qubits)
		# convert data
		norm,values = self.convert(data)
		# initialise circuit
		circuit = self.initialize_circuit(num_index_qubits,num_value_qubits)
		# prepare circuit
		self.value_setting(circuit=circuit,values=values)
		# additional information for decoding
		self.add_metadata(circuit=circuit,num_samples=num_samples,norm_factor=norm)
		if measure: 
			self.measure(circuit)
		if verbose == 2: 
			utils.draw_circuit(circuit)
		return circuit

	def measure(self,circuit):
		if not circuit.cregs: circuit.measure_all()

	def decode_components(self,counts):
		counts = utils.pad_counts(counts)
		return np.array(list(counts.values()))

	def reconstruct(self,counts,shots,norm):
		probabilities = self.decode_components(counts)
		data = utils.convert_from_probability_amplitudes(probabilities,norm,shots)
		return data

	def decode_result(self,result,keep_padding=False):
		counts = result.get_counts()
		shots  = result.results[0].shots
		header = result.results[0].header
		norm   = header.metadata['norm_factor']
		original_num_samples = header.metadata['num_samples']

		# reconstruct
		data = self.reconstruct(counts=counts,shots=shots,norm=norm)

		# undo padding
		if not keep_padding:
			data = data[:original_num_samples]
		
		return data

	def decode(self,circuit,backend=None,shots=4000,keep_padding=False):
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,keep_padding=keep_padding)
		return data