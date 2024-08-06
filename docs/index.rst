Quantum Audio
-------------

quantumaudio is a python package for building Quantum Representations of
Digital Audio using qiskit circuits.

|PyPI| |Read the Docs (version)| |GitHub|

The audio encoded as quantum states can be processed and played back
through a quantum computer or a simulator. The objective is to enable
new ways of exploring audio signal processing for artistic and research
purposes.

This package provides the following schemes and necessary utilities.

-  schemes: Quantum Audio Encoding and Decoding Methods

   -  QPAM : Quantum Probability Amplitude Modulation
   -  SQPAM : Single-Qubit Probability Amplitude Modulation
   -  MSQPAM : Multi-channel Single-Qubit Probability Amplitude
      Modulation
   -  QSM : Quantum State Modulation
   -  MQSM : Multi-channel Quantum State Modulation

-  utils: Utilary functions for data processing, circuit preparation
   along with plotting and audio playback functions for Jupyter
   Notebook.

Usage Example
~~~~~~~~~~~~~

.. code:: python

   import quantumaudio
   from quantumaudio import schemes, utils

   # Example signal
   original_signal = utils.simulate_data(num_samples=8)
       
   # An instance of a scheme can be created either directly
   sqpam = quantumaudio.load_scheme('spqam')

   # or from schemes
   qpam = schemes.QPAM()

   # Encoding and Decoding
   encoded_circuit = qpam.encode(original_audio)
   # ... do some processing
   decoded_signal  = qpam.decode(encoded_circuit,shots=4000)    

   # Compare original vs reconstructed signal
   utils.plot([original_signal,decoded_signal])    

.. |PyPI| image:: https://img.shields.io/pypi/v/quantumaudio
.. |Read the Docs (version)| image:: https://img.shields.io/readthedocs/quantumaudio/latest?label=API%20docs
.. |GitHub| image:: https://img.shields.io/github/license/moth-quantum/quantum-audio

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules