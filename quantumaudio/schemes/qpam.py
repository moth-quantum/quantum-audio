import quantumaudio.utils as utils
import qiskit
import numpy as np
from typing import Union

class QPAM:
	"""
	Quantum Probability Amplitude Modulation (QPAM).
	
	QPAM class implements encoding and decoding of Digital Audio as Quantum Probability Amplitudes.

	"""
	def __init__(self):
		"""
		Initialize the QPAM instance.

		name: 		 Displays the full name of the representation
		qubit_depth: Number of qubits to represent the amplitude of an audio signal
	
		n_fold:		 Fixed number of registers used in the representation
		labels:		 Name of the registers in the Qiskit Circuit (Order is from Bottom to Top)
		positions: 	 Positions of the registers in the list circuit.qregs (Order is from Top to Bottom)

		convert:	 Function that applies conversion of input at Encoding
		restore:	 Function that restores the input at Decoding
		
		"""
		self.name = 'Quantum Probability Amplitude Modulation'
		self.qubit_depth = 0
		
		self.n_fold = 1
		self.labels = ('time','amplitude')
		self.positions = tuple(range(self.n_fold-1,-1,-1))
		
		self.convert = utils.convert_to_probability_amplitudes
		self.restore = utils.convert_from_probability_amplitudes

	# ------------------- Encoding Helpers --------------------------- 

	# ----- Data Preparation -----

	def calculate(self, data: np.ndarray, verbose: Union[int,bool] = True) -> Tuple[int, Tuple[int, int]]:
		"""
		Calculates and returns the number of qubits required for encoding
		along with the original sample length required for decoding.

        Args:
            data: Array representing Digital Audio Samples
            verbose: Prints the Qubit information if True or Number greater than 0

        Returns: 
            A tuple with (original_sample_length,number_qubits_required)
        """

		# x-axis
		num_samples      = data.shape[-1]
		num_index_qubits = utils.get_qubit_count(num_samples)
		
		# y-axis
		assert data.ndim == 1 or data.shape[0] == 1, "Multi-channel not supported in QPAM"
		num_value_qubits  = self.qubit_depth

		# print
		if verbose:
			print(f'Number of qubits required: {num_index_qubits+num_value_qubits}\n')
			print(f'{num_index_qubits} for {self.labels[0]}')
			print(f'{num_value_qubits} for {self.labels[1]}\n')

		return num_samples,(num_index_qubits,num_value_qubits)

	def prepare_data(self, data, num_index_qubits):
		data = utils.apply_index_padding(data,num_index_qubits)
		data = data.squeeze()
		return data
		
	# ------ Circuit Preparation -----

	def initialize_circuit(self, num_index_qubits, num_value_qubits):
		index_register  = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register  = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register,name=self.name)
		return circuit

	def value_setting(self,circuit,values):
		circuit.initialize(values)

	def measure(self,circuit):
		if not circuit.cregs: circuit.measure_all()

	# ------------------- Default Encode Function ---------------------------

	def encode(self, data, measure = True, verbose=2):
		num_samples,(num_index_qubits,num_value_qubits) = self.get_num_qubits(data,verbose=bool(verbose))
		# prepare data
		data = self.prepare_data(data, num_index_qubits)
		# convert data
		norm,values = self.pre_process(data)
		# initialise circuit
		circuit = self.initialize_circuit(num_index_qubits,num_value_qubits)
		# encode values
		self.value_setting(circuit=circuit,values=values)
		# additional information for decoding
		circuit.metadata = {'num_samples':num_samples, 'norm_factor':norm}
		if measure: 
			self.measure(circuit)
		if verbose == 2: 
			utils.draw_circuit(circuit)
		return circuit

	# ------------------- Decoding Helpers --------------------------- 

	def decode_components(self,counts):
		counts = utils.pad_counts(counts)
		return np.array(list(counts.values()))

	def reconstruct_data(self,counts,shots,norm):
		probabilities = self.decode_components(counts)
		data = self.restore(probabilities,norm,shots)
		return data

	def decode_result(self,result,norm=None,keep_padding=False):
		counts = result.get_counts()
		shots  = result.results[0].shots
		header = result.results[0].header
		norm   = norm if norm else header.metadata['norm_factor']
		original_num_samples = header.metadata['num_samples']

		# reconstruct
		data = self.reconstruct_data(counts=counts,shots=shots,norm=norm)

		# undo padding
		if not keep_padding:
			data = data[:original_num_samples]
		
		return data

	# ------------------- Default Decode Function ------------------------- 

	def decode(self,circuit,backend=None,shots=4000,norm=None,keep_padding=False):
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,keep_padding=keep_padding)
		return data