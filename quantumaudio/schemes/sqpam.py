import quantumaudio.utils as utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name = 'Single-Qubit Probability Amplitude Modulation'
		self.qubit_depth = 1
		
		self.n_fold = 2
		self.labels = ('time','amplitude')
		self.positions = tuple(range(self.n_fold-1,-1,-1))

		self.convert = utils.convert_to_angles

	def encode(self,data,measure=True,verbose=2):
		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		assert data.ndim == 1 or data.shape[0] == 1, "Multi-channel not supported in SQPAM"
		num_value_qubits = self.qubit_depth

		# print
		if verbose:
			print(f'Number of qubits required: {num_index_qubits+num_value_qubits}\n')
			print(f'{num_index_qubits} for {self.labels[0]}')
			print(f'{num_value_qubits} for {self.labels[1]}\n')

		# prepare data
		data = utils.apply_index_padding(data,num_index_qubits)
		data = data.squeeze()
		values = self.convert(data)

		# prepare circuit
		index_register = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register)
		circuit.h(index_register)
		
		# encode values
		for i, value in enumerate(values):        
			self.value_setting(circuit=circuit, index=i, value=value)
		
		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples}

		# measure, print and return
		if measure: self.measure(circuit)
		if verbose == 2: utils.draw_circuit(circuit,decompose=1)
		return circuit

	@utils.with_indexing
	def value_setting(self,circuit,index,value):
		value_register, index_register = circuit.qregs
		
		# initialise sub-circuit
		sub_circuit = qiskit.QuantumCircuit(name=f'Sample {index}')
		sub_circuit.add_register(value_register)
		
		# rotate qubits with values
		for i in range(value_register.size):
			sub_circuit.ry(2*value, i)

		# entangle with index qubits
		sub_circuit = sub_circuit.control(index_register.size)
		
		# attach sub-circuit
		circuit.append(sub_circuit, [i for i in range(circuit.num_qubits-1,-1,-1)])

	def measure(self,circuit):
		if not circuit.cregs: utils.measure(circuit)

	def decode_components(self,counts,num_samples):
		# initialising components
		cosine_amps = np.zeros(num_samples)
		sine_amps   = np.zeros(num_samples)

		# getting components from counts
		for state in counts:
			(index_bits, value_bits) = state.split()
			i = int(index_bits, 2)
			a = counts[state]
			if (value_bits == '0'):
				cosine_amps[i] = a
			elif (value_bits =='1'):
				sine_amps[i] = a

		return cosine_amps,sine_amps

	def reconstruct(self,counts,num_samples,inverted=False):
		cosine_amps,sine_amps = self.decode_components(counts,num_samples)
		data = utils.convert_from_angles(cosine_amps,sine_amps)
		return data

	def decode_result(self,result,inverted=False,keep_padding=False):
		counts = result.get_counts()
		header = result.results[0].header
		original_num_samples = header.metadata['num_samples']

		# decoding x-axis
		index_position,_ = self.positions
		num_index_qubits = header.qreg_sizes[index_position][1]
		num_samples = 2 ** num_index_qubits
		
		# decoding y-axis
		data = self.reconstruct(counts=counts,num_samples=num_samples,inverted=False)

		# undo padding
		if not keep_padding: 
			data = data[:original_num_samples]

		return data

	def decode(self,circuit,backend=None,shots=1024,inverted=False,keep_padding=False):
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,inverted=inverted,keep_padding=keep_padding)
		return data