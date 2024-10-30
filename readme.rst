.. container::

   .. rubric:: Quantum Audio
      :name: quantum-audio

   |Python version| |PyPI| |Read the Docs (version)| |LICENSE| |DOI|
   |Open in Colab|

   An open-source Python package for building Quantum Representations of
   Digital Audio using *Qiskit* circuits.

💿 What is Quantum Audio ?
--------------------------

Quantum audio refers to the application of principles from quantum
mechanics to the creation, processing, and analysis of sound or audio
signals.

   Here, the information is processed using quantum bits, or qubits,
   instead of classical bits (0s and 1s).

New Paradigm 🎵
^^^^^^^^^^^^^^^

Audio plays a vital role in carrying information and music, traversing
through domains — from **Analog** and **Digital** formats to engaging
our senses in a profound way. With the advent of Quantum Computing,
**Quantum Audio** formulate ways of representing Audio in the Quantum
Domain, enabling new explorations in artistic and research contexts 💫

The Package 📦
^^^^^^^^^^^^^^

The ``quantumaudio`` package provides fundamental operations for
representing audio samples as Quantum States that can be processed on a
Quantum computer (or a Simulator) and played back 🔊

.. code:: python

   quantumaudio.encode(audio)   # returns a quantum circuit
   quantumaudio.decode(circuit) # returns audio samples

..

   Quantum Audio represents Audio in terms of Quantum Circuits and does
   not require Quantum Memory for storage.

🗒️ Table of Contents
--------------------

- `Overview <#overview>`__
- `Version Information <#version>`__
- `Installation <#installation>`__
- `Usage <#usage>`__
- `Additional Resources <#materials>`__
- `Contributing <#contributing>`__
- `Future Releases <#future-releases>`__
- `Citing <#citation>`__

🔍 Overview 
------------

Modulation Schemes are essential methods for encoding Audio signals in
both Analog (such as **FM** 📻) and Digital (such as **PCM** 💻)
formats. The same is extended for Quantum Audio. The package contains
different schemes to encode audio and necessary utilities.

The following subpackages can be accessed from ``quantumaudio``:

- ``schemes``: Quantum Audio Representation Methods. The following are
  included in the package:

+-----------+-----------------------------+---------------------------+
| Acronym   | Representation Name         | Original Reference        |
+===========+=============================+===========================+
| **QPAM**  | Quantum Probability         | `Real-                    |
|           | Amplitude Modulation        | Ket <https://doi.org/10.1 |
|           |                             | 007/s11128-015-1208-5>`__ |
+-----------+-----------------------------+---------------------------+
| **SQPAM** | Single-Qubit Probability    | `FRQ                      |
|           | Amplitude Modulation        | I <http://dx.doi.org/10.1 |
|           |                             | 007/s11128-010-0177-y>`__ |
+-----------+-----------------------------+---------------------------+
| *         | Multi-channel Single-Qubit  | `PM                       |
| *MSQPAM** | Probability Amplitude       | QA <https://doi.org/10.10 |
|           | Modulation                  | 07/s11128-022-03435-7>`__ |
+-----------+-----------------------------+---------------------------+
| **QSM**   | Quantum State Modulation    | `F                        |
|           |                             | RQA <https://doi.org/10.1 |
|           |                             | 016/j.tcs.2017.12.025>`__ |
+-----------+-----------------------------+---------------------------+
| **MQSM**  | Multi-channel Quantum State | `Q                        |
|           | Modulation                  | RMA <https://doi.org/10.1 |
|           |                             | 007/s11128-019-2317-3>`__ |
+-----------+-----------------------------+---------------------------+

- ``utils`` : Common utilary functions for data processing, analysis,
  circuit preparation, etc.

Additionally, ``tools`` contain extension functions that support basic
visual analysis and audio processing.

   For a quick tour of Quantum Audio, try
   `Colab <https://colab.research.google.com/drive/1qGWhTLWoxnJsR7tINR6MVGDvk56CX2uE?ts=66c70dcd>`__
   🚀

For more details of the package, please refer to the
`Documentation <https://quantumaudio.readthedocs.io>`__ site.

🧩 Version Information 
-----------------------

Pre-release original version: ``v0.0.2``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project is derived from research output on Quantum Representations
of Audio, carried by Interdisciplinary Centre for Computer Music
Research (`ICCMR <https://www.plymouth.ac.uk/research/iccmr>`__),
University of Plymouth, UK, namely:

