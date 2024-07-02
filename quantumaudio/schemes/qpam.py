import quantumaudio.utils as utils
import qiskit
import numpy as np
from typing import Union

class QPAM:
	"""
	Quantum Probability Amplitude Modulation (QPAM) Scheme.
	
	QPAM class implements encoding and decoding of Digital Audio as Quantum Probability Amplitudes.

	"""
	def __init__(self):
		"""
		Initialize the QPAM instance. The attributes of __init__ method are 
        specific to this Scheme which remains fixed and independent of the Data.
        These attributes gives an overview of how each Scheme differs 
        from one another.

		Attributes:

			name: 		 Holds the full name of the representation
			qubit_depth: Number of qubits to represent the amplitude of an audio signal.
						 (Note: In QPAM, no additional qubit is required to represent amplitude.)
		
			n_fold:		 Term for fixed number of registers used in a representation
			labels:		 Name of the Quantum registers (Arranged from Bottom to Top in a Qiskit Circuit)
			positions: 	 Index position of Quantum registers (Arranged from Top to Bottom in circuit.qregs)

			convert:	 Function that applies a mathematical conversion of input at Encoding
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

	def calculate(self, data: np.ndarray, verbose: Union[int,bool] = True) -> tuple[int, tuple[int, int]]:
		"""
		Returns necessary information required for Encoding and Decoding:
		 - Number of qubits required to encode both Time and Amplitude information.
		 - Original number of samples required for decoding.

        Args:
            data: Array representing Digital Audio Samples
            verbose: Prints the Qubit information if True or int > 0

        Returns: 
            A tuple with (original_sample_length, number_qubits_required)
            number_qubits_required is a tuple (int, int) consisting of
            num_index_qubits to encode Time Information (x-axis) and
            num_value_qubits to encode Amplitude Information (y-axis)
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

	def prepare_data(self, data: np.ndarray, num_index_qubits: int) -> np.ndarray:
		"""
		Prepares the data with appropriate dimensions for encoding:
		- It pads the length of data with zeros to fit the number of index qubits.
		- It also removes redundant dimension if the shape is (1,num_samples).

        Args:
            data: Array representing Digital Audio Samples
            num_index_qubits: Number of qubits used to encode the sample indices.

        Returns: 
            data: Array
        """
		data = utils.apply_index_padding(data,num_index_qubits)
		data = data.squeeze()
		return data
		
	# ------ Circuit Preparation -----

	def initialize_circuit(self, num_index_qubits: int, num_value_qubits: int) -> qiskit.QuantumCircuit:
		"""
		Initializes the circuit with Index and Value Registers

        Args:
            num_index_qubits: Number of qubits used to encode the sample indices.
            num_value_qubits: Number of qubits used to encode the sample values.

        Returns: 
            circuit: Qiskit Circuit with the registers
        """
		index_register  = qiskit.QuantumRegister(num_index_qubits,self.labels[0])
		value_register  = qiskit.QuantumRegister(num_value_qubits,self.labels[1])
		circuit = qiskit.QuantumCircuit(value_register,index_register,name=self.name)
		return circuit

	def value_setting(self, circuit: qiskit.QuantumCircuit, values: np.ndarray) -> None::
		"""
		Encodes the prepared, converted values to the initialised circuit.

        Args:
            circuit: Initialized Qiskit Circuit
            num_index_qubits: Number of qubits used to encode sampling.

        Returns: 
            circuit: Qiskit Circuit
        """
		circuit.initialize(values)

	def measure(self, circuit: qiskit.QuantumCircuit) -> None:
		"""
		Adds classical measurements to all qubits of the Quantum Circuit

		Args:
			circuit: Encoded Qiskit Circuit

		"""
		if not circuit.cregs: circuit.measure_all()

	# ------------------- Default Encode Function ---------------------------

	def encode(self, data: np.ndarray, measure: bool = True, verbose: Union[int,bool] = True) -> qiskit.QuantumCircuit:
		"""
		Given an audio data, prepares a Qiskit Circuit representing it.

		Args:
			data: Array representing Digital Audio Samples
			measure: Adds measurement to the circuit if set True or int > 0

		Returns:
			A Qiskit Circuit representing the Digital Audio.

		"""
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

	def decode_components(self, counts: Union[dict, qiskit.result.Counts]) -> np.ndarray:
		"""
		The first stage of decoding is extracting required components
		from counts.

		Args:
			counts: a dictionary with the outcome of measurements 
					performed on the quantum circuit.

		Returns:
			Array of components.

		"""
		counts = utils.pad_counts(counts)
		return np.array(list(counts.values()))

	def reconstruct_data(self, counts: Union[dict, qiskit.result.Counts], shots: int, norm: float) -> np.ndarray:
		"""
		Extract components and restore the conversion did
		in encoding stage.

		Args:
			counts: a dictionary with the outcome of measurements 
					performed on the quantum circuit.
			shots:  total number of times the quantum circuit is measured.
			norm :  the norm factor used to normalize the decoding

		Return:
			data: Array of restored values
		"""
		probabilities = self.decode_components(counts)
		data = self.restore(probabilities,norm,shots)
		return data

	def decode_result(self, result: qiskit.result.Result, norm: Optional[float] = None, keep_padding: bool = False) -> np.ndarray:
		"""
		Given a result object. Extract components and restore the conversion did
		in encoding stage.

		Args:
			counts: a dictionary with the outcome of measurements 
					performed on the quantum circuit.
			shots:  total number of times the quantum circuit is measured.
			norm :  the norm factor used to normalize the decoding

		Return:
			data: Array of restored values
		"""
		counts = result.get_counts()
		shots  = result.results[0].shots
		header = result.results[0].header
		norm   = norm if norm else header.metadata['norm_factor']
		if 'num_samples' in header.metadata:
			original_num_samples = header.metadata['num_samples']
		else:
			original_num_samples = None

		# reconstruct
		data = self.reconstruct_data(counts=counts,shots=shots,norm=norm)

		# undo padding
		if not keep_padding and original_num_samples:
			data = data[:original_num_samples]
		
		return data

	# ------------------- Default Decode Function ------------------------- 

	def decode(self, circuit: qiskit.QuantumCircuit:, backend: str = None, shots: int, norm: Optional[float] = None, keep_padding: bool = False) -> np.ndarray:
		"""
		Given a qiskit circuit, decodes and returns back the Original Audio.
		Args:
			circuit: A Qiskit Circuit representing the Digital Audio.
			backend: A backend string compatible with qiskit.execute method
			shots  : Total number of times the quantum circuit is measured.
			norm   : The norm factor used to normalize the decoding
			keep_padding: Undos the padding set at Encoding stage if set False.
		Return:
			data: Array of decoded values
		"""
		self.measure(circuit)
		result = utils.execute(circuit=circuit,backend=backend,shots=shots)
		data = self.decode_result(result=result,keep_padding=keep_padding)
		return data