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

"""This subpackage contains different schemes. The common information for using any scheme is detailed below.

A scheme denotes one of the Quantum Audio Representation Methods. The core functions of a scheme are encoding and decoding.

- **Encoding**: Takes in a digital audio array, performs necessary pre-processing, and prepares a quantum circuit. The quantum circuit can be used to create a state that represents the original digital audio.

- **Decoding**: Takes in the quantum circuit measurements, performs necessary post-processing, and reconstructs the original digital audio.

The simplest form of interaction with a scheme object is to use the `scheme.encode()` and `scheme.decode()` methods.

However, it involves several stages that can be manually implemented. The stages are listed below:

- **Calculate**: Calculates the necessary number of qubits for each quantum register with respect to the data shape, type of scheme, and any user-defined values valid for some schemes.

- **Data Pre-Processing**:

    - **Prepare Data**: Prepares the data by padding and reshaping.

    - **Convert**: Converts the data to values suitable for encoding.

- **Circuit Preparation**:

    - **Initialize Circuit**: Initializes the circuit with the calculated number of qubits for each quantum register representing a different aspect of the audio data (e.g., time register, value register, channel register, etc.).

    - **Value Setting**: Encodes or sets the converted values to the circuit.

    - **Add Metadata**: To keep encode and decode functions independent, key information lost during encoding (e.g., original sample length) can be preserved by manually attaching them as a dictionary to Qiskit's `circuit.metadata`. This is done by default in the `scheme.encode()` method.

    - **Measure (Optional)**: Adds appropriate classical registers for measurement.

- **Encode**: Combines all the above steps.

- **Execute (Optional)**: The circuit can be executed externally with any provider or internally using Qiskit's `execute` method, included in the `scheme.decode()` method, which uses the Aer simulator by default.

- **Decoding Stages**:

    1. **Decode Components**: Extracts required components directly from the counts (i.e., a dictionary with the outcome of measurements performed on the quantum circuit).

    2. **Undo Conversion**: Undoes the data conversion done during encoding. This can be done using the `scheme.restore()` method.

    3. **Undo Preparation**: Undoes the data preparation, such as padding, done during encoding. This can be done manually using NumPy slicing and reshape methods.

- **Reconstruct Data**: Takes in a counts dictionary for decoding, combining Decoding Stages 1 and 2.

- **Decode Result**: Takes in a Qiskit `result` object for decoding, combining Decoding Stages 1, 2, and 3. It considers additional metadata, such as the original sample length, to undo the padding done at the data preparation stage.

- **Decode**: Takes in a Qiskit `circuit` object for decoding, performs measurement (if needed), and default execution, followed by all stages of decoding.
"""

import importlib

def __getattr__(name):
    """Dynamically load and instantiate a scheme class."""
    try:
        module = importlib.import_module(f".{name.lower()}", package=__name__)
        return getattr(module, name.upper())
    except (ImportError, AttributeError) as e:
        raise AttributeError(
            f"module {__name__} has no attribute {name}"
        ) from e


def __dir__():
    return __all__


__all__ = ["QPAM", "SQPAM", "QSM", "MSQPAM", "MQSM"]
