import quantumaudio.utils as utils
import qiskit
import numpy as np
from bitstring import BitArray

class QSM:
	def __init__(self,qubit_depth=None):
		self.name = 'Quantum State Modulation'
		self.qubit_depth = qubit_depth
		self.labels = ('t','a')

	def encode(self,data):
		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels     = 1 if data.ndim == 1 else data.shape[0]
		num_value_qubits = utils.get_bit_depth(data) if not self.qubit_depth else self.qubit_depth
		
		# prepare data
		data   = utils.apply_index_padding(data,num_index_qubits)
		values = utils.quantize(data,num_value_qubits)

		# prepare circuit
		index_register 		= qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		amplitude_register 	= qiskit.QuantumRegister(num_value_qubits,self.labels[-1])
		circuit = qiskit.QuantumCircuit(amplitude_register,index_register)
		circuit.h(index_register)

		# encode information
		values = values.squeeze()
		for i, sample in enumerate(values):
			self.value_setting(circuit=circuit, index=i, value=sample)

		# measure
		utils.measure(circuit) # Note: kept in encode for demo but will be moved independent of encode

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


	def decode(self,circuit,backend=None,shots=4000):
		# execute
		counts = utils.get_counts(circuit=circuit,backend=backend,shots=shots,pad=False)

		# decoding x-axis
		num_index_qubits = circuit.qregs[1].size
		num_samples = 2 ** num_index_qubits
		
		# decoding y-axis
		bit_depth = circuit.qregs[0].size

		# decoding data
		data = np.zeros(num_samples, int)

		for state in counts:
			(t_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			a = BitArray(bin=a_bits).int
			data[t] = a

		data = data/(2**(bit_depth-1))
		return data