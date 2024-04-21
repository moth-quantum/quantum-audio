import utils
import qiskit
import numpy as np
from bitstring import BitArray

class QSM:
	def __init__(self):
		self.name = 'Quantum State Modulation'

	def encode(self,array):
		time_resolution,pad_length = utils.get_time_resolution(array)
		if pad_length: array = np.pad(array,(0,pad_length))
		bit_depth = utils.get_bit_depth(array)
		array = array*(2**(bit_depth-1))

		time_register = qiskit.QuantumRegister(time_resolution,'t')
		amplitude_register = qiskit.QuantumRegister(bit_depth,'a')
		qc = qiskit.QuantumCircuit(amplitude_register,time_register)
		qc.h(time_register)
		
		for t, sample in enumerate(array):
			self.omega_t(qc, t, int(sample), time_register, amplitude_register)

		self.measure(qc)
		return qc

	def treg_index_X(self, qc, t, treg):
		t_bitstring = []
		for i, treg_qubit in enumerate(treg):
			t_bit = (t >> i) & 1
			t_bitstring.append(t_bit)
			if not t_bit:
				qc.x(treg_qubit)

	def omega_t(self, qc, t, a, treg, areg):
		self.treg_index_X(qc, t, treg)
		astr = []
		for i, areg_qubit in enumerate(areg):
			a_bit = (a >> i) & 1
			astr.append(a_bit)
			if a_bit:
				qc.mct(treg, areg_qubit)
		self.treg_index_X(qc, t,treg)

	def measure(self,qc,treg_pos = 1,areg_pos = 0):
		treg = qc.qregs[treg_pos]
		areg = qc.qregs[areg_pos]

		ctreg = qiskit.ClassicalRegister(treg.size, 'ct')
		careg = qiskit.ClassicalRegister(areg.size, 'ca')        
		qc.add_register(careg)
		qc.add_register(ctreg)

		qc.measure(treg, ctreg)
		qc.measure(areg, careg)


	def decode(self,qc,backend=None,shots=4000):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots,pad=False)
		time_resolution = [q.size for q in qc.qregs if q.name == 't'][0]
		bit_depth = [q.size for q in qc.qregs if q.name == 'a'][0]
		N = 2**time_resolution
		audio = np.zeros(N, int)

		for state in counts:
			(t_bits, a_bits) = state.split()
			t = int(t_bits, 2)
			a = BitArray(bin=a_bits).int
			audio[t] = a

		audio = audio/(2**(bit_depth-1))
		return audio




