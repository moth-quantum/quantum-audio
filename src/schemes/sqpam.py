import utils
import qiskit
import numpy as np

class SQPAM:
	def __init__(self):
		self.name = 'Single-Qubit Probability Amplitude Modulation'

	def apply_x(self,qc,t,treg):
		t_bitstring = []
		for i, treg_qubit in enumerate(treg):
			t_bit = (t >> i) & 1
			t_bitstring.append(t_bit)
			if not t_bit:
				qc.x(treg_qubit)

	def value_setting(self,qc, t, a, treg, areg):
		self.apply_x(qc, t, treg)
		mc_ry = qiskit.QuantumCircuit()
		mc_ry.add_register(areg)
		mc_ry.ry(2*a, 0)
		mc_ry = mc_ry.control(treg.size)
		qc.append(mc_ry, [i for i in range(treg.size + areg.size - 1, -1, -1)])
		self.apply_x(qc, t, treg) 

	def encode(self,array):
		time_resolution,pad_length = utils.get_time_resolution(array)
		input_length = len(array)
		if pad_length: array = np.pad(array,(0,pad_length))
		angles = utils.convert_to_angles(array)
		time_register      = qiskit.QuantumRegister(time_resolution,'t')
		amplitude_register = qiskit.QuantumRegister(1,'a')
		qc = qiskit.QuantumCircuit(amplitude_register,time_register)
		qc.h(time_register)
		for t, theta in enumerate(angles):        
			self.value_setting(qc, t, theta, time_register, amplitude_register)
		self.measure(qc)
		qc.metadata['input_length'] = input_length
		return qc

	def measure(self,qc,treg_pos = 1,areg_pos = 0):
		treg = qc.qregs[treg_pos]
		areg = qc.qregs[areg_pos]

		ctreg = qiskit.ClassicalRegister(treg.size, 'ct')
		careg = qiskit.ClassicalRegister(areg.size, 'ca')        
		qc.add_register(careg)
		qc.add_register(ctreg)
        
		qc.measure(treg, ctreg)
		qc.measure(areg, careg)

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