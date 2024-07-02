# Quantum Audio
Quantum Audio is a Python module for building quantum circuits that encode and decode audio signals as quantum states. This is primarily aimed for quantum computing simulators, but it might also run on real quantum hardware. The main objective is to have a readily available tools for using quantum representations of audio in artistic contexts and for studying future Quantum Signal Processing algorithms for audio.

This package contains class implementations for generating quantum circuits from audio signals, as well as necessary pre and post processing functions.

It contatins implementations for five representation algorithms cited on the publication above, namely:

- <b>QPAM</b> - Quantum Probability Amplitude Modulation (Simple quantum superposition or "Amplitude Encoding")
- <b>SQPAM</b> - Single-Qubit Probability Amplitude Modulation (similar to FRQI quantum image representations)
- <b>QSM</b> - Quantum State Modulation (also known as FRQA in the literature)
- <b>MSQPAM</b> - Multi-Channel Single-Qubit Probability Amplitude Modulation
- <b>MQSM</b> - Multi-Channel Quantum State Modulation

Example of Quantum Audio Representation:
<img width="1392" alt="SQPAM" src="https://github.com/moth-quantum/quantum-audio/assets/161862817/76445dc1-3fed-4e1b-acc7-7fce6b459dad">
