import utils
import qiskit
import numpy as np
from bitstring import BitArray

class QSM:
	def __init__(self):
		self.name = 'Quantum State Modulation'

	def encode(self,array):
		# extract information
		time_resolution,pad_length = utils.get_time_resolution(array)
		if pad_length: array = np.pad(array,(0,pad_length))
		bit_depth = utils.get_bit_depth(array)
		if not bit_depth: bit_depth = 1
		amplitudes = array*(2**(bit_depth-1))
		metadata = {}

		# prepare circuit
		time_register = qiskit.QuantumRegister(time_resolution,'t')
		amplitude_register = qiskit.QuantumRegister(bit_depth,'a')
		qc = qiskit.QuantumCircuit(amplitude_register,time_register,metadata=metadata)
		qc.h(time_register)
		
		# encode information
		for t, sample in enumerate(amplitudes):
			self.value_setting(qc=qc, t=t, a=int(sample), treg=time_register, areg=amplitude_register)

		# measure
		utils.measure(qc)
		return qc

	@utils.with_time_indexing
	def value_setting(self, qc, t, a, treg, areg):
		#astr = []
		for i, areg_qubit in enumerate(areg):
			a_bit = (a >> i) & 1
			#astr.append(a_bit)
			if a_bit:
				qc.mct(treg, areg_qubit)


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




