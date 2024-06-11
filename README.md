# Quantum Audio
Quantum Audio is a Python module for building quantum circuits that encode and decode audio signals as quantum states. This is primarily aimed for quantum computing simulators, but it might also run on real quantum hardware. The main objective is to have a readily available tools for using quantum representations of audio in artistic contexts and for studying future Quantum Signal Processing algorithms for audio.

This package contains class implementations for generating quantum circuits from audio signals, as well as necessary pre and post processing functions.

It contatins implementations for five representation algorithms cited on the publication above, namely:

QPAM - Quantum Probability Amplitude Modulation (Simple quantum superposition or "Amplitude Encoding")
SQPAM - Single-Qubit Probability Amplitude Modulation (similar to FRQI quantum image representations)
QSM - Quantum State Modulation (also known as FRQA in the literature)
MSQPAM - Multi-Channel Single-Qubit Probability Amplitude Modulation
MQSM - Multi-Channel Quantum State Modulation
