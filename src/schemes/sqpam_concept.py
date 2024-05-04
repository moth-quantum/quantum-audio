import utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self,buffer_size=None,num_channels=None):
		self.name 		 = 'Single-Qubit Probability Amplitude Modulation'
		self.qubit_depth = 1
		self.conversion  = utils.convert_to_angles
		self.dimension   = self.get_qubit_dimensions((buffer_size,num_channels)) if buffer_size and num_channels else None

	def get_qubit_dimension(self,shape):
		# x-axis
		num_samples      = shape[0]
		num_index_qubits = utils.get_qubit_count()
		
		# y-axis
		num_channels     = shape[1]
		num_value_qubits = (self.qubit_depth,)*num_channels

		return (num_index_qubits,num_value_qubits)

	def prepare_circuit(self,dimension,labels=('t','a')):
		# x-axis
		index_register  = qiskit.QuantumRegister(dimension[0],labels[0])
		
		# y-axis
		value_registers = [qiskit.QuantumRegister(channel,f'{labels[1]}{c+1}') for c,channel in enumerate(dimension[1])]
		
		# initialize circuit
		circuit = qiskit.QuantumCircuit(*value_registers,index_register)
		circuit.h(index_register)

		return circuit

	def encode(self,data):
		# use pre-set or data-dependent qubit dimension
		dimension = self.dimension if self.dimension else self.get_qubit_dimension(data.shape)

		# prepare data
		data   = utils.apply_padding(data,dimension[0])
		values = self.conversion(data)

		# prepare circuit
		circuit = prepare_circuit(dimension)

		# encode values
		for i, value in enumerate(values):        
			self.value_setting(qc=circuit, index=i, value=value)
		
		# additional information for decoding
		qc.metadata = {'num_samples':num_samples}

		return qc

	@utils.with_time_indexing
	def value_setting(self,qc,index,value):
		areg, treg = qc.qregs
		mc_ry = qiskit.QuantumCircuit()
		mc_ry.add_register(areg)
		mc_ry.ry(2*value, 0)
		mc_ry = mc_ry.control(treg.size)
		qc.append(mc_ry, [i for i in range(qc.num_qubits-1, -1, -1)])

	def decode(self, qc, backend=None, shots=1024):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots)
		N = 2 ** qc.metadata['time_resolution']
		cosine_amps = np.zeros(N)
		sine_amps = np.zeros(N)
		for state in counts:
			(t_bits, a_bit) = state.split()
			t = int(t_bits, 2)
			a = counts[state]
			if (a_bit == '0'):
				cosine_amps[t] = a
			elif (a_bit =='1'):
				sine_amps[t] = a
		return (2*(sine_amps/(cosine_amps+sine_amps))-1)[:qc.metadata['input_length']]