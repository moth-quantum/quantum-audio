.. Quantum Audio documentation master file, created by
   sphinx-quickstart on Thu Aug  8 10:59:59 2024.

Quantum Audio
=============

.. container::

   .. rubric:: Quantum Audio
      :name: quantum-audio

   |Python version| |PyPI| |Read the Docs (version)| |LICENSE| |DOI|
   |Open in Colab|

   An open-source Python package for building Quantum Representations of
   Digital Audio using *Qiskit* circuits.

💿 What is Quantum Audio ?
--------------------------

Audio plays a vital role in carrying information and music, traversing
through domains — from analog and digital formats to engaging our senses
in a profound way. With the advent of Quantum Computing, we formulate
ways of representing Audio Information in the Quantum Domain, enabling
new explorations in artistic and research contexts 💫

The Quantum Audio Package provides fundamental operations for
representing audio as Quantum States that can be processed on a Quantum
computer (or Simulator) and played back 🔊

🗒️ Table of Contents
--------------------

-  `Overview <#overview>`__
-  `Version Information <#version>`__
-  `Installation <#installation>`__
-  `Usage <#usage>`__
-  `Additional Resources <#materials>`__
-  `Contributing <#contributing>`__
-  `Future Releases <#future-releases>`__
-  `Citing <#citing>`__

🔍 Overview 
------------

Modulation Schemes are essential methods for encoding Audio in both
Analog (such as **FM** 📻) and Digital (such as **PCM** 💻) formats. The
same is extended for Quantum Audio. The package contains different
schemes to encode audio and necessary utilities as follows:

-  ``schemes`` : Quantum Audio Representation Methods

+-----------+-----------------------------+---------------------------+
| Acronym   | Representation Name         | Original Reference        |
+===========+=============================+===========================+
| **QPAM**  | Quantum Probability         | Real-Ket                  |
|           | Amplitude Modulation        |                           |
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

-  ``utils`` : Common Utilary functions for Data Processing, Analysis,
   Circuit Preparation, etc.

Additionaly, ``tools`` is provided in the repository which extends the
core functionality to support Audio and Visual Examples.

   For a quick tour of Quantum Audio, try
   `Colab <https://colab.research.google.com/drive/1qGWhTLWoxnJsR7tINR6MVGDvk56CX2uE?ts=66c70dcd>`__
   🚀

🧩 Version Information 
-----------------------

Pre-release original version: ``v0.0.2``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This project is derived from research output on Quantum Representations
of Audio, carried by Interdisciplinary Centre for Computer Music
Research (ICCMR), University of Plymouth, UK, namely:

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
~~~~~~~~~~~~~~~~~~~~~~~~~

This project has been completely redeveloped and is now maintained by
Moth Quantum. https://mothquantum.com

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

   -  Improved organisation of code for Readability and Modularity
   -  Key Information of Original Audio is preserved at Encoding, making
      the Encoding and Decoding operations independent.

-  **License Change:**

   -  The License is updated from **MIT** to **Apache 2.0**

Migration Guide
~~~~~~~~~~~~~~~

If you’re transitioning from the previous version, please check the
`Migration
Guide <https://github.com/moth-quantum/quantum-audio/blob/main/MIGRATION.md>`__
for an overview of the package usability.

🪄 Installation 
----------------

To install the Quantum Audio Package, you can use ``pip`` (included with
Python) which installs it from
`PyPI <https://pypi.org/project/quantumaudio/>`__ package manager. Run
the following command in Terminal or Command Prompt:

::

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
   `here <https://github.com/moth-quantum/quantum-audio/blob/main/ENVIRONMENT.md>`__.

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

**Digital Audio Dependencies**
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The core package operates with *numpy* arrays. Dependencies for audio
file handling to run audio examples in notebook and scripts in the
repository can be additionally installed using ``pip``:
``pip install quantumaudio[audio_io]`` For local installation from the
cloned directory: ``pip install .[audio_io]`` or manually with
``pip install -r requirements-audio.txt``\ 

   [!Tip] If using your own choice of libraries for digital audio
   processing, please be aware that Multi-channel Quantum Audio is
   processed with *Channels First* data structure. e.g. ``(2, N)`` for a
   Stereo Audio of ``N`` samples.

**Notebook Dependencies**
^^^^^^^^^^^^^^^^^^^^^^^^^

The `Demo
Notebook <https://github.com/moth-quantum/quantum-audio/blob/main/DEMO.ipynb>`__
features interactive elements that require additional dependencies. It
can be installed using ``pip``: ``pip install quantumaudio[notebook]``
For local installation from the cloned directory:
``pip install .[notebook]`` or manually with
``pip install -r requirements-notebook.txt``

🎨 Usage 
---------

Get started on creating Quantum Audio Representations with just a few
lines of code.

