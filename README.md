## Quantum Audio
<i>quantumaudio is a python package for building Quantum Representations of Digital Audio using qiskit circuits.</i> 

<img width="1289" alt="Screenshot 2024-07-04 at 01 01 13" src="https://github.com/moth-quantum/quantum-audio/assets/161862817/66c3641b-3a2e-40d8-9186-c1fe470020b1">


The audio encoded as quantum states can be processed and played back through a quantum computer or a simulator. The objective is to enable new ways of exploring audio signal processing for artistic and research purposes. 

This package provides the following schemes and necessary utilities.

- <b>schemes</b>: Quantum Audio Encoding and Decoding Methods

    - QPAM   : Quantum Probability Amplitude Modulation
    - SQPAM  : Single-Qubit Probability Amplitude Modulation
    - MSQPAM : Multi-channel Single-Qubit Probability Amplitude Modulation
    - QSM    : Quantum State Modulation
    - MQSM   : Multi-channel Quantum State Modulation

- <b>utils</b>: Utilary functions for data processing, circuit preparation along
         with plotting and audio playback functions for Jupyter Notebook.

### A Simple Example
```python
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
```
