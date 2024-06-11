import quantumaudio.utils as utils
import qiskit
import numpy as np
from bitstring import BitArray

class MQSM:
	def __init__(self,qubit_depth=None):
		self.name = 'Multi-channel Quantum State Modulation'
		self.qubit_depth = qubit_depth
		self.labels = ('time','channel','amplitude')

	def encode(self,data):
		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels     = 1 if data.ndim == 1 else data.shape[0]
		num_channel_qubits = utils.get_qubit_count(num_channels)
		num_value_qubits = utils.get_bit_depth(data) if not self.qubit_depth else self.qubit_depth
		
		# prepare data
		data = utils.apply_padding(data,(num_channel_qubits,num_index_qubits))
		data = data.squeeze() if num_channels == 1 else utils.interleave_channels(data)
		values = utils.quantize(data,num_value_qubits)

		# prepare circuit
		index_register 		= qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		channel_register = qiskit.QuantumRegister(num_channel_qubits,self.labels[1])
		amplitude_register 	= qiskit.QuantumRegister(num_value_qubits,self.labels[-1])
		
		circuit = qiskit.QuantumCircuit(amplitude_register,channel_register,index_register)
		if num_channel_qubits: circuit.h(channel_register)
		circuit.h(index_register)

		# encode information
		for i, sample in enumerate(values):
			self.value_setting(circuit=circuit, index=i, value=sample)

		#circuit.x(channel_register) #applies channel inversion
		# measure
		utils.measure(circuit)

		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples,'num_channels':num_channels}

		return circuit

	@utils.with_indexing
	def value_setting(self,circuit, index, value):
		a_bitstring = []
		areg, creg, treg = circuit.qregs
		for i, areg_qubit in enumerate(areg):
			a_bit = (value >> i) & 1
			a_bitstring.append(a_bit)
			if a_bit:
				circuit.mct(creg[:] + treg[:], areg_qubit)


	def decode(self,circuit,backend=None,shots=4000):
		# execute
		counts = utils.get_counts(circuit=circuit,backend=backend,shots=shots,pad=False)

		# decoding x-axis
		num_channel_qubits = circuit.qregs[1].size
		num_index_qubits   = circuit.qregs[2].size

		num_samples = 2 ** num_index_qubits
		num_channels = 2 ** num_channel_qubits

		original_num_samples = circuit.metadata['num_samples']*num_channels
		original_num_channels = circuit.metadata['num_channels']
		
		# decoding y-axis
		bit_depth = circuit.qregs[0].size

		# decoding data
		data = np.zeros((num_channels,num_samples), int)

		for state in counts:
			(t_bits, c_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			c = int(c_bits, 2)
			a = BitArray(bin=a_bits).int
			data[c][t] = a

		data = data/(2**(bit_depth-1))

		if num_channels > 1: 
			data = utils.restore_channels(data,num_channels)
			data = data[:original_num_channels]
		else:
			data = data.squeeze()
		
		return data