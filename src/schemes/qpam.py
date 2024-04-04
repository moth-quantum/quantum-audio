import utils
import qiskit
import numpy as np

class QPAM:
	def __init__(self):
		self.name = 'Quantum Probability Amplitude Modulation'

	def encode(self,array):
		norm,amplitudes = utils.convert_to_probability_amplitudes(array)
		time_register_size = int(np.log2(len(array)))
		time_register = qiskit.QuantumRegister(time_register_size,'t')
		qc = qiskit.QuantumCircuit(time_register,metadata={'norm_factor':norm})
		qc.initialize(amplitudes)
		qc.measure_all()
		return qc

	def decode(self,qc,backend=None,shots=4000):
		counts = utils.get_counts(circuit=qc,backend=backend,shots=shots)
		probabilities = np.array(list(counts.values()))
		norm = qc.metadata['norm_factor']
		return 2*norm*np.sqrt(probabilities/shots)-1


