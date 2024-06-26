import quantumaudio.utils as utils
import qiskit
import numpy as np
from bitstring import BitArray

class QSM:
	def __init__(self,qubit_depth=None):
		self.name = 'Quantum State Modulation'
		self.qubit_depth = qubit_depth
		self.labels = ('time','amplitude')

	def encode(self,data,measure=True,verbose=2):
		# x-axis
		num_samples = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		assert data.ndim == 1 or data.shape[0] == 1, "Multi-channel not supported in QSM"
		num_value_qubits = utils.get_bit_depth(data) if not self.qubit_depth else self.qubit_depth

		# print
		if verbose:
			print(f'Number of qubits required: {num_index_qubits+num_value_qubits}\n')
			print(f'{num_index_qubits} for {self.labels[0]}')
			print(f'{num_value_qubits} for {self.labels[1]}\n')
		
		# prepare data
		data = utils.apply_index_padding(data,num_index_qubits)
		values = utils.quantize(data,num_value_qubits).squeeze()

		# prepare circuit
		index_register 		= qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		amplitude_register 	= qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(amplitude_register,index_register)
		circuit.h(index_register)

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

	def decode(self,circuit,backend=None,shots=4000,keep_padding=False):
		# execute
		counts = utils.get_counts(circuit=circuit,backend=backend,shots=shots,pad=False)

		# decoding x-axis
		num_index_qubits = circuit.qregs[1].size
		num_samples = 2 ** num_index_qubits
		original_num_samples = circuit.metadata['num_samples']
		
		# decoding y-axis
		bit_depth = circuit.qregs[0].size

		# initialising data
		data = np.zeros(num_samples, int)

		# decoding data
		for state in counts:
			(t_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			a = BitArray(bin=a_bits).int
			data[t] = a

		# reconstruct
		data = data/(2**(bit_depth-1))

		# undo padding
		if not keep_padding: 
			data = data[:original_num_samples]
		return data