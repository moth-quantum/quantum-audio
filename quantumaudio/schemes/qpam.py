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

from quantumaudio import utils


class QPAM:
    """Quantum Probability Amplitude Modulation (QPAM).

    QPAM class implements encoding and decoding of Digital Audio as
    Quantum Probability Amplitudes. It's the simplest of Schemes and
    uses Qiskit circuit's `initialize` method to set the Quantum States
    based on provided values. The values are normalized before encoding
    using the `convert` method.
    """

    def __init__(self) -> None:
        """Initialize the QPAM instance. The attributes of `__init__` method are
        specific to this Scheme which remains fixed and independent of the
        Data. These attributes gives an overview of the Scheme.

        Attributes:
            name:         Holds the full name of the representation.
            qubit_depth:  Number of qubits to represent the amplitude of an audio signal.
                          (Note: In QPAM, no additional qubit is
                          required to represent amplitude.)

            n_fold:       Term for fixed number of registers used in a representation.
            labels:       Name of the Quantum registers
            positions:    Index position of Quantum registers
                          (In Qiskit circuit the registers are arranged
                          from Top to Bottom)

            convert:      Function that applies a mathematical conversion of input at Encoding.
            restore:      Function that restores the conversion at Decoding.
        """
        self.name = "Quantum Probability Amplitude Modulation"
        self.qubit_depth = 0

        self.n_fold = 0
        self.labels = ("time", "amplitude")
        self.positions = (0,)

        self.convert = utils.convert_to_probability_amplitudes
        self.restore = utils.convert_from_probability_amplitudes
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
        ), "Multi-channel not supported in QPAM"
        num_value_qubits = self.qubit_depth

        num_qubits = (num_index_qubits, num_value_qubits)

        # print
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
        return circuit

    def value_setting(
        self, circuit: qiskit.QuantumCircuit, values: np.ndarray
    ) -> None:
        """Encodes the prepared, converted values to the initialised circuit.

        Args:
            circuit: Initialized Qiskit Circuit
            values: Array of probability amplitudes to encode
        """
        circuit.initialize(values)

    def measure(self, circuit: qiskit.QuantumCircuit) -> None:
        """Adds classical measurements to all qubits of the Quantum Circuit if
        the circuit is not already measured.

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
        verbose: Union[int, bool] = 2,
    ) -> qiskit.QuantumCircuit:
        """Given audio data, prepares a Qiskit Circuit representing it.

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
        norm, values = self.convert(data)
        # initialise circuit
        circuit = self.initialize_circuit(num_index_qubits, num_value_qubits)
        # encode values
        self.value_setting(circuit=circuit, values=values)
        # additional information for decoding
        circuit.metadata = {"num_samples": num_samples, "norm_factor": norm}
        if measure:
            self.measure(circuit)
        if verbose == 2:
            utils.draw_circuit(circuit)
        return circuit

    # ------------------- Decoding Helpers ---------------------------

    def decode_components(
        self, counts: Union[dict, qiskit.result.Counts]
    ) -> np.ndarray:
        """The first stage of decoding is extracting required components from
        counts.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.

        Returns:
            Array of components for further decoding.
        """
        counts = utils.pad_counts(counts)
        return np.array(list(counts.values()))

    def reconstruct_data(
        self,
        counts: Union[dict, qiskit.result.Counts],
        shots: int,
        norm: float,
    ) -> np.ndarray:
        """Given counts, Extract components and restore the conversion did at
        encoding stage.

        Args:
            counts: a dictionary with the outcome of measurements
                    performed on the quantum circuit.
            shots : total number of times the quantum circuit is measured.
            norm  : the norm factor used to normalize the decoding in QPAM.

        Return:
            data: Array of restored values
        """
        probabilities = self.decode_components(counts)
        data = self.restore(probabilities, norm, shots)
        return data

    def decode_result(
        self,
        result: qiskit.result.Result,
        norm: Optional[float] = None,
        keep_padding: bool = False,
    ) -> np.ndarray:
        """Given a Qiskit Result object, Extract components and restore the
        conversion did at encoding stage.

        Args:
            result: a qiskit Result object that contains counts along
                    with metadata that was held by the original circuit.
            shots : total number of times the quantum circuit is measured.
            norm  : the norm factor used to normalize the decoding.
            keep_padding: Undos the padding set at Encoding stage if set to False.

        Return:
            data: Array of restored values with original dimensions
        """
        
        counts, metadata = utils.get_counts_and_metadata(result)
        shots = metadata["shots"]
        norm = norm if norm else metadata["norm_factor"]
        
        if "num_samples" in metadata:
            original_num_samples = metadata["num_samples"]
        else:
            original_num_samples = None

        # reconstruct
        data = self.reconstruct_data(counts=counts, shots=shots, norm=norm)

        # undo padding
        if not keep_padding and original_num_samples:
            data = data[:original_num_samples]

        return data

    # ----- Default Decode Function -----

    def decode(
        self,
        circuit: qiskit.QuantumCircuit,
        backend: Optional[str] = None,
        shots: int = 4000,
        norm: Optional[float] = None,
        keep_padding: bool = False,
    ) -> np.ndarray:
        """Given a qiskit circuit, decodes and returns back the Original Audio Array.

        Args:
            circuit: A Qiskit Circuit representing the Digital Audio.
            backend: A backend string compatible with qiskit.execute method.
            shots  : Total number of times the quantum circuit is measured.
            norm   : The norm factor used to normalize the decoding in QPAM.
            keep_padding: Undo the padding set at Encoding stage if set to False.

        Return:
            data: Array of decoded values
        """
        self.measure(circuit)
        result = utils.execute(circuit=circuit, backend=backend, shots=shots)
        data = self.decode_result(result=result, keep_padding=keep_padding)
        return data
