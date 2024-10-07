# Copyright 2024 Moth Quantum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==========================================================================

from typing import Optional, Union, Callable, Any, Tuple

import numpy as np
import qiskit

from quantumaudio import utils
from .base_scheme import Scheme


class MSQPAM(Scheme):
    """Multi-channel Single-Qubit Probability Amplitude Modulation (MSQPAM).

    MSQPAM class implements an encoding and decoding scheme where the
    amplitude of a Digital signal is encoded through rotation gates
    acting on a single-qubit. This qubit is controlled by qubits of
    time register that encodes the corresponding time index information.
    Additionally, another register is used to represent the channel information.
    """

    def __init__(self, num_channels: Optional[int] = None) -> None:
        """Initialize the MSQPAM instance. The attributes of `__init__` method are
        specific to this Scheme which remains fixed and independent of the
        Data. These attributes give an overview of the Scheme.

        Attributes:
            name:         Holds the full name of the representation.
            qubit_depth:  Number of qubits to represent the amplitude of
                          an audio signal.
                          (Note: In MSQPAM, the qubit depth
                          is 1 denoting the "Single-Qubit".)
            num_channels: Number of channels in a 2-dimensional data.
                          E.g. (2,8) denotes stereo audio of length 8.
                          (Note: MSQPAM works with at least 2 channels.)

            n_fold:       Term for a fixed number of indexed registers used in a scheme.
            labels:       Name of the Quantum registers
            positions:    Index position of Quantum registers
                          (In a Qiskit circuit the registers are arranged
                          from Top to Bottom)

            convert:      Function that applies a mathematical conversion
                          of input at Encoding.
            restore:      Function that restores the conversion at Decoding.

        Args:
            num_channels: If None, the num_channels is adapted to the data.
                          However, a user can specify `num_channels` to
                          override it. In any case, Minimum 2 channels
                          is ensured by padding if required.

        """
        self.name = (
            "Multi-channel Single-Qubit Probability Amplitude Modulation"
        )
        self.qubit_depth = 1
        self.num_channels = num_channels

        self.n_fold = 2
        self.labels = ("time", "channel", "amplitude")
        self.positions = (2, 1, 0)

        self.convert = utils.convert_to_angles
        self.restore = utils.convert_from_angles

        print(self.name)

    # ------------------- Encoding Helpers ---------------------------

    # ----- Data Preparation -----

    def calculate(
        self, data: np.ndarray, verbose: Union[int, bool] = True
    ) -> Tuple[Tuple[int, int], Tuple[int, int, int]]:
        """Returns necessary information required for Encoding and Decoding:

         - Number of qubits required to encode Channel, Time and Amplitude information.
         - Original shape of the data required for decoding.

        Args:
            data: Array representing Digital Audio Samples.
            verbose: Prints the Qubit information if True or int > 0.

        Returns:
            A Tuple of (data_shape, qubit_shape).

            `data_shape` is a Tuple (int, int) consisting of:
                - `num_samples`
                - `num_channels`
            `qubit_shape` is a Tuple (int, int, int) consisting of:
                - `num_index_qubits` to encode Time Information (x-axis).
                - `num_channel_qubits` to encode Channel Information (y-axis).
                - `num_value_qubits` to encode Amplitude Information (y-axis).
        """
        # x-axis
        num_samples = data.shape[-1]
        num_index_qubits = utils.get_qubit_count(num_samples)

        # y-axis
        num_channels = (
            1 if data.ndim == 1 else data.shape[0]
        )  # data-dependent channels
        if self.num_channels:
            num_channels = self.num_channels  # override with pre-set channels

        data_shape = (num_channels, num_samples)

        num_channel_qubits = utils.get_qubit_count(
            max(2, num_channels)
        )  # apply constraint of minimum 2 channels
        num_value_qubits = self.qubit_depth

        qubit_shape = (num_index_qubits, num_channel_qubits, num_value_qubits)
        # print
        if verbose:
            utils.print_num_qubits(qubit_shape, labels=self.labels)
        return data_shape, qubit_shape

    def prepare_data(
        self, data: np.ndarray, num_index_qubits: int, num_channel_qubits: int
    ) -> np.ndarray:
        """Prepares the data with appropriate dimensions for encoding:

         - It pads the length of data with zeros on both dimensions to fit the
           number of states that can be represented with time and channel registers.
         - It flattens the array for encoding. The default arrangement of samples is
           made in an alternating manner using `utils.interleave_channels`.

        Args:
            data: Array representing Digital Audio Samples
            num_index_qubits: Number of qubits used to encode the sample indices.
            num_channel_qubits: Number of qubits used to encode the channels.

        Returns:
            Array with dimensions suitable for encoding.

        Note:
            This method should be followed by `convert()` method
            to convert the values suitable for encoding.
        """
        data = utils.apply_padding(
            data, (num_channel_qubits, num_index_qubits)
        )
        data = utils.interleave_channels(data)
        return data

    def initialize_circuit(
        self,
        num_index_qubits: int,
        num_channel_qubits: int,
        num_value_qubits: int,
    ) -> qiskit.QuantumCircuit:
        """Initializes the circuit with Index, Channel and Value Registers.

        Args:
            num_index_qubits: Number of qubits used to encode the sample indices.
            num_channel_qubits: Number of qubits used to encode the channels.
            num_value_qubits: Number of qubits used to encode the sample values.

        Returns:
            Qiskit Circuit with the registers
        """
        index_register = qiskit.QuantumRegister(
            num_index_qubits, self.labels[0]
        )
        channel_register = qiskit.QuantumRegister(
            num_channel_qubits, self.labels[1]
        )
        value_register = qiskit.QuantumRegister(
            num_value_qubits, self.labels[2]
        )

        circuit = qiskit.QuantumCircuit(
            value_register,
            channel_register,
            index_register,
            name=self.__class__.__name__,
        )
        circuit.h(channel_register)
        circuit.h(index_register)
        return circuit

    @utils.with_indexing
    def value_setting(
        self, circuit: qiskit.QuantumCircuit, index: int, value: float
    ) -> None:
        """Encodes the prepared, converted values to the initialised circuit.
        This function is used to set a single value at a single index. The
        decorator `with_indexing` applies the necessary control qubits
        corresponding to the given index.

        Args:
            circuit: Initialized Qiskit Circuit
            index: position to set the value
            value: value to be set at the index
        """
        value_register, channel_register, index_register = circuit.qregs

        # initialise sub-circuit
        sub_circuit = qiskit.QuantumCircuit(
            name=f"Sample {index} (CH {index%(2**channel_register.size)})"
        )
        sub_circuit.add_register(value_register)

        # rotate qubits with values
        sub_circuit.ry(2 * value, 0)

        # entangle with index qubits
        sub_circuit = sub_circuit.control(
            channel_register.size + index_register.size
        )

        # attach sub-circuit
        circuit.append(
            sub_circuit, list(i for i in range(circuit.num_qubits - 1, -1, -1))
        )

    def measure(self, circuit: qiskit.QuantumCircuit) -> None:
        """Adds classical measurements to all registers of the Quantum Circuit
        if the circuit is not already measured.

        Args:
            circuit: Encoded Qiskit Circuit
        """
        if not circuit.cregs:
            circuit.measure_all()

    # ----- Default Encode Function -----

    def encode(
        self,
        data: np.ndarray,
        measure: bool = True,
        verbose: Union[int, bool] = 1,
    ) -> qiskit.QuantumCircuit:
        """Given audio data, prepares a Qiskit Circuit representing it.

        Args:
            data: Array representing Digital Audio Samples
            measure: Adds measurement to the circuit if set True or int > 0.
            verbose: Level of information to print.

              - >1: Prints the number of qubits required.
              - >2: Displays the encoded circuit.

        Returns:
            A Qiskit Circuit representing the Digital Audio
        """
        data = utils.validate_data(data)

        (num_channels, num_samples), qubit_shape = self.calculate(
            data, verbose=verbose
        )
        num_index_qubits, num_channel_qubits, num_value_qubits = qubit_shape

        # prepare data
        data = self.prepare_data(data, num_index_qubits, num_channel_qubits)
        values = self.convert(data)

        # prepare circuit
        circuit = self.initialize_circuit(
            num_index_qubits, num_channel_qubits, num_value_qubits
        )

        # encode information
        for i, sample in enumerate(values):
            self.value_setting(circuit=circuit, index=i, value=sample)

        # additional information for decoding
        circuit.metadata = {
            "num_samples": num_samples,
            "num_channels": num_channels,
            "qubit_shape": qubit_shape,
            "scheme": circuit.name,
        }

        # measure
        if measure:
            self.measure(circuit)
        if verbose == 2:
            utils.draw_circuit(circuit, decompose=1)
        return circuit

    # ------------------- Decoding Helpers ---------------------------

    def decode_components(
        self,
        counts: Union[dict, qiskit.result.Counts],
        qubit_shape: Tuple[int, int],
    ) -> np.ndarray:
        """The first stage of decoding is extracting required components from
        counts.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.
            qubit_shape: Tuple to determine the number of (channels, samples) to get.

        Returns:
            2-D Array of shape (num_channels, num_samples)
            for further decoding.
        """
        # initialising components
        num_index_qubits = qubit_shape[0]
        num_channel_qubits = qubit_shape[1]

        num_samples = 2**num_index_qubits
        num_channels = 2**num_channel_qubits
        num_components = (num_channels, num_samples)

        cosine_amps = np.zeros(num_components)
        sine_amps = np.zeros(num_components)

        # getting components from counts
        for state in counts:
            index_bits, channel_bits, value_bits = utils.split_string(
                state, qubit_shape
            )
            index = int(index_bits, 2)
            channel = int(channel_bits, 2)
            value = counts[state]
            if value_bits == "0":
                cosine_amps[channel][index] = value
            elif value_bits == "1":
                sine_amps[channel][index] = value

        return cosine_amps, sine_amps

    def reconstruct_data(
        self,
        counts: Union[dict, qiskit.result.Counts],
        qubit_shape: Tuple[int, int],
        inverted: bool = False,
    ) -> np.ndarray:
        """Given counts, Extract components and restore the conversion did at
        encoding stage.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.
            qubit_shape: Tuple to determine the number of (channels, samples) to get.
            inverted : retrieves cosine components of the signal.

        Return:
            Array of restored values
        """
        cosine_amps, sine_amps = self.decode_components(counts, qubit_shape)
        data = self.restore(cosine_amps, sine_amps, inverted)
        return data

    def decode_counts(
        self,
        counts: Union[dict, qiskit.result.Counts],
        metadata: dict,
        inverted: bool = False,
        keep_padding: Tuple[int, int] = (False, False),
    ) -> np.ndarray:
        """Given a Qiskit counts object or Dictionary, Extract components and restore the
        conversion did at encoding stage.

        Args:
                counts: a qiskit Counts object or Dictionary obtained from a job result.
                metadata: metadata required for decoding.
                inverted : retrieves cosine components of the signal.
                keep_padding: Undo the padding set at Encoding stage if set to False.

                  - Dimension 0 for Channels.
                  - Dimension 1 for Time.

        Return:
                Array of restored values with original dimensions
        """
        # decoding x-axis
        index_position, channel_position, _ = self.positions
        qubit_shape = metadata["qubit_shape"]

        num_channel_qubits = qubit_shape[1]
        num_channels = 2**num_channel_qubits

        original_num_samples = metadata["num_samples"]
        original_num_channels = metadata["num_channels"]

        # decoding y-axis
        data = self.reconstruct_data(
            counts=counts,
            qubit_shape=qubit_shape,
            inverted=False,
        )

        # post-processing
        data = utils.restore_channels(data, num_channels)

        if not keep_padding[0]:
            data = data[:original_num_channels]

        if not keep_padding[1]:
            data = data[:, :original_num_samples]

        return data

    def decode_result(
        self,
        result: qiskit.result.Result,
        metadata: Optional[dict] = None,
        inverted: bool = False,
        keep_padding: Tuple[int, int] = (False, False),
    ) -> np.ndarray:
        """Given a result object. Extract components and restore the conversion
        did in the encoding stage.

        Args:
                result: a qiskit Result object that contains counts along
                        with metadata that was held by the original circuit.
                metadata: optionally pass metadata as argument.
                inverted : retrieves cosine components of the signal.
                keep_padding: Undo the padding set at Encoding stage if set to False.

                  - Dimension 0 for Channels.
                  - Dimension 1 for Time.

        Return:
                Array of restored values with original dimensions
        """
        counts = utils.get_counts(result)
        metadata = utils.get_metadata(result) if not metadata else metadata
        data = self.decode_counts(
            counts=counts,
            metadata=metadata,
            inverted=inverted,
            keep_padding=keep_padding,
        )
        return data

    # ----- Default Decode Function -----

    def decode(
        self,
        circuit: qiskit.QuantumCircuit,
        metadata: Optional[dict] = None,
        inverted: bool = False,
        keep_padding: Tuple[int, int] = (False, False),
        execute_function: Callable[
            [qiskit.QuantumCircuit, dict], Any
        ] = utils.execute,
        **kwargs,
    ) -> np.ndarray:
        """Given a qiskit circuit, decodes and returns the Original Audio Array.

        Args:
                circuit: A Qiskit Circuit representing the Digital Audio.
                metadata: optionally pass metadata as argument.
                inverted: retrieves cosine components of the signal.
                keep_padding: Undo the padding set at Encoding stage if set to False.

                  - Dimension 0 for Channels.
                  - Dimension 1 for Time.
                execute_function: Function to execute the circuit for decoding.
        Return:
                Array of decoded values
        """
        self.measure(circuit)
        result = utils.execute(circuit=circuit, **kwargs)
        data = self.decode_result(
            result=result,
            metadata=metadata,
            inverted=inverted,
            keep_padding=keep_padding,
        )
        return data
