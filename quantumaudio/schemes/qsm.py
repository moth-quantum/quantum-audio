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

from typing import Optional, Union

import numpy as np
import qiskit
from bitstring import BitArray

from quantumaudio import utils


class QSM:
    """Quantum State Modulation (QSM).

    QSM class implements an encoding and decoding scheme where the
    amplitude of a Digital signal is encoded as qubit states controlled
    by qubits of time register that represent the corresponding time index.
    """

    def __init__(self, qubit_depth: Optional[int] = None) -> None:
        """Initialize the QSM instance. The attributes of `__init__` method are
        specific to this Scheme which remains fixed and independent of the
        Data. These attributes gives an overview of the Scheme.

        Attributes:
            name:         Holds the full name of the representation.
            qubit_depth:  Number of qubits to represent the amplitude of
                          an audio signal.
                          (Note: In QSM, this is a variable
                          that depends on the bit depth of audio)

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
        """
        self.name = "Quantum State Modulation"
        self.qubit_depth = qubit_depth

        self.n_fold = 1
        self.labels = ("time", "amplitude")
        self.positions = (1, 0)

        self.convert = utils.quantize
        self.restore = utils.de_quantize
        print(self.name)

    # ------------------- Encoding Helpers ---------------------------

    # ----- Data Preparation -----

    def calculate(
        self, data: np.ndarray, verbose: Union[int, bool] = True
    ) -> tuple[int, tuple[int, int]]:
        """Returns necessary information required for Encoding and Decoding:

         - Number of qubits required to encode both Time and Amplitude information.
         - Original number of samples required for decoding.

        Args:
            data: Array representing Digital Audio Samples.
            verbose: Prints the Qubit information if True or int > 0.

        Returns:
            A tuple of (num_samples, number_qubits)
            number_qubits is a tuple (int, int) consisting of:
            - num_index_qubits to encode Time Information (x-axis).
            - num_value_qubits to encode Amplitude Information (y-axis).
        """
        # x-axis
        num_samples = data.shape[-1]
        num_index_qubits = utils.get_qubit_count(num_samples)

        # y-axis
        assert (
            data.ndim == 1 or data.shape[0] == 1
        ), "Multi-channel not supported in QSM"
        num_value_qubits = (
            utils.get_bit_depth(data)
            if not self.qubit_depth
            else self.qubit_depth
        )

        num_qubits = (num_index_qubits, num_value_qubits)
        if verbose:
            utils.print_num_qubits(num_qubits, labels=self.labels)
        return num_samples, num_qubits

    def prepare_data(
        self, data: np.ndarray, num_index_qubits: int
    ) -> np.ndarray:
        """Prepares the data with appropriate dimensions for encoding:

        - It pads the length of data with zeros to fit the number of states
          that can be represented with `num_index_qubits`.
        - It also removes redundant dimension if the shape is (1,num_samples).

        Args:
            data: Array representing Digital Audio Samples
            num_index_qubits: Number of qubits used to encode the sample indices.

        Returns:
            data: Array with dimensions suitable for encoding.

        Note:
            This method should be followed by scheme.convert()
            to convert the values suitable for encoding.
        """
        data = utils.apply_index_padding(data, num_index_qubits)
        data = data.squeeze()
        return data

    # ----- Circuit Preparation -----

    def initialize_circuit(
        self, num_index_qubits: int, num_value_qubits: int
    ) -> qiskit.QuantumCircuit:
        """Initializes the circuit with Index and Value Registers.

        Args:
            num_index_qubits: Number of qubits used to encode the sample indices.
            num_value_qubits: Number of qubits used to encode the sample values.

        Returns:
            circuit: Qiskit Circuit with the registers
        """
        index_register = qiskit.QuantumRegister(
            num_index_qubits, self.labels[0]
        )
        value_register = qiskit.QuantumRegister(
            num_value_qubits, self.labels[1]
        )
        # Arranging Registers from Top to Bottom
        circuit = qiskit.QuantumCircuit(
            value_register, index_register, name=self.__class__.__name__
        )
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
        a_bitstring = []
        value_register, index_register = circuit.qregs
        for i, areg_qubit in enumerate(value_register):
            a_bit = (value >> i) & 1
            a_bitstring.append(a_bit)
            if a_bit:
                circuit.mcx(index_register, areg_qubit)

    def measure(self, circuit: qiskit.QuantumCircuit) -> None:
        """Adds classical measurements to all registers of the Quantum Circuit
        if the circuit is not already measured.

        Args:
            circuit: Encoded Qiskit Circuit
        """
        if not circuit.cregs:
            circuit.barrier()
            circuit.measure_all()

    # ----- Default Encode Function -----

    def encode(
        self,
        data: np.ndarray,
        measure: bool = True,
        verbose: Union[int, bool] = 2,
    ) -> qiskit.QuantumCircuit:
        """Given an audio data, prepares a Qiskit Circuit representing it.

        Args:
            data: Array representing Digital Audio Samples
            measure: Adds measurement to the circuit if set True or int > 0.
            verbose: Level of information to print.
                     - >1: Prints number of qubits required.
                     - >2: Displays the encoded circuit.

        Returns:
            A Qiskit Circuit representing the Digital Audio
        """
        num_samples, (num_index_qubits, num_value_qubits) = self.calculate(
            data, verbose=bool(verbose)
        )
        # prepare data
        data = self.prepare_data(data, num_index_qubits)
        # convert data
        values = self.convert(data, num_value_qubits)
        # initialise circuit
        circuit = self.initialize_circuit(num_index_qubits, num_value_qubits)
        # encode values
        for i, sample in enumerate(values):
            self.value_setting(circuit=circuit, index=i, value=sample)

        # additional information for decoding
        circuit.metadata = {
            "num_samples": num_samples,
            "num_qubits": (num_index_qubits, num_value_qubits),
        }

        # measure, print and return
        if measure:
            self.measure(circuit)
        if verbose == 2:
            utils.draw_circuit(circuit)
        return circuit

    # ------------------- Decoding Helpers ---------------------------

    def decode_components(
        self,
        counts: Union[dict, qiskit.result.Counts],
        num_components: int,
    ) -> np.ndarray:
        """The first stage of decoding is extracting required components from
        counts.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.
            num_components: number of components to get.

        Returns:
            Array of components for further decoding.
        """
        data = np.zeros(num_components, int)
        num_index_qubits = int(np.log2(num_components))
        for state in counts:
            index_bits = state[:num_index_qubits]
            value_bits = state[num_index_qubits:]
            index = int(index_bits, 2)
            value = BitArray(bin=value_bits).int
            data[index] = value
        return data

    def reconstruct_data(
        self,
        counts: Union[dict, qiskit.result.Counts],
        num_components: int,
        qubit_depth: int,
    ) -> np.ndarray:
        """Given counts, Extract components and restore the conversion did at
        encoding stage.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.
            num_components: number of components to get.
            qubit_depth : number of qubits in amplitude register.

        Return:
            data: Array of restored values
        """
        data = self.decode_components(counts, num_components)
        data = self.restore(data, qubit_depth)
        return data

    def decode_result(
        self,
        result: qiskit.result.Result,
        keep_padding: bool = False,
    ) -> np.ndarray:
        """Given a result object. Extract components and restore the conversion
        did in encoding stage.

        Args:
                result: a qiskit Result object that contains counts along
                        with metadata that was held by the original circuit.
                keep_padding: Undo the padding set at Encoding stage if set False.

        Return:
                data: Array of restored values with original dimensions
        """

        counts, metadata = utils.get_counts_and_metadata(result)
        index_position, amplitude_position = self.positions

        # decoding x-axis
        num_index_qubits = metadata["num_qubits"][0]
        num_samples = 2**num_index_qubits
        original_num_samples = metadata["num_samples"]

        # decoding y-axis
        qubit_depth = metadata["num_qubits"][0]
        data = self.reconstruct_data(counts, num_samples, qubit_depth)

        # undo padding
        if not keep_padding:
            data = data[:original_num_samples]
        return data

    # ----- Default Decode Function -----

    def decode(
        self,
        circuit: qiskit.QuantumCircuit,
        backend: Optional[str] = None,
        shots: int = 4000,
        keep_padding: bool = False,
    ) -> np.ndarray:
        """Given a qiskit circuit, decodes and returns back the Original Audio Array.

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
