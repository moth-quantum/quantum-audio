## Quantum Audio
<i>quantumaudio is a python package for building Quantum Representations of Digital Audio using qiskit circuits.</i> 

![PyPI](https://img.shields.io/pypi/v/quantumaudio) ![Read the Docs (version)](https://img.shields.io/readthedocs/quantumaudio/latest?label=API%20docs) ![GitHub](https://img.shields.io/github/license/moth-quantum/quantum-audio)
<!-- <img width="930" alt="MQSM" src="https://github.com/moth-quantum/quantum-audio/assets/161862817/d4fcb03d-1c48-4d4a-8f6f-6b8c285b58f1"> -->
<br>The audio encoded as quantum states can be processed and played back through a quantum computer or a simulator. The objective is to enable new ways of exploring audio signal processing for artistic and research purposes. 

This package provides the following schemes and necessary utilities.

- <b>schemes</b>: Quantum Audio Encoding and Decoding Methods

    - QPAM   : Quantum Probability Amplitude Modulation
    - SQPAM  : Single-Qubit Probability Amplitude Modulation
    - MSQPAM : Multi-channel Single-Qubit Probability Amplitude Modulation
    - QSM    : Quantum State Modulation
    - MQSM   : Multi-channel Quantum State Modulation

- <b>utils</b>: Utilary functions for data processing, circuit preparation along
         with plotting and audio playback functions for Jupyter Notebook.

### Usage Example
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

### Installation
To install Quantum Audio, you can use pip: ```pip install quantumaudio```

### Contributing
Contributions to Quantum Audio are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

### License
Quantum Audio is licensed under the Apache License 2.0.

### Acknowledgments
This project was inspired by the research work on quantum audio processing by [list of researchers or institutions]. We would like to thank them for their contributions to this field.

### Contact
If you have any questions or need further assistance, please feel free to reach out to us at [email address or contact information].