- Itaboraí, P.V., Miranda, E.R. (2022). Quantum Representations of
  Sound: From Mechanical Waves to Quantum Circuits. In: Miranda, E.R.
  (eds) Quantum Computer Music. Springer, Cham.
  https://doi.org/10.1007/978-3-031-13909-3_10

- Itaboraí, P. V. (2022). Quantumaudio Module (Version 0.0.2) [Computer
  software]. https://github.com/iccmr-quantum/quantumaudio

- Itaboraí, P. V. (2023) Towards Quantum Computing for Audio and Music
  Expression. Thesis. University of Plymouth. Available at:
  https://doi.org/10.24382/5119

For more details, see the `NOTICE <NOTICE>`__ file.

Redevelopment: ``v0.1.0``
~~~~~~~~~~~~~~~~~~~~~~~~~

This project has been completely re-developed and is now maintained by
\ `Moth Quantum <https://mothquantum.com>`__\ .

- **New Architecture:**

  - This project has been restructured for better flexibility and
    scalability.
  - Instead of *QuantumAudio* Instances, the package begins at the level
    of *Scheme* Instances that perform encoding and decoding functions
    independent of the data.

- **Feature Updates:**

  - Introducing 2 Additional Schemes that can encode and decode
    Multi-channel Audio.
  - Supports Faster encoding and decoding of long audio files using
    Batch processing.

- **Dependency Change:**

  - Support for *Qiskit* is updated from ``v0.22`` to ``v1.0+``

- **Improvements:**

  - Improved organisation of code for Readability and Modularity.
  - Key metadata information is preserved during the encoding operation,
    making the decoding process independent.

- **License Change:**

  - The License is updated from **MIT** to **Apache 2.0**

Migration Guide
~~~~~~~~~~~~~~~

If you’re transitioning from the previous version, please check the
`Migration
Guide <https://github.com/moth-quantum/quantum-audio/blob/main/docs/guides/MIGRATION.md>`__
for an overview of the package usability.

🪄 Installation 
----------------

To install the Quantum Audio Package, you can use ``pip`` (included with
Python) which installs it from
`PyPI <https://pypi.org/project/quantumaudio/>`__ package manager. Run
the following command in Terminal or Command Prompt:

.. code:: console

   pip install quantumaudio

For local installation by
`cloning <https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository>`__,
navigate to the cloned directory in Terminal or Command Prompt and run:
``pip install .`` or ``pip install -r requirements.txt``

   [!Note] When using ``pip`` commands to install packages and
   dependencies, it’s recommended to use a **virtual environment** to
   keep them isolated from the system’s Python. This will avoid any
   dependency conflicts. Instructions on using a virtual environment are
   provided
   `here <https://github.com/moth-quantum/quantum-audio/blob/main/docs/guides/ENVIRONMENT.md>`__.

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

All additional dependencies required that support the demos provided in
the repository can be installed using ``pip``:
``pip install "quantumaudio[demos]"`` It includes the following
collection of dependencies, also mentioned in the folder
``demos/requirements``:

- **Digital Audio Dependencies** The core package operates with *numpy*
  arrays. Dependencies for audio file handling to run audio examples in
  notebook and scripts in the repository can be separately installed
  using ``pip install soundfile==0.12.1 librosa==0.10.2.post1``

..

   [!Tip] If using your own choice of libraries for digital audio
   processing, please be aware that Multi-channel Quantum Audio is
   processed with *Channels First* data structure. e.g. ``(2, N)`` for a
   Stereo Audio of ``N`` samples.

- **Notebook Dependencies** The `Demo
  Notebook <https://github.com/moth-quantum/quantum-audio/blob/main/demos/1_Basics_Walkthrough.ipynb>`__
  features interactive elements that require additional dependency. It
  can be installed using ``pip install ipywidgets``

🎛️ Usage 
---------

Using Schemes
~~~~~~~~~~~~~

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

..

   [!Note] The ``encode`` function returns a circuit with attached
   classical measurements by default. In Qiskit, it is not possible to
   directly modify a circuit after these measurements are added. If you
   wish to return a circuit without measurements, you can specify
   ``measure=False`` while encoding.

Using Functions
~~~~~~~~~~~~~~~

The core functions are also directly accessible without declaring a
Scheme object. (Refer to
`Documentation <https://quantumaudio.readthedocs.io/>`__ for all the
available functions)

