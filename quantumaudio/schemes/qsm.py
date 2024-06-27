import quantumaudio.utils as utils
import qiskit
import numpy as np
from bitstring import BitArray

class QSM:
	def __init__(self,qubit_depth=None):
		self.name = 'Quantum State Modulation'
		self.qubit_depth = qubit_depth
		
		
		self.n_fold = 2
		self.labels = ('time','amplitude')
		self.positions = tuple(range(self.n_fold-1,-1,-1))

		self.convert = utils.quantize
		self.restore = utils.de_quantize

	def get_num_qubits(self, data, verbose=True):
		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		assert data.ndim == 1 or data.shape[0] == 1, "Multi-channel not supported in QSM"
		num_value_qubits = utils.get_bit_depth(data) if not self.qubit_depth else self.qubit_depth

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
		index_register = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register,name=self.name)
		circuit.h(index_register)
		return circuit

	def encode(self,data,measure=True,verbose=2):
		num_samples,(num_index_qubits,num_value_qubits) = self.get_num_qubits(data,verbose=bool(verbose))
		# prepare data
		data = self.prepare_data(data, num_index_qubits)
		# convert data
		values = self.convert(data,num_value_qubits)
		# initialise circuit
		circuit = self.initialize_circuit(num_index_qubits,num_value_qubits)
		# encode values
		for i, sample in enumerate(values):
			self.value_setting(circuit=circuit, index=i, value=sample)

		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples}

		# measure, print and return
		if measure: self.measure(circuit)
		if verbose == 2: utils.draw_circuit(circuit)
		return circuit

	@utils.with_indexing
	def value_setting(self,circuit, index, value):
		a_bitstring = []
		areg, treg = circuit.qregs
		for i, areg_qubit in enumerate(areg):
			a_bit = (value >> i) & 1
			a_bitstring.append(a_bit)
			if a_bit:
				circuit.mct(treg, areg_qubit)

	def measure(self,circuit):
		if not circuit.cregs: utils.measure(circuit)

	def decode_components(self,counts,num_components):
		data = np.zeros(num_components, int)
		for state in counts:
			(t_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			a = BitArray(bin=a_bits).int
			data[t] = a
		return data

	def reconstruct_data(self,counts,num_samples,bit_depth):
		data = self.decode_components(counts,num_samples)
		data = self.restore(data,bit_depth)
		return data

	def decode_result(self,result,keep_padding=False):
		counts = result.get_counts()
		header = result.results[0].header

		index_position, amplitude_position = self.positions
		
		# decoding x-axis
		num_index_qubits = header.qreg_sizes[index_position][-1]
		num_samples = 2 ** num_index_qubits
		original_num_samples = header.metadata['num_samples']

		# decoding y-axis
		bit_depth = header.qreg_sizes[amplitude_position][-1]
		data = self.reconstruct_data(counts,num_samples,bit_depth)

		# undo padding
		if not keep_padding: 
			data = data[:original_num_samples]
		return data

	def decode(self,circuit,backend=None,shots=4000,keep_padding=False):
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,keep_padding=keep_padding)
		return data