from quantumaudio import utils
import qiskit
import numpy as np
from bitstring import BitArray
from typing import Union, Optional


class MQSM:
    """
    Multi-channel Quantum State Modulation (MQSM).

    MQSM class implements an encoding and decoding scheme where the
    amplitude of a Digital signal is encoded as qubit states. 
    These states are controlled by qubits of register that represent the 
    corresponding time index information. Additionally another register
    is used to represent the channel information.  
    """
    def __init__(self, qubit_depth=None, num_channels=None):
        """
        Initialize the MQSM instance. The attributes of `__init__` method are
        specific to this Scheme which remains fixed and independent of the
        Data. These attributes gives an overview of the Scheme.

        Attributes:
            name:         Holds the full name of the representation.
            qubit_depth:  Number of qubits to represent the amplitude of 
                          an audio signal.
                          (Note: In QSM, this is a variable
                          that depends on the bit depth of audio)
            num_channels: Number of channels in a 2-dimensional data.
                          For e.g. (2,8) denotes stereo audio of length 8.
                          (Note: MQSM works with at-least 2 channels.)

            n_fold:       Term for fixed number of registers used.
            labels:       Name of the Quantum registers
            positions:    Index position of Quantum registers
                          (In Qiskit circuit the registers are arranged 
                          from Top to Bottom)

            convert:      Function that applies a mathematical conversion 
                          of input at Encoding.
            restore:      Function that restores the conversion at Decoding.

        Args:
            qubit_depth:  If None, the qubit_depth is adapted to the data.
                          However, the user can specify `qubit_depth` to 
                          override it. This is useful in case of 
                          real hardware limitations.
            
            num_channels: If None, the num_channels is adapted to the data.
                          However, an user can specify `num_channel` to 
                          override it. In any case, Minimum 2 channels 
                          is ensured by padding if required.

        """
        self.name = "Multi-channel Quantum State Modulation"
        self.qubit_depth = qubit_depth
        self.num_channels = num_channels

        self.n_fold = 3
        self.labels = ("time", "channel", "amplitude")
        self.positions = tuple(range(self.n_fold - 1, -1, -1))

        self.convert = utils.quantize
        self.restore = utils.de_quantize

    # ------------------- Encoding Helpers ---------------------------

    def calculate(
        self, data: np.ndarray, verbose: Union[int, bool] = True
    ) -> tuple[tuple[int, int], tuple[int, int, int]]:
        """
        Returns necessary information required for Encoding and Decoding:
         - Number of qubits required to encode Channel, Time and Amplitude information.
         - Original shape of the data required for decoding.

        Args:
            data: Array representing Digital Audio Samples.
            verbose: Prints the Qubit information if True or int > 0.

        Returns:
            A tuple of (data_shape, number_qubits)
            data_shape is a tuple (int, int) consisting of num_samples
            and updated num_channels.
            number_qubits is a tuple (int, int) consisting of:
            - num_index_qubits to encode Time Information (x-axis).
            - num_value_qubits to encode Amplitude Information (y-axis).
        """
        # x-axis
        num_samples = data.shape[-1]
        num_index_qubits = utils.get_qubit_count(num_samples)

        # y-axis
        num_channels = 1 if data.ndim == 1 else data.shape[0]  # data-dependent channels
        if self.num_channels:
            num_channels = self.num_channels  # override with pre-set channels
        num_channels = max(2, num_channels)  # apply constraint of minimum 2 channels

        data_shape = (num_channels, num_samples)

        num_channel_qubits = utils.get_qubit_count(num_channels)
        num_value_qubits = (
            utils.get_bit_depth(data) if not self.qubit_depth else self.qubit_depth
        )

        num_qubits = (num_index_qubits, num_channel_qubits, num_value_qubits)
        # print
        if verbose:
            utils.print_num_qubits(num_qubits, labels=self.labels)
        return data_shape, num_qubits

    def prepare_data(self, data: np.ndarray, num_index_qubits: int, num_channel_qubits: int) -> np.ndarray:
        """
        Prepares the data with appropriate dimensions for encoding:
        - It pads the length of data with zeros on both dimensions to fit the
          number of states that can be represented with time and channel registers.
        - It flattens the array for encoding. The default arrangement of samples is 
          made in an alternating manner using `utils.interleave_channels`.

        Args:
            data: Array representing Digital Audio Samples
            num_index_qubits: Number of qubits used to encode the sample indices.
            num_channel_qubits: Number of qubits used to encode the channels.

        Returns:
            data: Array with dimensions suitable for encoding.

        Note:
            This method should be followed by scheme.convert()
            to convert the values suitable for encoding.
        """
        data = utils.apply_padding(data, (num_channel_qubits, num_index_qubits))
        data = utils.interleave_channels(data)
        return data

    def initialize_circuit(
        self, num_index_qubits: int, num_channel_qubits: int, num_value_qubits: int
    ) -> qiskit.QuantumCircuit:
        """
        Initializes the circuit with Index, Channel and Value Registers.

        Args:
            num_index_qubits: Number of qubits used to encode the sample indices.
            num_channel_qubits: Number of qubits used to encode the channels.
            num_value_qubits: Number of qubits used to encode the sample values.

        Returns:
            circuit: Qiskit Circuit with the registers
        """
        index_register = qiskit.QuantumRegister(num_index_qubits, self.labels[0])
        channel_register = qiskit.QuantumRegister(num_channel_qubits, self.labels[1])
        value_register = qiskit.QuantumRegister(num_value_qubits, self.labels[2])

        circuit = qiskit.QuantumCircuit(
            value_register, channel_register, index_register, name=self.name
        )
        circuit.h(channel_register)
        circuit.h(index_register)
        return circuit

    @utils.with_indexing
    def value_setting(self, circuit: qiskit.QuantumCircuit, index: int, value: float) -> None:
        """
        Encodes the prepared, converted values to the initialised circuit.
        This function is used to set a single value at a single index. The
        decorator `with_indexing` applies the necessary control qubits
        corresponding to the given index.

        Args:
            circuit: Initialized Qiskit Circuit
            index: position to set the value
            value: value to be set at the index
        """
        a_bitstring = []
        value_register, channel_register, index_register = circuit.qregs
        for i, areg_qubit in enumerate(value_register):
            a_bit = (value >> i) & 1
            a_bitstring.append(a_bit)
            if a_bit:
                circuit.mct(channel_register[:]+index_register[:], areg_qubit)

    def measure(self, circuit: qiskit.QuantumCircuit) -> None:
        """
        Adds classical measurements to all registers of the Quantum Circuit
        if the circuit is not already measured.

        Args:
            circuit: Encoded Qiskit Circuit
        """
        if not circuit.cregs:
            utils.measure(circuit)

    # ----- Default Encode Function -----

    def encode(
        self, data: np.ndarray, measure: bool = True, verbose: Union[int, bool] = True
    ) -> qiskit.QuantumCircuit:
        """
        Given an audio data, prepares a Qiskit Circuit representing it.

        Args:
            data: Array representing Digital Audio Samples
            measure: Adds measurement to the circuit if set True or int > 0.
            verbose: Level of information to print.
                     - >1: Prints number of qubits required.
                     - >2: Displays the encoded circuit.
        Returns:
            A Qiskit Circuit representing the Digital Audio
        """

        (num_channels, num_samples), num_qubits = self.calculate(data, verbose=verbose)
        num_index_qubits, num_channel_qubits, num_value_qubits = num_qubits

        # prepare data
        data = self.prepare_data(data, num_index_qubits, num_channel_qubits)
        values = self.convert(data, num_value_qubits)

        # prepare circuit
        circuit = self.initialize_circuit(
            num_index_qubits, num_channel_qubits, num_value_qubits
        )

        # encode information
        for i, sample in enumerate(values):
            self.value_setting(circuit=circuit, index=i, value=sample)

        # additional information for decoding
        circuit.metadata = {"num_samples": num_samples, "num_channels": num_channels}

        # measure
        if measure:
            self.measure(circuit)
        if verbose == 2:
            utils.draw_circuit(circuit)
        return circuit

    # ------------------- Decoding Helpers ---------------------------

    def decode_components(
        self, counts: Union[dict, qiskit.result.Counts],
        num_channels: int,
        num_samples: int,
    ) -> np.ndarray:
        """
        The first stage of decoding is extracting required components from
        counts.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.
            num_channels: number of channels to get.
            num_samples: number of samples to get.

        Returns:
            2-D Array of shape (num_channels, num_samples) 
            for further decoding.
        """
        data = np.zeros((num_channels, num_samples), int)
        for state in counts:
            (t_bits, c_bits, a_bits) = state.split()
            t = int(t_bits, 2)
            c = int(c_bits, 2)
            a = BitArray(bin=a_bits).int
            data[c][t] = a
        return data

    def reconstruct_data(
        self, 
        counts: Union[dict, qiskit.result.Counts], 
        num_samples: int, 
        num_channels: int,
        qubit_depth: int,
    ) -> np.ndarray:
        """
        Given counts, Extract components and restore the conversion did at
        encoding stage.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.
            num_channels: number of channels to get.
            num_samples : number of samples to get.
            qubit_depth : number of qubits in amplitude register.

        Return:
            data: Array of restored values
        """
        data = self.decode_components(counts, num_channels, num_samples)
        data = self.restore(data, qubit_depth)
        return data

    def decode_result(
        self,
        result: qiskit.result.Result,
        keep_padding: tuple[int, int] = (False,False),
    ) -> np.ndarray:
        """
        Given a result object. Extract components and restore the conversion
        did in encoding stage.

        Args:
                result: a qiskit Result object that contains counts along
                        with metadata that was held by the original circuit.
                keep_padding: Undo the padding set at Encoding stage if set False.
                              Dimension 0: for channels
                              Dimension 1: for time

        Return:
                data: Array of restored values with original dimensions
        """
        counts = result.get_counts()
        header = result.results[0].header

        index_position, channel_position, amplitude_position = self.positions

        # decoding x-axis
        num_index_qubits = header.qreg_sizes[index_position][1]
        num_channel_qubits = header.qreg_sizes[channel_position][1]

        num_samples = 2**num_index_qubits
        num_channels = 2**num_channel_qubits

        original_num_samples = (
            header.metadata["num_samples"] * num_channels
        )  # verify this
        original_num_channels = header.metadata["num_channels"]

        # decoding y-axis
        bit_depth = header.qreg_sizes[amplitude_position][-1]

        # decoding data
        data = self.reconstruct_data(
            counts=counts,
            num_channels=num_channels,
            num_samples=num_samples,
            qubit_depth=bit_depth,
        )

        # reconstruct
        data = utils.restore_channels(data, num_channels)

        if not keep_padding[0]:
            data = data[:original_num_channels]

        if not keep_padding[1]:
            data = data[:, :original_num_samples]

        return data

    def decode(
        self,
        circuit: qiskit.QuantumCircuit,
        backend: Optional[str] = None,
        shots: int = 4000,
        keep_padding: tuple[int, int] = (False,False),
    ) -> np.ndarray:
        """
        Given a qiskit circuit, decodes and returns back the Original Audio.

        Args:
                circuit: A Qiskit Circuit representing the Digital Audio.
                backend: A backend string compatible with qiskit.execute method
                shots  : Total number of times the quantum circuit is measured.
                keep_padding: Undo the padding set at Encoding stage if set False.
        Return:
                data: Array of decoded values
        """
        self.measure(circuit)
        result = utils.execute(circuit=circuit, backend=backend, shots=shots)
        data = self.decode_result(result=result, keep_padding=keep_padding)
        return data
