# Quantum Audio
quantumaudio is a python package for building Quantum Representations of Digital Audio using Qiskit Circuits. Here, Digital Audio is encoded as quantum states that can be processed and played back through a quantum computer or a simulator. This enables a new perspective of audio signal processing for artistic and research interests. 

This package provides the following schemes and necessary utilities.

- schemes: Quantum Audio Encoding and Decoding Methods

    - QPAM   : Quantum Probability Amplitude Modulation
    - SQPAM  : Single-Qubit Probability Amplitude Modulation
    - MSQPAM : Multi-channel Single-Qubit Probability Amplitude Modulation
    - QSM    : Quantum State Modulation
    - MQSM   : Multi-channel Quantum State Modulation

- utils: Utilary functions for data processing, circuit preparation along
         with plotting and audio playback functions for Jupyter Notebook.