.. code:: python

   circuit = quantumaudio.encode(data, scheme="qpam")
   decoded_data = quantumaudio.decode(circuit)

Here, any remaining arguments can be passed as keywords
e.g. ``quantumaudio.encode(data, scheme="qsm", measure="False")``.

   [!Note] The circuit depth can grow complex for a long array of
   samples which is the case with Digital Audio. It is optimal to
   represent a short length of samples per Circuit when using the
   ``encode()`` method.

Working with Digital Audio
~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~

A Scheme’s ``decode()`` method uses local
`AerSimulator <https://github.com/Qiskit/qiskit-aer>`__ as the default
backend. Internally, the function calls ``utils.execute()`` method that
performs ``backend.run()``. Any such backend object compatible with
Qiskit can be passed to the ``backend=`` parameter of the ``decode()``
function. To configure this further or to use primitives, please refer
to custom `execute functions <#custom_functions>`__.

Running on External Quantum Backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package allows flexible use of Quantum Hardware from different
Providers as the execution of circuits can be done independently.
Depending on the results, there are two ways to decode quantum audio:

- **Results Object:** If the result obtained follow the format of
  `qiskit.result.Result <https://docs.quantum.ibm.com/api/qiskit/qiskit.result.Result>`__
  or
  `qiskit.primitives.PrimitiveResult <https://docs.quantum.ibm.com/api/qiskit/qiskit.primitives.PrimitiveResult>`__,

  - The audio can be decoded with
    ``scheme.decode_result(result_object)`` method.
  - In this case, relevant metadata information is automatically
    extracted and applied at decoding. It can also be manually passed
    using ``metadata=`` parameter.

- **Counts Dictionary:** If the result is in form of a counts dictionary
  or
  `qiskit.result.Counts <https://docs.quantum.ibm.com/api/qiskit/qiskit.result.Counts>`__
  object,

  - The audio can be decoded using
    ``scheme.decode_counts(counts, metadata)`` method.
  - Here, the metadata dictionary is required which can be obtained from
    the encoded circuit’s ``.metadata`` attribute.

..

   [!Tip] **Dictionaries** are data type in python to store {key :
   *value*} pairs. - **Counts Dicitonary** contains keys representing
   classical measurement outcomes and values indicating the number of
   times the outcome was observed. Example:
   ``{'00': 77, '01': 79, '10': 84, '11': 72}``. - **Metadata
   Dictionary** stores the key information that is required at decoding,
   which is commonly the original data dimensions to restore and layout
   of qubits. Both can be obtained from ``scheme.calculate()`` method.

Viewing Metadata
~~~~~~~~~~~~~~~~

The Metadata Information can be viewed from the encoded circuit’s
``.metadata`` attribute. The common keys found in a metadata are: -
**num_samples** (*int*) : Original sample length to restore. -
**num_channels** (*int*): Original number of channels to restore.
(Applicable for multi-channel schemes) - **qubit_shape** (*tuple*):
Stores the arrangement and number of qubits that encode each aspect of
the audio information i.e. *Time*, *Channel* (if applicable) and
*Amplitude*.

The *QPAM* scheme’s encoding only preserves **num_samples** (*int*) and
the normalization factor - **norm_factor** (*float*) which is required
to restore the values. > [!Note] > When passing metadata manually in any
of the decode functions, *QPAM* Scheme additionaly requires **shots**
(*int*) information used for executing the circuit which can also be
passed through the argument ``shots=``.

   [!Tip] The essential keys required for decoding with any scheme can
   be checked from the scheme’s ``.keys`` attribute.

Using Custom Functions 
~~~~~~~~~~~~~~~~~~~~~~~

The ``decode`` and ``stream`` operations can be configured with the
following custom functions. They require few mandatory arguments
followed by custom preceding keyword arguments (denoted as
``**kwargs``). - **Process Function**: The default process function of
``stream()`` simply encodes and decodes a chunk of data with default
parameters. It can be overriden by passing a custom function to the
``process_function=`` parameter. The mandatory arguments for the custom
process function are ``data=`` and ``scheme=``.

.. code:: python

   processed_data = process_function(data, scheme, **kwargs)

- **Execute Function** : The default execute function for ``decode()``
  can be overriden by passing a custom function to the
  ``execute_function=`` parameter. The mandatory argument for the custom
  execute function is ``circuit=``. (QPAM also expects ``shots=`` since
  it’s a metadata)

