import utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name 		 = 'Single-Qubit Probability Amplitude Modulation'
		self.qubit_depth = 1

	def encode(self,data):
		# x-axis
		num_samples 	 = data.shape[0]
		num_index_qubits = utils.get_qubit_count(num_samples)
		data 			 = utils.apply_padding(data,num_index_qubits)
		
		# y-axis
		num_channels 	 = data.shape[1]
		num_value_qubits = (self.qubit_depth,)*num_channels
		values = utils.convert_to_angles(data)

		# prepare circuit
		index_register  = qiskit.QuantumRegister(num_index_qubits,'t')
		value_registers = [qiskit.QuantumRegister(channel,f'a{c+1}') for c,channel in enumerate(num_value_qubits)]
		circuit 		= qiskit.QuantumCircuit(*value_registers,index_register,metadata=metadata)
		circuit.h(index_register)

		# encode values
		for i, value in enumerate(values):        
			self.value_setting(qc=circuit, index=i, value=value)
		
		# additional information for decoding
		decode_info = {'num_samples':num_samples}
		qc.metadata = decode_info

		return qc

	@utils.with_time_indexing
	def value_setting(self,qc, index, value):
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