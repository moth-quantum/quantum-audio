import quantumaudio.utils as utils
import qiskit
import numpy as np

class MSQPAM:
	def __init__(self,num_channels=None):
		self.name = 'Multi-channel Single-Qubit Probability Amplitude Modulation'
		self.qubit_depth = 1
		self.num_channels = num_channels
		
		self.n_fold = 3
		self.labels = ('time','channel','amplitude')
		self.positions = tuple(range(self.n_fold-1,-1,-1))

		self.convert = utils.convert_to_angles
		self.restore = utils.convert_from_angles

	# ------------------- Encoding Helpers ---------------------------
	
	def calculate(self,data,verbose=True):
		# x-axis
		num_samples = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels = 1 if data.ndim == 1 else data.shape[0]  # data-dependent channels
		if self.num_channels: num_channels = self.num_channels # override with pre-set channels
		num_channels = max(2,num_channels) 					   # apply constraint of minimum 2 channels
		
		num_channel_qubits = utils.get_qubit_count(num_channels)
		num_value_qubits = self.qubit_depth
		
		num_qubits = (num_index_qubits,num_channel_qubits,num_value_qubits)

		# print
		if verbose: utils.print_num_qubits(num_qubits,labels=self.labels)
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
	def value_setting(self,circuit,index,value):
		value_register, channel_register, index_register = circuit.qregs
		
		# initialise sub-circuit
		sub_circuit = qiskit.QuantumCircuit(name=f'Sample {index} (CH {index%(2**channel_register.size)})')
		sub_circuit.add_register(value_register)
		
		# rotate qubits with values
		sub_circuit.ry(2*value, 0)

		# entangle with index qubits
		sub_circuit = sub_circuit.control(channel_register.size + index_register.size)
		
		# attach sub-circuit
		circuit.append(sub_circuit, [i for i in range(circuit.num_qubits-1,-1,-1)])

	def measure(self,circuit):
		if not circuit.cregs: utils.measure(circuit)

	# ------------------- Encode Function ---------------------------

	def encode(self,data,measure=True,verbose=2):
		(num_channels,num_samples), num_qubits = self.calculate(data,verbose=verbose)
		num_index_qubits, num_channel_qubits, num_value_qubits = num_qubits

		# prepare data
		data = self.prepare_data(data,num_index_qubits,num_channel_qubits)
		values = self.convert(data)

		# prepare circuit
		circuit = self.initialize_circuit(num_index_qubits,num_channel_qubits,num_value_qubits)
		
		# encode values
		for i, value in enumerate(values):        
			self.value_setting(circuit=circuit, index=i, value=value)
		
		# additional information for decoding
		circuit.metadata = {'num_channels':num_channels,'num_samples':num_samples,}

		# measure
		if measure: self.measure(circuit)
		if verbose == 2: utils.draw_circuit(circuit,decompose=1)
		return circuit

	# ------------------- Decoding Helpers --------------------------- 

	def decode_components(self,counts,num_channels,num_samples):

		# initialising components
		cosine_amps = np.zeros((num_channels,num_samples))
		sine_amps   = np.zeros((num_channels,num_samples))

		# getting components from counts
		for state in counts:
			(index_bits, channel_bits, value_bits) = state.split()
			i = int(index_bits, 2)
			j = int(channel_bits, 2)
			a = counts[state]
			if (value_bits == '0'):
				cosine_amps[j][i] = a
			elif (value_bits =='1'):
				sine_amps[j][i] = a

		return cosine_amps,sine_amps

	def reconstruct_data(self,counts,num_channels,num_samples,inverted=False):
		cosine_amps,sine_amps = self.decode_components(counts,num_channels,num_samples)
		data = self.restore(cosine_amps,sine_amps)
		return data

	def decode_result(self,result,inverted=False,keep_padding=(False,False)):
		counts = result.get_counts()
		header = result.results[0].header

		# decoding x-axis
		index_position,channel_position,_ = self.positions
		num_index_qubits   = header.qreg_sizes[index_position][1]
		num_channel_qubits = header.qreg_sizes[channel_position][1]

		num_samples = 2 ** num_index_qubits
		num_channels = 2 ** num_channel_qubits

		original_num_samples = header.metadata['num_samples']*num_channels #verify this
		original_num_channels = header.metadata['num_channels']

		# decoding y-axis
		data = self.reconstruct_data(counts=counts,num_channels=num_channels,num_samples=num_samples,inverted=False)

		# post-processing
		if not keep_padding[0]:
			data = data[:original_num_channels]
		
		if not keep_padding[1]:
			data = data[:, :original_num_samples]

		return data

	def decode(self,circuit,backend=None,shots=1024,inverted=False,keep_padding=(False,False)):
		# execute
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,inverted=inverted,keep_padding=keep_padding)
		return data
