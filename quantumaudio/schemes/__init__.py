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

"""A **Scheme** denotes one of the **Quantum Audio Representation Methods**. 
This subpackage provides different schemes. The common information
for using any scheme is detailed below.

===========
Basic Usage
===========

The core functions of a scheme are encoding and decoding.

- `Encoding`: Takes in a digital audio array, performs necessary pre-processing, 
  and prepares a quantum circuit. The quantum circuit can be used to create a state
  that represents the original digital audio. 

- `Decoding`: Takes in the quantum circuit measurements, performs necessary 
  post-processing, and reconstructs the original digital audio.

The simplest form of interaction with a `Scheme` object is to use the 
``encode()`` and ``decode()`` methods, as indicated by the base class
:ref:`quantumaudio.scheme.Scheme <base-scheme>`.

==============
Detailed Steps
==============

The Encoding and Decoding operations of a scheme can involve several stages
that can be manually used for research and debugging purposes. The stages 
of schemes implemented in the package are listed below.

Encoding
========

- **Analysis**

    - `Calculate`: Calculates the necessary number of qubits for each quantum register
      with respect to the data shape, type of scheme, and any user-defined values valid
      for some schemes. (``calculate()``)

- **Data Pre-Processing**
    - `Prepare Data`: Prepares the data dimension by padding and reshaping. 
      For multi-channel schemes, it also handles the arrangement of samples. (``prepare_data()``)
    - `Convert`: Converts the data to values suitable for encoding. (``convert()``)

- **Circuit Preparation**
    - `Initialize Circuit`: Initializes the circuit with the calculated 
      number of qubits for each quantum register representing a different 
      aspect of the audio data (i.e. time, value and channel). (``initialize_circuit()``)
    - `Value Setting`: Encodes or sets the converted values to the circuit. (``value_setting()``)
    
- **Adding Metadata**
    - To keep encode and decode functions independent, key information lost during encoding 
      (e.g., original sample length) is preserved as a Python Dictionary. This can be manually attached to
      `Qiskit` circuit's ``.metadata`` attribute or passed separately as argument ``metadata=`` in a decode function.

Intermediate
============

- **Measure**
    - Add appropriate classical registers to the encoded circuit for measurement.
      This can be implemented with a scheme's ``measure()`` method or simply with 
      `Qiskit` circuit's ``measure_all()`` attribute. 
    - By default, ``encode()`` method returns measured circuit unless specified ``measure=False`` when calling it. 

- **Execute**
    - The measured and encoded circuit can be executed externally with any provider.
    - By default, the ``decode()`` method executes with IBM's `AerSimulator` by calling :ref:`quantumaudio.utils.execute <execute>` method.  
    

Decoding
========

- **Decoding Stages**
    1. `Decode Components`: Extracts required components directly from 
       the counts (i.e., a dictionary with the outcome of measurements performed on the quantum circuit).
       (``decode_components()``)

    2. `Undo Conversion`: Undoes the data conversion done during encoding. 
       This can be done using the ``restore()`` method. (It performs the inverse of ``convert()`` method)

    3. `Undo Preparation`: Undoes the data preparation, such as padding, done 
       during encoding. This can be done manually using NumPy slicing and reshape methods.
       For multi-channel schemes, the arrangement of samples must also be restored.

- **Reconstruct Data**
    - Takes in a counts dictionary for decoding, combining Decoding Stages 1 and 2.

- **Decode Counts** 
    - Takes in a counts dictionary for decoding, combining Decoding Stages 1 and 2. 
      Additionally, it requires metadata, to restore the original dimensions of data.

- **Decode Result**
    - Takes in a Qiskit `result` object for decoding, combining Decoding Stages 1, 2, and 3. 
      It considers additional metadata, such as the original sample length, to undo the padding done at the data preparation stage.

- **Decode**
    - Takes in a Qiskit `circuit` object for decoding, performs measurement (if needed), and 
      default execution, followed by all stages of decoding.
"""

import importlib
from .base_scheme import Scheme


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


__all__ = ["QPAM", "SQPAM", "QSM", "MSQPAM", "MQSM", "Scheme"]
