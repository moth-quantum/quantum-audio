.. container::

   |Python version| |PyPI| |Read the Docs (version)| |LICENSE| |DOI|
   |Open in Colab|

   An open-source Python package for building Quantum Representations of
   Digital Audio using *Qiskit* circuits.

What is Quantum Audio ?
-----------------------

Quantum Audio refers to standard methods of encoding Digital Audio
Information as Quantum Information, leveraging principles of Quantum
mechanics for Audio Signal Processing. Here, the information is processed 
using quantum bits, or qubits, instead of classical bits (0s and 1s).

The ``quantumaudio`` package provides fundamental operations for
representing audio samples as Quantum States that can be processed on a
Quantum computer (or a Simulator) and played back.

.. code:: python

   quantumaudio.encode(audio)   #returns a quantum circuit
   quantumaudio.decode(circuit) #returns audio samples

Installation 
------------

To install the Quantum Audio Package, run the 
following command in Terminal or Command Prompt:

.. code:: console

   pip install quantumaudio


Additional dependencies required for the demos provided in
the GitHub repository can be installed using ``pip``:

.. code:: console

   pip install "quantumaudio[demos]"

This includes Digital Audio Dependencies (`soundfile` and `librosa`) and 
an Interative notebook dependency (`ipywidgets`). 


Overview 
--------

Modulation Schemes are essential methods for encoding Audio signals in
both Analog (such as **FM**) and Digital (such as **PCM**)
formats. The same is extended for Quantum Audio. The package contains
different schemes to encode audio and necessary utilities.

The following subpackages can be accessed from ``quantumaudio``:

-  ``schemes`` : Quantum Audio Representation Methods

   - **QPAM**: Quantum Probability Amplitude Modulation (Original: `Real-ket <https://doi.org/10.1007/s11128-015-1208-5>`__)

   - **SQPAM**: Single-Qubit Probability Amplitude Modulation (Original: `FRQI <http://dx.doi.org/10.1007/s11128-010-0177-y>`__)

   - **MSQPAM**: Multi-channel Single-Qubit Probability Amplitude Modulation (Original: `PMQA <https://doi.org/10.1007/s11128-022-03435-7>`__)

   - **QSM**: Quantum State Modulation (Original: `FRQA <https://doi.org/10.1016/j.tcs.2017.12.025>`__)

   - **MQSM**: Multi-channel Quantum State Modulation (Original: `QRMA <https://doi.org/10.1007/s11128-019-2317-3>`__)

-  ``utils`` : Common utilary functions for data processing, analysis,
   circuit preparation, etc.

Additionally, ``tools`` contain extension functions that support basic
visual analysis and audio processing.

Usage 
-----

Using Schemes
^^^^^^^^^^^^^

Get started on creating Quantum Audio Representations with just a few
lines of code.

.. code:: python

   # An instance of a scheme can be created using:
   import quantumaudio
   qpam = quantumaudio.load_scheme("qpam") # or directly access from quantumaudio.schemes.QPAM()

   # Define an Input
   original_data = quantumaudio.tools.test_signal() # for a random array of samples (range: -1.0 to 1.0)

   # Encoding
   encoded_circuit = qpam.encode(original_data)

   # ... optionally do some analysis or processing

   # Decoding
   decoded_data  = qpam.decode(encoded_circuit,shots=4000)    


Using Functions
^^^^^^^^^^^^^^^

The core functions are also directly accessible without declaring a
Scheme object. (Refer to :ref:`Documentation <functions>` for all the available
functions)

.. code:: python

   circuit = quantumaudio.encode(data, scheme="qpam")
   decoded_data = quantumaudio.decode(circuit)

Here, any remaining arguments can be passed as keywords
e.g. ``quantumaudio.encode(data, scheme="qsm", measure="False")``.


Working with Digital Audio
^^^^^^^^^^^^^^^^^^^^^^^^^^

For faster processing of longer arrays, the ``stream`` method is
preferred.

.. code:: python

   quantumaudio.stream(data)

It wraps the functions provided in the module
``quantumaudio.tools.stream`` that help process large arrays as chunks
for efficient handling. Examples of its usage can be found in the
`Demos <https://github.com/moth-quantum/quantum-audio/blob/demos/>`__
provided in the repository.

Running on Native Backends
^^^^^^^^^^^^^^^^^^^^^^^^^^

A Scheme’s ``decode()`` method uses local
`AerSimulator <https://github.com/Qiskit/qiskit-aer>`__ as the default
backend. Internally, the function calls ``quantumaudio.utils.execute``
method to perform ``backend.run()`` method. Any Qiskit compatible
backend object can be specified by passing the ``backend=`` parameter to
the ``decode()`` function.

Running on External Quantum Backends
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The package allows flexible use of Quantum Hardware from different
Providers as the execution of circuits can be done independently.
Depending on the results, there are two ways to decode quantum audio:

