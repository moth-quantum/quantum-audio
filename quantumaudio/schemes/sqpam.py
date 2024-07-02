import quantumaudio.utils as utils
import qiskit
import numpy as np
from typing import Union


class SQPAM:
    """
    Single-Qubit Probability Amplitude Modulation (SQPAM).

    SQPAM class implements encoding and decoding of Digital Audio where
    the amplitude is encoded through controlled rotation gates acting
    on a single-qubit.

    """

    def __init__(self):
        """
                Initialize the SQPAM instance. The attributes of __init__ method are
        specific to this Scheme which remains fixed and independent of the Data.
        These attributes gives an overview of the Scheme.

                Attributes:

                        name:		  Holds the full name of the representation
                        qubit_depth:  Number of qubits to represent the amplitude of an audio signal.
                                                  (Note: In SQPAM, the qubit depth is 1 denoting the "Single-Qubit".)

                        n_fold:		  Term for fixed number of registers used in a representation
                        labels:		  Name of the Quantum registers (Arranged from Bottom to Top in a Qiskit Circuit)
                        positions: 	  Index position of Quantum registers (Arranged from Top to Bottom in the circuit attribute .qregs)

                        convert:	  Function that applies a mathematical conversion of input at Encoding
                        restore:	  Function that restores the conversion at Decoding

        """

        self.name = "Single-Qubit Probability Amplitude Modulation"
        self.qubit_depth = 1

        self.n_fold = 2
        self.labels = ("time", "amplitude")
        self.positions = tuple(range(self.n_fold - 1, -1, -1))

        self.convert = utils.convert_to_angles
        self.restore = utils.convert_from_angles

    # ------------------- Encoding Helpers ---------------------------

    # Data Preparation

    def calculate(
        self, data: np.ndarray, verbose: Union[int, bool] = True
    ) -> tuple[int, tuple[int, int]]:
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
        num_samples = data.shape[-1]
        num_index_qubits = utils.get_qubit_count(num_samples)

        # y-axis
        assert (
            data.ndim == 1 or data.shape[0] == 1
        ), "Multi-channel not supported in SQPAM"
        num_value_qubits = self.qubit_depth

        num_qubits = (num_index_qubits, num_value_qubits)
        if verbose:
            utils.print_num_qubits(num_qubits, labels=self.labels)
        return num_samples, num_qubits

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
        data = utils.apply_index_padding(data, num_index_qubits)
        data = data.squeeze()
        return data

    def initialize_circuit(self, num_index_qubits, num_value_qubits):
        """
            Initializes the circuit with Index and Value Registers

        Args:
            num_index_qubits: Number of qubits used to encode the sample indices.
            num_value_qubits: Number of qubits used to encode the sample values.

        Returns:
            circuit: Qiskit Circuit with the registers
        """
        index_register = qiskit.QuantumRegister(num_index_qubits, self.labels[0])
        value_register = qiskit.QuantumRegister(num_value_qubits, self.labels[1])
        circuit = qiskit.QuantumCircuit(value_register, index_register, name=self.name)
        circuit.h(index_register)
        return circuit

    @utils.with_indexing
    def value_setting(self, circuit, index, value):
        """
            Encodes the prepared, converted values to the initialised circuit.

        Args:
            circuit: Initialized Qiskit Circuit
            num_index_qubits: Number of qubits used to encode sampling.

        Returns:
            circuit: Qiskit Circuit
        """
        value_register, index_register = circuit.qregs

        # initialise sub-circuit
        sub_circuit = qiskit.QuantumCircuit(name=f"Sample {index}")
        sub_circuit.add_register(value_register)

        # rotate qubits with values
        for i in range(value_register.size):
            sub_circuit.ry(2 * value, i)

        # entangle with index qubits
        sub_circuit = sub_circuit.control(index_register.size)

        # attach sub-circuit
        circuit.append(sub_circuit, [i for i in range(circuit.num_qubits - 1, -1, -1)])

    def measure(self, circuit):
        """
        Adds classical measurements to all registers in the Quantum Circuit

        Args:
                circuit: Encoded Qiskit Circuit

        """
        if not circuit.cregs:
            utils.measure(circuit)

    # Default Encode Function

    def encode(self, data, measure=True, verbose=2):
        """
        Given an audio data, prepares a Qiskit Circuit representing it.

        Args:
                data: Array representing Digital Audio Samples
                measure: Adds measurement to the circuit if set True or int > 0
                verbose: Level of information to print.
                                 Prints number of qubits if 1 and Displays circuit if 2.

        Returns:
                A Qiskit Circuit representing the Digital Audio.

        """
        num_samples, (num_index_qubits, num_value_qubits) = self.calculate(
            data, verbose=bool(verbose)
        )
        # prepare data
        data = self.prepare_data(data, num_index_qubits)
        # convert data
        values = self.convert(data)
        # initialise circuit
        circuit = self.initialize_circuit(num_index_qubits, num_value_qubits)
        # encode values
        for i, value in enumerate(values):
            self.value_setting(circuit=circuit, index=i, value=value)
        # additional information for decoding
        circuit.metadata = {"num_samples": num_samples}
        # measure, print and return
        if measure:
            self.measure(circuit)
        if verbose == 2:
            utils.draw_circuit(circuit, decompose=1)
        return circuit

    # ------------------- Decoding Helpers ---------------------------

    def decode_components(self, counts, num_components):
        """
        The first stage of decoding is extracting required components
        from counts.

        Args:
                counts: a dictionary with the outcome of measurements
                                performed on the quantum circuit.

        Returns:
                Array of components.

        """
        # initialising components
        cosine_amps = np.zeros(num_components)
        sine_amps = np.zeros(num_components)

        # getting components from counts
        for state in counts:
            (index_bits, value_bits) = state.split()
            i = int(index_bits, 2)
            a = counts[state]
            if value_bits == "0":
                cosine_amps[i] = a
            elif value_bits == "1":
                sine_amps[i] = a

        return cosine_amps, sine_amps

    def reconstruct_data(self, counts, num_samples, inverted=False):
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
        cosine_amps, sine_amps = self.decode_components(counts, num_samples)
        data = self.restore(cosine_amps, sine_amps)
        return data

    def decode_result(self, result, inverted=False, keep_padding=False):
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
        header = result.results[0].header

        # decoding x-axis
        index_position, _ = self.positions
        num_index_qubits = header.qreg_sizes[index_position][1]
        num_samples = 2**num_index_qubits
        original_num_samples = header.metadata["num_samples"]

        # decoding y-axis
        data = self.reconstruct_data(
            counts=counts, num_samples=num_samples, inverted=False
        )

        # undo padding
        if not keep_padding:
            data = data[:original_num_samples]

        return data

    # Default Decode Function

    def decode(
        self, circuit, backend=None, shots=1024, inverted=False, keep_padding=False
    ):
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
        result = utils.execute(circuit=circuit, backend=backend, shots=shots)
        data = self.decode_result(
            result=result, inverted=inverted, keep_padding=keep_padding
        )
        return data