.. code:: python

   result = execute_function(circuit, **kwargs)

**Example**: An optional execute function is included in the package
which uses `Sampler
Primitive <https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/qiskit_ibm_runtime.SamplerV2>`__:
``quantumaudio.utils.execute_with_sampler`` that can be passed to the
``decode()`` method. It requires the dependency
``pip install qiskit-ibm-runtime``.

📘 Additional Resources 
------------------------

Notebook Examples
~~~~~~~~~~~~~~~~~

For examples of circuit preparation, signal reconstruction, and
interactive demonstrations, please check the `Demo
Notebook <https://github.com/moth-quantum/quantum-audio/blob/main/demos/1_Basics_Walkthrough.ipynb>`__.
It combines the core package with additional functions from the
``demos/tools`` folder to go through Visual and Digital Audio examples.

Quick Export ⚡️
~~~~~~~~~~~~~~~

To quickly export quantumaudio from any audio file (e.g., *mp3*, *ogg*,
*flac*, *m4a*), a script ``export.py`` is provided in the
``demos/scripts`` folder. Navigate to the directory and run:
``bash   python export.py -i path/to/input/audio/file`` \```console
usage: export.py [-h] -i [-o] [-v] [–scheme] [–shots] [–sr] [–stereo]
[–buffer_size]

Process quantum audio and export as .wav file.

options: -h, –help show this help message and exit -i, –input Path to
the input audio file. -o, –output Path to the output audio file.
(default: saves in same directory with a prefix ``qa_``) -v, –verbose
Enable verbose mode. –scheme Quantum Audio Scheme (default: ``qpam`` for
mono audio, ``mqsm`` for stereo audio). –shots Number of shots for
measurement (default: 8000) –sr Sample rate of Digital audio (default:
22050) –stereo Enable stereo –buffer_size Length of each audio chunk
(default: 256) \``\`

   [!Note] Digital Audio `Dependencies <#installation>`__ must be
   installed to run this script.

🤝 Contributing 
----------------

Contributions to Quantum Audio are welcome! This package is designed to
be a versatile tool for both research and artistic exploration.

If you find any issues or have suggestions for improvements, please open
an issue or submit a pull request on the GitHub repository.

- **Code Contributions:** Add new features, fix bugs, or improve
  existing functionality and code.
- **Documentation:** Enhance the README, tutorials, or other project
  documentation.
- **Educational Use:** If you’re using this project for learning,
  teaching or research, we’d love to hear about your experiences and
  suggestions.
- **Feedback and Ideas:** Share your thoughts, feature requests, or
  suggest improvements by opening an issue.

For more information on contributing to Code and Documentation, please
review `Contributing
Guidelines <https://github.com/moth-quantum/quantum-audio/blob/main/docs/guides/CONTRIBUTING.md>`__

🚩 Future Releases 
-------------------

We’re excited to keep the package updated with features and
improvements! In future releases, we plan to introduce other schemes
from Quantum Audio Literature along with Base Scheme Class Categories to
support a generic structure for further contributions.

✅ Citing 
----------

If you use this code or find it useful in your research, please consider
citing: > Moth Quantum. (2024). Quantum Audio (v0.1.0). Zenodo.
https://doi.org/10.5281/zenodo.14012135 —

📜 Copyright
------------

Copyright 2024 Moth Quantum

Licensed under the `Apache License <LICENSE>`__, Version 2.0 (the
“License”); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the `License <LICENSE>`__ for the specific language governing
permissions and limitations under the License.

📧 Contact
----------

If you have any questions or need further assistance, please feel free
to contact Moth Quantum at hello@mothquantum.com

.. |Python version| image:: https://img.shields.io/badge/python-3.9+-important
.. |PyPI| image:: https://img.shields.io/pypi/v/quantumaudio
.. |Read the Docs (version)| image:: https://img.shields.io/readthedocs/quantumaudio/latest?label=API%20docs
.. |LICENSE| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://github.com/moth-quantum/quantum-audio/blob/main/LICENSE
.. |DOI| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.14012134.svg
   :target: https://doi.org/10.5281/zenodo.14012134
.. |Open in Colab| image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1qGWhTLWoxnJsR7tINR6MVGDvk56CX2uE?ts=66c70dcd
