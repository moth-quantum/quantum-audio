import utils
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
		num_samples      = data.shape[0]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels = 1 #data.shape[1]
		
		if not self.qubit_depth:
			num_value_qubits = utils.get_bit_depth(data.squeeze())
		else:
			num_value_qubits = self.qubit_depth
		
		# prepare data
		data   = utils.apply_padding(data,num_index_qubits)
		values = data * (2**(num_value_qubits-1))

		# prepare circuit
		index_register 		= qiskit.QuantumRegister(num_index_qubits,'t')
		amplitude_register 	= qiskit.QuantumRegister(num_value_qubits,'a')
		circuit = qiskit.QuantumCircuit(amplitude_register,index_register)
		circuit.h(index_register)
		
		# encode information
		for i, sample in enumerate(values):
			self.value_setting(circuit=circuit, index=i, value=int(sample))

		# measure
		utils.measure(circuit)
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


	def decode(self,qc,backend=None,shots=4000):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots,pad=False)
		time_resolution = [q.size for q in qc.qregs if q.name == 't'][0]
		bit_depth = [q.size for q in qc.qregs if q.name == 'a'][0]
		N = 2**time_resolution
		data = np.zeros(N, int)

		for state in counts:
			(t_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			a = BitArray(bin=a_bits).int
			data[t] = a

		data = data/(2**(bit_depth-1))
		return data.reshape(-1,1)



