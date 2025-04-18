## Migration Guidelines

### From Quantum Audio Version v0.0.2 to v0.1.0

### 1. Loading a scheme

**v0.0.2**
  ```python
  import quantumaudio
  qpam = quantumaudio.QuantumAudio('qpam') #returns a QuantumAudio Instance with QPAM scheme
  ```

**v0.1.0**
  ```python
  import quantumaudio
  qpam = quantumaudio.load_scheme('qpam') #returns a Scheme Instance

  #or quantumaudio.schemes.QPAM()
  #or quantumaudio.QPAM()
  ```

### 2. Encoding a Digital Audio Array into Quantum Circuit

**v0.0.2**
  ```python
  qpam.load_input(digital_audio) # here qpam gets updated
  qpam.prepare()
  qpam.measure()
  
  circuit = qpam.circuit
  ```

**v0.1.0**
  ```python
  circuit = qpam.encode(digital_audio) # qpam remains unchanged

  # or circuit = qpam.encode(digital_audio, measure=False) # Return circuit without measurement
  ```
For manually implementing each step of the ```encode()``` operation, please check [Documentation](https://quantumaudio.readthedocs.io/en/latest/contents/quantumaudio.schemes.html).

### 3. Decoding Digital Audio Array from a Quantum Circuit

**v0.0.2**
  ```python
  qpam.run(shots=4000)
  qpam.reconstruct_audio()

  digital_audio = qpam.output
  ```

**v0.1.0**
  ```python
  digital_audio = qpam.decode(circuit, shots=4000)
  ```
  The ```scheme.decode()``` function uses local _AerSimulator_ as default backend. It performs ```backend.run()``` method internally. Any backend object compatible with this method can be passed with ```backend=``` parameter. 
  
  For manually implementing each step of the ```decode()``` operation, please check [Documentation](https://quantumaudio.readthedocs.io/en/latest/contents/quantumaudio.schemes.html).
