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
  qpam = quantumaudio.load_scheme('qpam') #returns a Scheme Class
  ```
  or
  
  ```python
  from quantumaudio import schemes
  qpam = schemes.QPAM()
  ```

### 2. Encoding a Digital Audio Array into Quantum Circuit

**v0.0.2**
  ```python
  qpam.load_input(digital_audio) # here qpam is updated
  qpam.prepare()
  qpam.measure()
  
  circuit = qpam.circuit
  ```

**v0.1.0**
  ```python
  circuit = qpam.encode(digital_audio) # qpam remains unchanged
  ```
  or
  ```python
  circuit = qpam.encode(digital_audio, measure=False) # Return circuit without measurement
  ```
For manually implementing each step of the ```encode()``` operation, please check [Documentation]()

### 3. Decoding Digital Audio Array from a Quantum Circuit

**v0.0.2**
  ```python
  qpam.run(shots=4000)
  qpam.reconstruct_audio()

  digital_audio = qpam.output
  ```

**v0.1.0**
  ```python
  digital_audio = qpam.decode(cirucit, shot=4000)
  ```
  Any backend compatible with qiskit.execute method can be passed with backend parameter. Defaults to AerSimulator.
