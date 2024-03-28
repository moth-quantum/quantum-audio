import utils
import qiskit
import numpy as np

class QPAM:
	def __init__(self):
		self.name = 'Quantum Probability Amplitude Modulation'
		self.norm = None

	def encode(self,array):
		self.norm,amplitudes = utils.convert_to_probability_amplitudes(array)
		time_register_size = int(np.log2(len(array)))
		time_register = qiskit.QuantumRegister(time_register_size,'t')
		qc = qiskit.QuantumCircuit(time_register)
		qc.initialize(amplitudes)
		qc.measure_all()
		return qc

	def decode(self,qc,backend,shots):
		job = qiskit.execute(qc,backend=backend,shots=shots)
		result = job.result()
		counts = utils.pad_counts(result.get_counts())
		probabilities = np.array(list(counts.values()))
		return 2*self.norm*np.sqrt(probabilities/shots)-1


