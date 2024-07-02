import quantumaudio.utils as utils
import qiskit
import numpy as np
from bitstring import BitArray

class MQSM:
	def __init__(self,qubit_depth=None,num_channels=None):
		self.name = 'Multi-channel Quantum State Modulation'
		self.qubit_depth = qubit_depth
		self.num_channels = num_channels

		self.n_fold = 3
		self.labels = ('time','channel','amplitude')
		self.positions = tuple(range(self.n_fold-1,-1,-1))

		self.convert = utils.quantize
		self.restore = utils.de_quantize

	# ------------------- Encoding Helpers ---------------------------

	def calculate(self,data,verbose=True):
		# x-axis
		num_samples = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels = 1 if data.ndim == 1 else data.shape[0]  # data-dependent channels
		if self.num_channels: 
			num_channels = self.num_channels # override with pre-set channels
		num_channels = max(2,num_channels) 					   # apply constraint of minimum 2 channels

		num_channel_qubits = utils.get_qubit_count(num_channels)
		num_value_qubits = utils.get_bit_depth(data) if not self.qubit_depth else self.qubit_depth

		num_qubits = (num_index_qubits,num_channel_qubits,num_value_qubits)
		# print
		if verbose: 
			utils.print_num_qubits(num_qubits,labels=self.labels)
		return (num_channels, num_samples), num_qubits

	def prepare_data(self, data, num_index_qubits, num_channel_qubits):
		data = utils.apply_padding(data,(num_channel_qubits,num_index_qubits))
		data = utils.interleave_channels(data)
		return data

	def initialize_circuit(self, num_index_qubits, num_channel_qubits, num_value_qubits):
		index_register   = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		channel_register = qiskit.QuantumRegister(num_channel_qubits,self.labels[1])
		value_register   = qiskit.QuantumRegister(num_value_qubits,self.labels[2])

		circuit = qiskit.QuantumCircuit(value_register,channel_register,index_register,name=self.name)
		circuit.h(channel_register)
		circuit.h(index_register)
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

	def measure(self,circuit):
		if not circuit.cregs: 
			utils.measure(circuit)

	# ------------------- Encode Function ---------------------------

	def encode(self,data,measure=True,verbose=2):
		(num_channels, num_samples), num_qubits = self.calculate(data,verbose=verbose)
		num_index_qubits, num_channel_qubits, num_value_qubits = num_qubits

		# prepare data
		data = self.prepare_data(data,num_index_qubits,num_channel_qubits)
		values = self.convert(data,num_value_qubits)

		# prepare circuit
		circuit = self.initialize_circuit(num_index_qubits,num_channel_qubits,num_value_qubits)

		# encode information
		for i, sample in enumerate(values):
			self.value_setting(circuit=circuit, index=i, value=sample)

		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples,'num_channels':num_channels}

		# measure
		if measure: 
			self.measure(circuit)
		if verbose == 2: 
			utils.draw_circuit(circuit)
		return circuit

	# ------------------- Decoding Helpers --------------------------- 

	def decode_components(self,counts,num_channels,num_samples):
		data = np.zeros((num_channels,num_samples), int)
		for state in counts:
			(t_bits, c_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			c = int(c_bits, 2)
			a = BitArray(bin=a_bits).int
			data[c][t] = a
		return data

	def reconstruct_data(self,counts,num_channels,num_samples,bit_depth):
		data = self.decode_components(counts,num_channels,num_samples)
		data = self.restore(data,bit_depth)
		return data

	def decode_result(self,result,keep_padding=(False,False)):
		counts = result.get_counts()
		header = result.results[0].header

		index_position,channel_position,amplitude_position = self.positions

		# decoding x-axis
		num_index_qubits   = header.qreg_sizes[index_position][1]
		num_channel_qubits = header.qreg_sizes[channel_position][1]

		num_samples = 2 ** num_index_qubits
		num_channels = 2 ** num_channel_qubits

		original_num_samples = header.metadata['num_samples']*num_channels #verify this
		original_num_channels = header.metadata['num_channels']

		# decoding y-axis
		bit_depth = header.qreg_sizes[amplitude_position][-1]

		# decoding data
		data = self.reconstruct_data(counts=counts,num_channels=num_channels,num_samples=num_samples,bit_depth=bit_depth)

		# reconstruct
		data = utils.restore_channels(data,num_channels)

		if not keep_padding[0]:
			data = data[:original_num_channels]
		
		if not keep_padding[1]:
			data = data[:, :original_num_samples]
		
		return data

	def decode(self,circuit,backend=None,shots=4000,keep_padding=(False,False)):
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,keep_padding=keep_padding)
		return data