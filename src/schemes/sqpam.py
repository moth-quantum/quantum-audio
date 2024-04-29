import utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name = 'Single-Qubit Probability Amplitude Modulation'

	def encode(self,array):
		# extract information
		input_length = len(array)
		time_resolution,pad_length = utils.get_time_resolution(array)
		if pad_length: array = np.pad(array,(0,pad_length))
		amplitudes = utils.convert_to_angles(array)
		metadata = {'input_length':input_length}

		# prepare circuit 
		time_register      = qiskit.QuantumRegister(time_resolution,'t')
		amplitude_register = qiskit.QuantumRegister(1,'a')
		qc = qiskit.QuantumCircuit(amplitude_register,time_register,metadata=metadata)
		qc.h(time_register)

		# encode information
		for t, theta in enumerate(amplitudes):        
			self.value_setting(qc=qc, t=t, a=theta, treg=time_register, areg=amplitude_register)
		
		# measure
		utils.measure(qc)
		return qc

	def value_setting(self,qc, t, a, treg, areg):
		utils.apply_x_at_index(qc,t,treg)
		mc_ry = qiskit.QuantumCircuit()
		mc_ry.add_register(areg)
		mc_ry.ry(2*a, 0)
		mc_ry = mc_ry.control(treg.size)
		qc.append(mc_ry, [i for i in range(treg.size + areg.size - 1, -1, -1)])
		utils.apply_x_at_index(qc,t,treg)

	def decode(self, qc, backend=None, shots=1024):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots)
		N = 2**qc.metadata['input_length']
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