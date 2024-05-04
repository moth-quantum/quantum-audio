import utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name = 'Single-Qubit Probability Amplitude Modulation'

	def encode(self,array):
		# extract information
		input_length = len(array)
		num_channels = array.shape[0]

		time_resolution,pad_length = utils.get_time_resolution(array)
		if pad_length: array = np.pad(array,(0,pad_length))
		amplitudes = utils.convert_to_angles(array)
		metadata = {'input_length':input_length,'time_resolution':time_resolution}

		# prepare circuit 
		time_register      = qiskit.QuantumRegister(time_resolution,'t')
		amplitude_register = qiskit.QuantumRegister(2,'a')
		qc = qiskit.QuantumCircuit(amplitude_register,time_register,metadata=metadata)
		qc.h(time_register)
		qc.barrier(amplitude_register,time_register)

		# encode information
		for i, sample in enumerate(amplitudes):        
			self.value_setting(qc=qc, index=i, value=(sample,sample))
			qc.barrier(amplitude_register,time_register)
		
		# measure
		utils.measure(qc)
		return qc

	@utils.with_time_indexing
	def value_setting(self,qc, index, value):
		areg, treg = qc.qregs
		mc_ry = qiskit.QuantumCircuit()
		mc_ry.add_register(areg)
		for i in range(areg.size):
			mc_ry.ry(2*value[i], i)
		mc_ry = mc_ry.control(treg.size)
		qc.append(mc_ry, [i for i in range(qc.num_qubits-1, -1, -1)])

	def decode(self, qc, backend=None, shots=1024):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots)
		N = 2 ** qc.metadata['time_resolution']
		cosine_amps = np.zeros(N)
		sine_amps = np.zeros(N)
		for state in counts:
			(t_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			a = counts[state]
			channel = []
			for a_bit in a_bits:
				if (a_bit == '0'):
					cosine_amps[t] = a
				elif (a_bit =='1'):
					sine_amps[t] = a
				channel.append((2*(sine_amps/(cosine_amps+sine_amps))-1)[:qc.metadata['input_length']])
		return channel