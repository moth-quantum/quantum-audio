import utils
import qiskit
import numpy as np
from bitstring import BitArray

class QSM:
	def __init__(self,qubit_depth=None):
		self.name = 'Quantum State Modulation'
		self.qubit_depth = [qubit_depth] if isinstance(qubit_depth) == int else qubit_depth
		self.labels = ('t','a')

	def encode(self,data):
		# x-axis
		num_samples      = data.shape[0]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels = data.shape[1]
		num_channel_qubits = utils.get_qubit_count(num_channels)
		
		if not self.qubit_depth:
			qubit_depth = [utils.get_bit_depth(data[:, channel]) for channel in range(num_channels)]
		else:
			qubit_depth = self.qubit_depth
		num_value_qubits = [qubit_depth]*num_channels if len(qubit_depth) == 1 else qubit_depth

		# prepare data
		data   = utils.apply_padding(data,num_index_qubits)
		values = data * (2**(num_value_qubits-1).reshape(1, -1))

		# prepare circuit
		index_register 		= qiskit.QuantumRegister(num_index_qubits,'t')
		channel_register 	= qiskit.QuantumRegister(num_channel_qubits,'c') #check in jupyter-notebook
		amplitude_register 	= qiskit.QuantumRegister(bit_depth,'a')
		qc = qiskit.QuantumCircuit(amplitude_register,channel_register,index_register)
		qc.h(index_register)
		
		# encode information
		for i, sample in enumerate(values):
			self.value_setting(qc=qc, index=i, value=int(sample))

		# measure
		utils.measure(qc)
		return qc

	@utils.with_time_indexing
	def value_setting(self,qc, index, value):
		a_bitstring = []
		areg, treg = qc.qregs
		for i, areg_qubit in enumerate(areg):
			a_bit = (value >> i) & 1
			a_bitstring.append(a_bit)
			if a_bit:
				qc.mct(treg, areg_qubit)


	def decode(self,qc,backend=None,shots=4000):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots,pad=False)
		time_resolution = [q.size for q in qc.qregs if q.name == 't'][0]
		bit_depth = [q.size for q in qc.qregs if q.name == 'a'][0]
		N = 2**time_resolution
		audio = np.zeros(N, int)

		for state in counts:
			(t_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			a = BitArray(bin=a_bits).int
			audio[t] = a

		audio = audio/(2**(bit_depth-1))
		return audio