.. code:: python

   # An instance of a scheme can be created using:
   import quantumaudio
   qpam = quantumaudio.load_scheme('qpam') # or directly access from quantumaudio.schemes.QPAM()

   # Define an Input
   original_data = quantumaudio.utils.test_signal() # for a random array of samples (range: -1.0 to 1.0)

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

   [!Tip] The circuit depth can grow complex for a long array of samples
   which is the case with Digital Audio. It is optimal to represent a
   short length of samples per Circuit. The functions provided in
   ``tools/stream.py`` facilitate the processing of Long arrays in
   chunks. Examples of the usage can be found in the `Demo
   Notebook <https://github.com/moth-quantum/quantum-audio/blob/main/DEMO.ipynb>`__
   and ``scripts`` provided in the repository.

Running on Native Backends
~~~~~~~~~~~~~~~~~~~~~~~~~~

The default ``scheme.decode()`` uses local
`AerSimulator <https://github.com/Qiskit/qiskit-aer>`__ as the default
backend. Internally, the function performs ``backend.run()`` method (in
``quantumaudio.utils.execute``) and any compatible backend object can be
specified by passing the ``backend=`` parameter.

Running on External Quantum Backends
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
   -  In this case, the metadata dictionary can be accessed from the
      encoded circuit using ``circuit.metadata``

..

   [!Tip] **Dictionaries** are data type in python to store {key :
   value} pairs. - **Counts Dicitonary** contains keys representing
   classical measurement outcomes and values indicating the number of
   times the outcome was observed. Example:
   ``{'00': 77, '01': 79, '10': 84, '11': 72}``. - **Metadata
   Dictionary** stores the key information that is required at decoding,
   which is commonly the original data dimensions to restore.

   [!Note] When passing metadata manually in the above decode functions,
   QPAM Scheme additionaly requires ``shots`` information used at
   execution as metadata which can also be passed through the parameter
   ``shots=``.

📘 Additional Resources 
------------------------

Notebook Examples
~~~~~~~~~~~~~~~~~

For examples of circuit preparation, signals reconstruction, and
interactive demonstrations, please check the `Demo
Notebook <https://github.com/moth-quantum/quantum-audio/blob/main/DEMO.ipynb>`__.
It combines the core package with useful functions from the ``tools``
folder to go through Visual and Digital Audio examples.

Quick Export ⚡️
~~~~~~~~~~~~~~~

To quickly export quantumaudio from any audio file (e.g., mp3, ogg,
flac, m4a), a script ``export.py`` is provided in the ``scripts``
folder. Navigate with ``cd scripts`` and run:

.. code-block:: console

    python export.py -i path/to/input/audio/file

    usage: export.py [-h] -i [-o] [-v] [–scheme] [–shots] [–sr] [–stereo]
                      [–buffer_size]

    Process quantum audio and export as .wav file.

    options:
      -h, –help        show this help message and exit
      -i, –input       Path to the input audio file.
                       (default: saves in same directory with a prefix ``qa_``)
      -o, –output      Path to the output audio file.
      -v, –verbose     Enable verbose mode.
      –scheme          Quantum Audio Scheme (default: ``qpam`` for mono audio,
                       ``mqsm`` for stereo audio).
      –shots           Number of shots for measurement (default: 8000)
      –sr              Sample rate of Digital audio (default: 22050)
      –stereo          Enable stereo
      –buffer_size     Length of each audio chunk (default: 256)

[!Note] Digital Audio `Dependencies <#installation>`__ must be
installed to run this script and it currently uses *AerSimulator*.

🤝 Contributing 
----------------

Contributions to Quantum Audio are welcome! This package is designed to
be a versatile tool for both research and artistic exploration.

If you find any issues or have suggestions for improvements, please open
an issue or submit a pull request on the GitHub repository.

-  **Code Contributions:** Add new features, fix bugs, or improve
   existing functionality and code.
-  **Documentation:** Enhance the README, tutorials, or other project
   documentation.
-  **Educational Use:** If you’re using this project for learning,
   teaching or research, we’d love to hear about your experiences and
   suggestions.
-  **Feedback and Ideas:** Share your thoughts, feature requests, or
   suggest improvements by opening an issue.

For more information on contributing to Code and Documentation, please
review `Contributing
Guidelines <https://github.com/moth-quantum/quantum-audio/blob/main/CONTRIBUTING.md>`__

🚩 Future Releases 
-------------------

We’re excited to keep the package updated with features and improvements
as the community evolves! Quantum Audio Package ``v0.1.0`` is a upgrade
from ``v0.0.2`` with a focus on the core architectural changes. In
future releases, we plan to introduce other schemes from Quantum Audio
Literature along with Base Scheme Class Categories to support a generic
structure for further contributions.

✅ Citing 
----------

If you use this code or find it useful in your research, please consider
citing: `DOI <>`__

--------------

📜 Copyright
------------

Copyright 2024 Moth Quantum

Licensed under the Apache License, Version 2.0 (the “License”); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

📧 Contact
----------

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

Quantum Audio documentation
===========================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules