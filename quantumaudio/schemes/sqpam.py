import quantumaudio.utils as utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name = 'Single-Qubit Probability Amplitude Modulation'
		self.qubit_depth = 1
		self.labels      = ('time','channel','amplitude')

	def encode(self,data):
		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels     = 1 if data.ndim == 1 else data.shape[0]
		num_channel_qubits = utils.get_qubit_count(num_channels)
		num_value_qubits = self.qubit_depth

		# prepare data
		data   = utils.apply_index_padding(data,num_index_qubits)
		values = utils.convert_to_angles(data)

		# prepare circuit
		index_register   = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		channel_register = qiskit.QuantumRegister(num_channel_qubits,self.labels[1])
		value_register   = qiskit.QuantumRegister(num_value_qubits,self.labels[2])

		circuit = qiskit.QuantumCircuit(value_register,channel_register,index_register)
		circuit.h(index_register)
		
		# encode values
		values = values.squeeze() if num_channels == 1 else utils.interleave_channels(values)
		for i, value in enumerate(values):        
			self.value_setting(circuit=circuit, index=i, value=value)
		
		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples}

		# measure
		utils.measure(circuit)

		return circuit

	@utils.with_indexing
	def value_setting(self,circuit,index,value):
		value_register, channel_register, index_register = circuit.qregs
		
		# initialise sub-circuit
		sub_circuit = qiskit.QuantumCircuit()
		sub_circuit.add_register(value_register)
		
		# rotate qubits with values
		for i in range(value_register.size):
			sub_circuit.ry(2*value, i)

		# entangle with index qubits
		sub_circuit = sub_circuit.control(channel_register.size + index_register.size)
		
		# attach sub-circuit
		circuit.append(sub_circuit, [i for i in range(circuit.num_qubits-1,-1,-1)])

	def decode(self,circuit,backend=None,shots=1024,inverted=False):
		# execute
		counts = utils.get_counts(circuit=circuit,backend=backend,shots=shots)
		
		# decoding x-axis
		num_channel_qubits = circuit.qregs[1].size
		num_index_qubits   = circuit.qregs[2].size

		num_samples = 2 ** num_index_qubits
		num_channels = 2 ** num_channel_qubits

		total_samples = num_samples*num_channels
		original_num_samples = circuit.metadata['num_samples']*num_channels

		# decoding y-axis
		
		# initialising components
		cosine_amps = np.zeros(total_samples)
		sine_amps   = np.zeros(total_samples)

		# getting components from counts
		for state in counts:
			(index_bits, value_bits) = state.split()
			i = int(index_bits, 2)
			a = counts[state]
			if (value_bits == '0'):
				cosine_amps[i] = a
			elif (value_bits =='1'):
				sine_amps[i] = a

		total_amps = cosine_amps+sine_amps
		amps = sine_amps if not inverted else cosine_amps
		ratio = np.divide(amps, total_amps, out=np.zeros_like(amps), where=total_amps!=0)
		data = 2 * (ratio) - 1

		data = data[:original_num_samples]
		if num_channels > 1: data = utils.restore_channels(data,num_channels)

		return data