-  **Results Object:** If the result obtained follow the format of
   `qiskit.result.Result <https://docs.quantum.ibm.com/api/qiskit/qiskit.result.Result>`__
   or
   `qiskit.primitives.PrimitiveResult <https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.PrimitiveResult>`__,

   -  The audio can be decoded with
      ``scheme.decode_result(result_object)`` method.
   -  In this case, relevant metadata information is automatically
      extracted and applied at decoding. It can also be manually passed
      using ``metadata=`` parameter.

-  **Counts Dictionary:** If the result is in form of a counts
   dictionary or
   `qiskit.result.Counts <https://docs.quantum.ibm.com/api/qiskit/qiskit.result.Counts>`__
   object,

   -  The audio can be decoded using
      ``scheme.decode_counts(counts, metadata)`` method.
   -  The metadata dictionary can be accessed from the encoded circuit
      using ``circuit.metadata``.

Using Custom Functions
^^^^^^^^^^^^^^^^^^^^^^

The ``decode`` and ``stream`` operations can be configured with the
following custom functions. They require few mandatory arguments
followed by custom preceding keyword arguments (denoted as
``**kwargs``). 

- **Process Function**: The default process function of ``stream()`` simply encodes and decodes a chunk of data with default parameters. It can be overriden by passing a custom function to the ``process_function=`` parameter. The mandatory arguments for the custom process function are ``data=`` and ``scheme=``.

.. code:: python

   processed_data = process_function(data, scheme, **kwargs)

-  **Execute Function**: The default execute function for ``decode()``
   can be overriden by passing a custom function to the
   ``execute_function=`` parameter. The mandatory argument for the
   custom execute function is ``circuit=``.

.. code:: python

   result = execute_function(circuit, **kwargs)

**Example**: An optional execute function is included in the package
which uses `Sampler
Primitive <https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/qiskit_ibm_runtime.SamplerV2>`__:
``quantumaudio.utils.execute_with_sampler`` that can be passed to the
``decode()`` method.


Version Information 
-------------------

Pre-release original version: ``v0.0.2``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project is derived from research output on Quantum Representations
of Audio, carried by Interdisciplinary Centre for Computer Music
Research (`ICCMR <https://www.plymouth.ac.uk/research/iccmr>`__),
University of Plymouth, UK, namely:

-  Itaboraí, P.V., Miranda, E.R. (2022). Quantum Representations of
   Sound: From Mechanical Waves to Quantum Circuits. In: Miranda, E.R.
   (eds) Quantum Computer Music. Springer, Cham.
   https://doi.org/10.1007/978-3-031-13909-3_10

-  Itaboraí, P. V. (2022). Quantumaudio Module (Version 0.0.2) [Computer
   software]. https://github.com/iccmr-quantum/quantumaudio

-  Itaboraí, P. V. (2023) Towards Quantum Computing for Audio and Music
   Expression. Thesis. University of Plymouth. Available at:
   https://doi.org/10.24382/5119

Redevelopment: ``v0.1.0``
^^^^^^^^^^^^^^^^^^^^^^^^^

This project has been completely re-developed and is now maintained by
\ `Moth Quantum <https://mothquantum.com>`__\ .

-  **New Architecture:**

   -  This project has been restructured for better flexibility and
      scalability.
   -  Instead of *QuantumAudio* Instances, the package begins at the
      level of *Scheme* Instances that perform encoding and decoding
      functions independent of the data.

-  **Feature Updates:**

   -  Introducing 2 Additional Schemes that can encode and decode
      Multi-channel Audio.
   -  Supports Faster encoding and decoding of long audio files using
      Batch processing.

-  **Dependency Change:**

   -  Support for *Qiskit* is updated from ``v0.22`` to ``v1.0+``

-  **Improvements:**

   -  Improved organisation of code for Readability and Modularity.
   -  Key metadata information is preserved during the encoding
      operation, making the decoding process independent.

-  **License Change:**

   -  The License is updated from **MIT** to **Apache 2.0**

Citing 
------

If you use this code or find it useful in your research, please consider
citing: `DOI <>`__

--------------

Copyright
---------

Copyright 2024 Moth Quantum

Licensed under the Apache License, Version 2.0 (the “License”); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Contact
-------

If you have any questions or need further assistance, please feel free
to contact Moth Quantum at hello@mothquantum.com

.. |Python version| image:: https://img.shields.io/badge/python-3.9+-important
.. |PyPI| image:: https://img.shields.io/pypi/v/quantumaudio
.. |Read the Docs (version)| image:: https://img.shields.io/readthedocs/quantumaudio/latest?label=API%20docs
.. |LICENSE| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://github.com/moth-quantum/quantum-audio/blob/main/LICENSE
.. |DOI| image:: https://zenodo.org/badge/DOI/10.1234/zenodo.123456.svg
   :target: https://doi.org/
.. |Open in Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1qGWhTLWoxnJsR7tINR6MVGDvk56CX2uE?ts=66c70dcd
