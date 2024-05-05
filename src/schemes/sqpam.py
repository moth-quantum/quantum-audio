import utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name 		 = 'Single-Qubit Probability Amplitude Modulation'
		self.qubit_depth = 1
		self.labels      = ('t','a')

	def encode(self,data):
		# x-axis
		num_samples      = data.shape[0]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		num_channels     = data.shape[1]
		num_value_qubits = self.qubit_depth

		# prepare data
		data   = utils.apply_padding(data,num_index_qubits)
		values = utils.convert_to_angles(data)

		# prepare circuit
		index_register  = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register  = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register)
		circuit.h(index_register)

		# encode values
		for i, value in enumerate(values):        
			self.value_setting(circuit=circuit, index=i, value=value)
		
		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples}

		return circuit

	@utils.with_indexing
	def value_setting(self,circuit,index,value):
		value_register, index_register = circuit.qregs
		
		# initialise sub-circuit
		sub_circuit = qiskit.QuantumCircuit()
		sub_circuit.add_register(value_register)
		
		# rotate qubits with values
		for i in range(value_register.size):
			sub_circuit.ry(2*value[i], i)

		# entangle with index qubits
		sub_circuit = sub_circuit.control(index_register.size)
		
		# attach sub-circuit
		circuit.append(sub_circuit, [i for i in range(circuit.num_qubits-1,-1,-1)])

	def decode(self,circuit,backend=None,shots=1024):
		# measure
		utils.measure(circuit)

		# execute
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
			decoded_data = []
			for channel in value_bits:
				if (channel == '0'):
					cosine_amps[i] = a
				elif (channel =='1'):
					sine_amps[i] = a
				data = (2*(sine_amps/(cosine_amps+sine_amps))-1)
				decoded_data.append(data[:original_num_samples])

		return np.array(decoded_data).transpose()

