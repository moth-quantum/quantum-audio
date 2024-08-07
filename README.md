# Quantum Audio
![PyPI](https://img.shields.io/pypi/v/quantumaudio) ![Read the Docs (version)](https://img.shields.io/readthedocs/quantumaudio/latest?label=API%20docs) ![GitHub](https://img.shields.io/github/license/moth-quantum/quantum-audio)

Quantum Audio is a Python package for building Quantum Representations of Digital Audio using Qiskit circuits.

The objective of Quantum Audio is to enable new ways of exploring audio signal processing for artistic and research purposes. 
The package provides fundamental features to encode audio as Quantum States that can be processed on a Quantum computer or simulator and played back.

The package contains different schemes to encode audio and necessary utilities as follows:

- ```schemes``` : Quantum Audio Representation Methods
  
| Acronym | Representation Name | Original Reference |
|---------|---------------------|--------------------|
| QPAM    | Quantum Probability Amplitude Modulation | Real-Ket          |
| SQPAM   | Single-Qubit Probability Amplitude Modulation | [FRQI](http://dx.doi.org/10.1007/s11128-010-0177-y)  |
| MSQPAM  | Multi-channel Single-Qubit Probability Amplitude Modulation | [PMQA](https://doi.org/10.1007/s11128-022-03435-7)  |
| QSM     | Quantum State Modulation | [FRQA](https://doi.org/10.1016/j.tcs.2017.12.025) |
| MQSM    | Multi-channel Quantum State Modulation | [QRMA](https://doi.org/10.1007/s11128-019-2317-3)  |

- ```utils``` : Utilary functions for data processing, analysis, circuit preparation, etc.

## Acknowledgment of Previous Version (v0.0.2)
This project is derived from research output on quantum representations of audio, carried by <b>Interdisciplinary Centre for Computer Music Research (ICCMR)</b>, University of Plymouth, UK, namely:
- Itaboraí, P.V., Miranda, E.R. (2022). Quantum Representations of Sound: From Mechanical Waves to Quantum Circuits. In: Miranda, E.R. (eds) Quantum Computer Music. Springer, Cham. https://doi.org/10.1007/978-3-031-13909-3_10
- Itaboraí, P. V. (2022). Quantumaudio Module (Version 0.0.2) [Computer software]. https://github.com/iccmr-quantum/quantumaudio
- Itaboraí, P. V. (2023) Towards Quantum Computing for Audio and Music Expression. Thesis. University of Plymouth. Available at: https://doi.org/10.24382/5119

## Key Changes in the Redeveloped Version (v0.1.0)
This project has been completely redeveloped and is now maintained by <b>Moth Quantum</b>. https://mothquantum.com
- **New Architecture:**
  - This project has been restructured for better flexibility and scalability.
  - Instead of _QuantumAudio_ Instances, the package operates in the level of _Scheme_ Instances that performs encoding and decoding functions independent of the data.
  - This enables an avenue of Tools that can be built upon the core functionality.
- **Feature Updates:**
  - Introducing 2 Additional Schemes that can encode and decode Multi-channel Audio.
  - Faster encoding and decoding of long audio files using Batch processing.
- **Dependency Changes:**
  - Support for _Qiskit_ is updated from **v0.22** to **v0.46**
- **Improvements:**
  - Key Information of Original Audio is preserved at Decoding, making the Encoding and Decoding operations independent.
  - Improved organisation of code for Readability and Modularity

### Usage Example
```python
# An instance of a scheme can be created using:
import quantumaudio
qpam = quantumaudio.load_scheme('qpam')

# or directly importing from schemes
# from quantumaudio import schemes
# qpam = schemes.QPAM() 

# Encoding and Decoding
encoded_circuit = qpam.encode(original_audio)
# ... do some processing
decoded_signal  = qpam.decode(encoded_circuit,shots=4000)    
```
```python
# Compare original vs reconstructed signal
import tools
tools.plot([original_signal,decoded_signal])    
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
