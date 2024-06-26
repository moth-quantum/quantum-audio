import quantumaudio.utils as utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name = 'Single-Qubit Probability Amplitude Modulation'
		self.qubit_depth = 1
		self.labels = ('time','amplitude')

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
		values = utils.convert_to_angles(data)

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

	def decode(self,circuit,backend=None,shots=1024,inverted=False,keep_padding=False):
		# execute
		self.measure(circuit)
		counts = utils.get_counts(circuit=circuit,backend=backend,shots=shots)
		
		# decoding x-axis
		num_index_qubits = circuit.qregs[1].size
		num_samples = 2 ** num_index_qubits
		original_num_samples = circuit.metadata['num_samples']

		# decoding y-axis

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

		total_amps = cosine_amps+sine_amps
		amps = sine_amps if not inverted else cosine_amps
		
		# reconstruct
		ratio = np.divide(amps, total_amps, out=np.zeros_like(amps), where=total_amps!=0)
		data = 2 * (ratio) - 1

		# undo padding
		if not keep_padding: 
			data = data[:original_num_samples]

		return data